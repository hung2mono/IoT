import usys
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const
import urequests
import time
import dht
import network as MOD_NETWORK
GLOB_WLAN=MOD_NETWORK.WLAN(MOD_NETWORK.STA_IF)
if GLOB_WLAN.isconnected() == True:
    GLOB_WLAN.active(False)
GLOB_WLAN.active(True)
GLOB_WLAN.connect("namewifi", "passwifi")
while not GLOB_WLAN.isconnected():
  pass
print(GLOB_WLAN.isconnected())
# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

if usys.platform == "pyboard":
    cfg = {"spi": 2, "miso": "Y7", "mosi": "Y8", "sck": "Y6", "csn": "Y5", "ce": "Y4"}
elif usys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 5}
elif usys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 33, "sck": 25, "csn": 26, "ce": 27}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

# Constants and variables:
HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = '99JI22NUXI9T6585' 
UPDATE_TIME_INTERVAL = 5000  # in ms 
last_update = time.ticks_ms()

d = dht.DHT11(machine.Pin(2))
d.measure()
def slave():
    temp2=str(d.temperature())
    humi2=str(d.humidity())
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    if cfg["spi"] == -1:
        spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
        nrf = NRF24L01(spi, csn, ce, payload_size=8)
    else:
        nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")

    while True:
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                temp, humi = struct.unpack("ii", buf)
                data={'field1':temp, 'field2':humi,'field3':temp2,'field4':hume2}
                request = urequests.post( 
                      'http://api.thingspeak.com/update?api_key=' +
                      THINGSPEAK_WRITE_API_KEY, 
                      json = data, 
                      headers = HTTP_HEADERS )  
                request.close() 
slave()

