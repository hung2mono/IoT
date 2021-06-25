from time import sleep
from machine import Pin
from machine import I2C
from nrf24l01 import NRF24L01
from micropython import const
import gc
import dht
_RX_POLL_DELAY = const(15)
_SLAVE_SEND_DELAY = const(10)

if usys.platform == "pyboard":
    cfg = {"spi": 2, "miso": "Y7", "mosi": "Y8", "sck": "Y6", "csn": "Y5", "ce": "Y4"}
elif usys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 5}
elif usys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 33, "sck": 25, "csn": 26, "ce": 27}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
if cfg["spi"] == -1:
    spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
else:
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

nrf.open_tx_pipe(pipes[0])
nrf.open_rx_pipe(1, pipes[1])
nrf.start_listening()
##############################################################
d = dht.DHT11(machine.Pin(2))
d.measure()
def main():
    temp=str(d.temperature())
    humi=str(d.humidity())
    while True:
      
      try:
             nrf.send(struct.pack("ii", temp , humi))
      except OSError:
             pass
      time.sleep_ms(250)
while True:
    main()
