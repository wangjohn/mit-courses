#!/usr/bin/python
import random, time

def client(servers):
  a = random.randint(0, 9)
  b = random.randint(0, 9)
  amt = random.randint(0, 10)
  results = []
  for s in servers:
    results.append(s.xfer(a, b, amt))   
  # make a set out of results, and see if it has one item:
  if len(set(results)) != 1: 
    print 'bug: xfer(%s,%s,%d) =' % (a,b,amt), results

import socket, sys, signal
class srv(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port

  def xfer(self, a, b, amt):
    time.sleep(random.random() * 0.05) # Add some network delay
    fd = socket.create_connection((self.host, self.port))
    fd.send("%s %s %d" % (str(a), str(b), amt))
    resp = fd.recv(4096)
    ra, rb = resp.split(' ')
    fd.close()
    return (int(ra), int(rb))

ports = sys.argv[1:]
servers = []
for p in ports:
  servers.append(srv('localhost', p))

keep_running = True
def sigint(a, b):
  global keep_running
  keep_running = False

signal.signal(signal.SIGINT, sigint)
signal.siginterrupt(signal.SIGINT, False)

while keep_running:
  client(servers)
