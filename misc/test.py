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


import ast

# 给定的字符串表示的列表


if  __name__ =='__main__':
    result_string = "{<Connection host=18.221.243.180>: <Result cmd='test -d charm' exited=1>}"

    # 将字符串转换为有效的Python对象
    result_list = ast.literal_eval(result_string)

    # 遍历列表，获取exited的值
    for connection, result in result_list.items():
        exited = result.exited
        print(exited)




