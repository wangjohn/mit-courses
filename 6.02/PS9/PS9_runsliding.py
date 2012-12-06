import subprocess
import re
if __name__ == '__main__' :
   for l in [0.0004, 0.0008, 0.0016, 0.0032, 0.0064, 0.0128, 0.0192, 0.0256, 0.0384, 0.0512, 0.06, 0.07, 0.08, 0.09, 0.1, 0.12, 0.13, 0.15, 0.16] :
       print l
       a=subprocess.Popen(['python', 'PS9_2.py' , '-w' ,'16' ,'-l',str(l),'-t','10000'],stdout=subprocess.PIPE)
       out,err=a.communicate()
       print out.split('\n')[1] # get throughput
