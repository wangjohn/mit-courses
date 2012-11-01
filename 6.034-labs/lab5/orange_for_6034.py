import sys
sys.path += ["/Applications/Orange.app/Contents/Resources/orange", # Os X
             "C:\\Python25\\Lib\\site-packages\\orange", # Windows
             "C:\\Python26\\Lib\\site-packages\\orange", # Windows
             "/usr/lib/python2.5/dist-packages/orange", # Linux w/2.5
             "/usr/lib/python2.6/dist-packages/orange", # Linux w/2.6
             # Athena
             "/afs/athena.mit.edu/course/6/6.034/lib/python2.5/dist-packages/orange",
             ]

import os
if "LD_LIBRARY_PATH" not in os.environ:
    os.environ["LD_LIBRARY_PATH"] = ""
if "orange" not in os.environ["LD_LIBRARY_PATH"]:
    os.environ['LD_LIBRARY_PATH'] = ("/afs/athena.mit.edu/course/6/6.034/lib/"+
                                     "64bit/orange"+
                                     ":"+os.environ['LD_LIBRARY_PATH'])

#try:
import orange
import orngTree
import orngTest
import orngStat
import orngEnsemble
print "Orange version:",orange.version
#except ImportError:
#    raise "Did not find the Orange framework.  http://www.ailab.si/orange/"

from data_reader import *

def funcToMethod(func,clas,method_name=None):
    """Adds func to class so it is an accessible method; use method_name to specify the name to be used for calling the method.
    The new method is accessible to any instance immediately."""
    func.im_class=clas
    func.im_func=func
    func.im_self=None
    if not method_name: method_name=func.__name__
    clas.__dict__[method_name]=func

def cmstr(self):
    return ("<cm TruPos:%d FlsNeg:%d FlsPos:%d TruNeg:%d>" %
            (self.TP, self.FN, self.FP, self.TN))
funcToMethod(cmstr,orngStat.ConfusionMatrix,"__str__")

def bill_identifier(bill_data):
    text = bill_data['number']
    if not text:
        text = bill_data['name'].replace(r'\W','_')
    return str(bill_data['id']) +":"+ text

def write_congress_data(legislators, filename,
                        descriptions=None, unknown_column=-1):
    f = open(filename, "w")
    num_votes = len(legislators[0]['votes'])
    if descriptions:
        if len(descriptions) != len(legislators[0]['votes']):
            print ("%s: %d != %d" %
                   (filename, len(descriptions), len(legislators[0]['votes'])))
            print descriptions[0]
        print >>f, "party\t" + "\t".join([bill_identifier(v)
                                          for v in descriptions])
    else:
        print >>f, "party\t" + "\t".join(map(str,xrange(num_votes)))
    print >>f, "\t".join(["discrete" for i in xrange(num_votes+1)])
    print >>f, "\t".join(["" for i in xrange(-1, unknown_column)]),
    print >>f, "class\t",
    print >>f, "\t".join(["" for i in xrange(unknown_column+1, num_votes)])
    for legislator in legislators:
        print >>f, legislator['party'] + "\t" + "\t".join(map(str,legislator['votes']))


if __name__ == "__main__":
    for term in ["H004", "S109", "H109", "S110", "H110"]:
        write_congress_data(read_congress_data(term+".ord"), term+".tab",
                            descriptions=read_vote_data(term+"desc.csv"),
                            unknown_column=-1)
