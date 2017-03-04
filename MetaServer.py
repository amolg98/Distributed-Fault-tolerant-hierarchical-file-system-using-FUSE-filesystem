#!/usr/bin/env python
"""
Author: David Wolinsky
Version: 0.02

Description:
The XmlRpc API for this library is:
  get(base64 key)
    Returns the value and ttl associated with the given key using a dictionary
      or an empty dictionary if there is no matching key
    Example usage:
      rv = rpc.get(Binary("key"))
      print rv => {"value": Binary, "ttl": 1000}
      print rv["value"].data => "value"
  put(base64 key, base64 value, int ttl)
    Inserts the key / value pair into the hashtable, using the same key will
      over-write existing values
    Example usage:  rpc.put(Binary("key"), Binary("value"), 1000)
  print_content()
    Print the contents of the HT
  read_file(string filename)
    Store the contents of the Hahelperable into a file
  write_file(string filename)
    Load the contents of the file into the Hahelperable
"""

import sys, SimpleXMLRPCServer, getopt, pickle, time, threading, xmlrpclib, unittest
from datetime import datetime, timedelta
from xmlrpclib import Binary
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import sys, pickle, xmlrpclib
from sys import argv
from xmlrpclib import Binary
import socket
import errno
from socket import error
from errno import ECONNREFUSED
import socket, signal
from SimpleXMLRPCServer import *


# Presents a HT interface
class SimpleHT:
  def __init__(self):
    print "SimpleHT:main"	
    self.data = {}
    self.next_check = datetime.now() + timedelta(minutes = 5)

  def count(self):
    # Remove expired entries
    self.next_check = datetime.now() - timedelta(minutes = 5)
    self.check()
    return len(self.data)

  # Retrieve something from the HT
  def get(self, key):
    print "SimpleHT:get"	
    # Remove expired entries
    self.check()
    # Default return value
    rv = {}
    # If the key is in the data structure, return properly formated results
    key = key.data
    if key in self.data:
      ent = self.data[key]
      now = datetime.now()
      if ent[1] > now:
        ttl = (ent[1] - now).seconds
        rv = {"value": Binary(ent[0]), "ttl": ttl}
      else:
        del self.data[key]
    return rv

  # Insert something into the HT
  def put(self, key, value, ttl):
    # Remove expired entries
    print "SimpleHT:put"
    self.check()
    end = datetime.now() + timedelta(seconds = ttl)
    self.data[key.data] = (value.data, end)
    return True
    
  # Load contents from a file
  def read_file(self, filename):
    f = open(filename.data, "rb")
    self.data = pickle.load(f)
    f.close()
    return True

  # Write contents to a file
  def write_file(self, filename):
    f = open(filename.data, "wb")
    pickle.dump(self.data, f)
    f.close()
    return True

  # Print the contents of the hashtable
  def print_content(self):
    print self.data
    return True

  # Print the contents of the hashtable
  def list_contents(self):
    print self.data.keys()
    return self.data.keys()

  # Remove expired entries
  def check(self):
    print 'Check'
    now = datetime.now()
    if self.next_check > now:
      return
    self.next_check = datetime.now() + timedelta(minutes = 5)
    to_remove = []
    for key, value in self.data.items():
      if value[1] < now:
        to_remove.append(key)
    for key in to_remove:
      del self.data[key]

  #Ping test
  def ping(self):
   """Simple function to respond when called to demonstrate connectivity."""
   return True

  
  def corrupt(self,key):
    print key
    self.check()
    self.put(Binary(key), Binary(pickle.dumps('Corrupted in the server')), 6000)
    return 1

class AltXMLRPCServer(SimpleXMLRPCServer):

    finished=False

      
    def serve_forever(self):
	self.quit = 0
	while not self.quit:
	    self.handle_request()


    def terminate(self):
	    self.quit = 1
	    return 1

    '''def serve_forever(self):
        while not self.finished: self.handle_request()'''



def main(ports):
  print "server:main"
  optlist, args = getopt.getopt(sys.argv[1:], "", ["port=", "test"])
  ol={}
  data_ports=sys.argv[1:]

  for k,v in optlist:
    ol[k] = v

  #port = 51234
  if "--port" in ol:
    port = int(ol["--port"])  
  if "--test" in ol:
    sys.argv.remove("--test")
    unittest.main()
    return

  port=int(data_ports[0])
  serve(port)





# Start the xmlrpc server
def serve(port):
  port1 = int(port)
  print "port",port1
  '''file_server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', port))
  file_server.register_introspection_functions()
  file_server.register_function(sht.get)
  file_server.register_function(sht.put)
  file_server.register_function(sht.print_content)
  file_server.register_function(sht.read_file)
  file_server.register_function(sht.write_file)
  file_server.register_function(sht.print_keys)
  file_server.serve_forever()'''
  sht = SimpleHT()
  server = AltXMLRPCServer(('', port1))
  server.register_function(server.shutdown)
  server.register_introspection_functions()
  '''server.register_signal(signal.SIGHUP)
  server.register_signal(signal.SIGINT)'''
  server.register_function(server.terminate)
  server.register_function(sht.get)
  server.register_function(sht.put)
  server.register_function(sht.ping)
  server.register_function(sht.read_file)
  server.register_function(sht.write_file)
  server.register_function(sht.list_contents)
  server.register_function(sht.print_content)
  server.register_function(sht.corrupt)
  server.serve_forever()
  print "Closed"

# Execute the xmlrpc in a thread ... needed for testing
class serve_thread:
  def __call__(self, port):
    serve(port)

# Wrapper functions so the tests don't need to be concerned about Binary blobs
class Helper:
  def __init__(self, caller):
    self.caller = caller

  def put(self, key, val, ttl):
    return self.caller.put(Binary(key), Binary(val), ttl)

  def get(self, key):
    return self.caller.get(Binary(key))

  def write_file(self, filename):
    return self.caller.write_file(Binary(filename))

  def read_file(self, filename):
    return self.caller.read_file(Binary(filename))

if __name__ == "__main__":

	#ports = []
  	ports = argv[1]
  	main(ports)
