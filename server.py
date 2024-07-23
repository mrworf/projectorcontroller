#!/usr/bin/env python3
#
# REST api for controlling a JVC DLA-RS1 projector
#
from controller import ProjectorController
from flask import Flask
from flask import jsonify
#from flask.ext.socketio import SocketIO
import time
import logging
import argparse
import sys

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

""" Parse it! """
parser = argparse.ArgumentParser(description="JVC-2-REST Gateway", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--logfile', metavar="FILE", help="Log to file instead of stdout")
parser.add_argument('--debug', action='store_true', default=False, help='Enable loads more logging')
parser.add_argument('--port', default=5003, type=int, help="Port to listen on")
parser.add_argument('--listen', metavar="ADDRESS", default="0.0.0.0", help="Address to listen on")
parser.add_argument('--tty', default="/dev/ttyUSB1", help="TTY for JVC DLA-RS1 projector")
config = parser.parse_args()

""" Setup logging """
if config.debug:
  logging.basicConfig(filename=config.logfile, level=logging.DEBUG, format='%(filename)s@%(lineno)d - %(levelname)s - %(message)s')
else:
  logging.basicConfig(filename=config.logfile, level=logging.INFO, format='%(filename)s@%(lineno)d - %(levelname)s - %(message)s')

""" Disable some logging by-default """
logging.getLogger("Flask-Cors").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)

def abortServer():
  IOLoop.instance().stop()

app = Flask(__name__)
controller = ProjectorController(config.tty, abortServer)

""" Sends operation commands to the receiver and optionally waits for the result
"""
@app.route("/command/<data>", methods = ["GET"])
def api_command(data):
  result = {
    'message': "Command sent"
  }

  if data == 'on':
    controller.sendOn()
  elif data == 'off':
    controller.sendOff()
  else:
    result.message = 'No such command'
  return jsonify(result)

if __name__ == "__main__":
  controller.init()
  app.debug = True
  #app.run(host=config.listen, port=config.port, use_debugger=False, use_reloader=False)
  #while True:
  #  time.sleep(5)
  http_server = HTTPServer(WSGIContainer(app))
  http_server.listen(config.port)
  IOLoop.instance().start()
  sys.exit(255)
