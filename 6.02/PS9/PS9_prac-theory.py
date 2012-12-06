# This script processes throughput information printed by PSet 10, Task
# 2 (sliding window), obtained by running PS10_runsliding.sh (included
# in this directory), and plots a graph showing the empirically
# observed throughput as a function of the loss rate experienced by
# data and ACK packets on the path.  It also plots the maximum
# possible throughput that the implemented sliding window protocol can
# achieve.  It hard codes the number "12", as there are 12 hops
# back-and-forth in the default topology, and uses the effective
# packet-ACK success rate of the path to be equal to
# (1-link_loss_rate)**hops, where hops (=12 below) is the number of
# hops.  If you run it on a different topology, change "hops" to be
# whatever the number of hops on the data + ACK paths is.
#
# The Chapter 20 lecture notes explain why the optimal throughput for
# the sliding window protocol described in 6.02 cannot exceed the
# probability that any given data packet successfully gets an ACK in
# return.

import sys
import math
import matplotlib.pyplot as p

f = open(sys.argv[1], 'r')
lines = f.readlines()
xdat = []
ydat = []
y_theory = []
logx = []
logy = []
hops = 12
for line in lines:
    t = line.split()
    if len(t) == 1:   # per-link loss-rate
        x = float(t[0])
        xdat.append(x)
        logx.append(math.log(1-x))
        y_theory.append((1-x)**hops)
    else:             # output from PS10_2
        y = float(t[3])
        ydat.append(y)
        logy.append(math.log(y))

p.xlabel('Per-link loss probability')
p.ylabel('Throughput (pkts/time slot)')
p.plot(xdat, ydat,label="experiment")
p.plot(xdat, y_theory,label="theory")
p.legend()
p.show()

