# Yamaha Recevier Serial Controller
#
# This module will handle simple communication with a Yamaha
# receiver using the serial port protocol. It's by no means
# complete and does not actually care about the commands sent,
# it simply tries its best to encode/decode the data.
#
# Some resources:
# http://en.wikipedia.org/wiki/Control_character (for STX, DC3, etc)
# http://download.yamaha.com/api/asset/file/?language=en&site=au.yamaha.com&asset_id=54852
#
import serial
import threading
import time
import queue
import logging
import codecs

class ProjectorController (threading.Thread):
  serialbuffer = bytes()
  serialpos = 0
  ready = False
  reports = {}
  config = None
  model = ""
  version = ""
  state = "unknown"
  powersave = False
  parsehint = False
  inwait = False

  def __init__(self, serialport, cbTerminate):
    """
    Initialize serial port but don't do anything else
    """
    threading.Thread.__init__(self)

    self.cbTerminate = cbTerminate
    self.serialport = serialport
    # Timeout of 0.2s is KEY! Because we must NEVER interrupt the receiver if it's saying something
    self.port = serial.Serial(serialport, baudrate=19200, timeout=0.200, rtscts=False, xonxoff=False, dsrdtr=False, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE)
    self.state = "unknown"
    self.port.flushInput()
    self.port.flushOutput()

  def init(self):
    """
    Kicks off the whole thing. Starts the thread and sends init command
    to the receiver
    """
    self.daemon = True

    logging.info("Projector-2-REST Gateway")
    logging.info("Intialized communication on " + self.serialport)
    self.idle = True
    self.flush()
    self.start()

  def sendOn(self):
    self.sendHex('2189015057310A')

  def sendOff(self):
    self.sendHex('2189015057300A')

  def sendHex(self, hexcode):
    str = codecs.decode(hexcode, 'hex_codec')
    self.port.write(str)

  def run(self):
    """
    Serial buffer management, continously read data from serial port
    and buffer locally for some more intelligent parsing
    """
    while True:
      #logging.debug("Pre-read")
      try:
        data = self.port.read(1024).decode('latin1')
      except:
        logging.error('Problems reading from serial, USB device disconnected?')
        self.cbTerminate()

  # Reads X bytes from buffer
  def read(self, bytes):
    remain = self.avail()
    if bytes > remain:
      raise ControllerException("Not enough bytes in buffer, wanted %d had %d" % (bytes, remain))

    result = self.serialbuffer[self.serialpos:self.serialpos+bytes]
    self.serialpos += bytes
    return result

  # Removes the read bytes from the buffer
  def flush(self):
    self.serialbuffer = self.serialbuffer[self.serialpos:]
    self.serialpos = 0

  # Returns bytes in buffer
  def avail(self):
    return len(self.serialbuffer) - self.serialpos

  # Resets the read pointer, useful when not all data is available
  def reset(self):
    self.serialpos = 0

class ControllerException(Exception):
  pass
