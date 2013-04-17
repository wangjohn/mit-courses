#!/usr/bin/python

def xfer(a, b, amt):
  if state[a] > amt:
    state[a] -= amt
    state[b] += amt
  return (state[a], state[b])

import collections, sys, socket, os
from time import gmtime, strftime
state = None

cmd, datafile = sys.argv
def setup():
  try:
    os.remove(datafile)
  except OSError:
    pass
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(('', 0))
  s.listen(2)
  print "\nListening on port " + str(s.getsockname()[1]) + " ..."
  return s

def readfile(fn):
  s = collections.defaultdict(lambda: 100)
  if not os.path.exists(fn):
    open(fn, 'w').close()
  with open(fn) as f:
    for l in f.readlines():
      f = l.split(' ')
      if f[0] != "#":
        s[f[0]] = int(f[1])
  return s

def writefile(fn, s, time):
  with open(fn, 'w') as f:
    f.write(time)
    for k in sorted(s):
      f.write('%s %d\n' % (k, s[k]))

s = setup()
while True:
  conn, addr = s.accept()
  msg = conn.recv(4096)
  a = None
  try:
    msg, time = msg.split(";")
    a, b, amts = msg.split(' ')
    amt = int(amts)
  except:
    pass
  if a is not None:
    state = readfile(datafile)
    ra, rb = xfer(a, b, amt)
    writefile(datafile, state, time)
    # print '%s %s %d -> %d %d' % (a, b, amt, ra, rb)
    conn.send("%d %d" % (ra, rb))
  conn.close()
