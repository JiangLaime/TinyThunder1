import os
import random
import struct
import sys
import gevent
from gevent.queue import *
from io import BytesIO
from gevent import Greenlet
from random import Random
nameList = open(os.path.dirname(os.path.abspath(__file__)) + '/../experiments/names.txt','r').read().strip().split('\n')




lock = Queue()
lock.put(1)

class test1:
  def __init__(self,name):
    self.name = name

  def __repr__(self):
    return '\033[94m' + "test finished" + "\033[0m"

def testNum(name) :
  global num
  lock.get()
  num+=1
  print(num)
def deepDecode(s, msgTypeCounter):
    mc = msgTypeCounter
    f = "from"
    t = "to"
    trSet = [1, 2, 3]
    rh = 4
    mb = "message body"
    sig = "signature"
    return mc, (f, t, ('B', ('i', (trSet, rh, mb), sig)),)




num = 0

if  __name__ =='__main__':
    global num
    print(num)




