#!/usr/bin/env python
# encoding: utf-8

import socket
import bencoder
from random import randint
import hashlib
from threading import Thread
import logging
import os
class DHT(Thread):
  def __init__(self,ip,port):
    Thread.__init__(self)
    self.nodeID = self.randomNodeID()
    self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  #UDP
    self.socket.bind((ip,port))
    logging.basicConfig(level=logging.DEBUG)
    logging.info("server start in %s:%d",ip,port)
    
    self.BOOTSTRAP_NODES = (
      ("router.bittorrent.com", 6881),
      ("dht.transmissionbt.com", 6881),
      ("router.utorrent.com", 6881)
      )
  
  def randomNodeID(self,size=20):
    length = 10
    """
    TODO figure it out.
    Mainline dht里边的key长度为160bit，注意是bit，不是byte。
    在常见的编译型编程语言中，最长的整型也才是64bit，所以用整型是表示不了key的
    Node IDs are chosen at random from the same 160-bit space as BitTorrent infohashes
    
    Use SHA1 and plenty of entropy to ensure a unique ID.
    """
    # randomStr = ""
    # for item in range(length):
    #   randomStr+=chr(randint(0,255))
    #   sha1 = hashlib.sha1()
    #   sha1.update(randomStr.encode('utf-8'))
    # return sha1.hexdigest()
    return os.urandom(size)

    
  def sendKRPC(self,msg,address):
    #data = bytes(bencoder.bencode(msg),'utf-8')
    data = bencoder.bencode(msg)
    logging.debug(data)
    self.socket.sendto(data,address)
  def ping(self,address):
    """
    PING
    arguments:  {"id" : "<querying nodes id>"}

    response: {"id" : "<queried nodes id>"}

    ping Query = 
    bencoded = d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe

    Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
    bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
    """
    msg={"t":"aa",
         "y":"q",
         "q":"ping",
         "a":{
           "id":self.nodeID
           }
        }
    self.sendKRPC(msg,address)
  
  def findNode(self,address,targetID):
    """
    arguments:  {"id" : "<querying nodes id>", "target" : "<id of target node>"}

    response: {"id" : "<queried nodes id>", "nodes" : "<compact node info>"}
    """
    msg = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":self.nodeID, "target":targetID}}
    self.sendKRPC(msg,address)
  
  def getPeer(self,address,infoHash):
    """
    arguments:  {"id" : "<querying nodes id>", "info_hash" : "<20-byte infohash of target torrent>"}

  response: {"id" : "<queried nodes id>", "token" :"<opaque write token>", "values" : ["<peer 1 info string>", "<peer 2 info string>"]}

  or: {"id" : "<queried nodes id>", "token" :"<opaque write token>", "nodes" : "<compact node info>"}
    """
    msg = {"t":"aa",
           "y":"q", 
           "q":"get_peers", 
           "a": {
             "id":self.nodeID,
              "info_hash":infoHash
    }}
    self.sendKRPC(msg,address)

  def announcePeer(self,address,info_hash,port,token):
    """
    arguments:  {"id" : "<querying nodes id>",
    "implied_port": <0 or 1>,
    "info_hash" : "<20-byte infohash of target torrent>",
    "port" : <port number>,
    "token" : "<opaque token>"}

    response: {"id" : "<queried nodes id>"}

     announce_peer has four arguments: 
     "id" containing the node ID of the querying node,
     "info_hash" containing the infohash of the torrent, 
     "port" containing the port as an integer
     "token" received in response to a previous get_peers query. 
     The queried node must verify that the token was previously sent to the same IP address as the 
     querying node. 
      Then the queried node should store the IP address of the querying node and the supplied port 
       number under the infohash in its store of peer contact information.

    There is an optional argument called implied_port which value is either 0 or 1. If it is
     present and non-zero, the port argument should be ignored and the source port of the UDP 
     packet should be used as the peer's port instead. This is useful for peers behind a NAT 
     that may not know their external port, and supporting uTP, they accept incoming connections
     on the same port as the DHT port.    
    """
    msg = {"t":"aa",
           "y":"q",
           "q":"announce_peer",
           "a": {"id":self.nodeID, "info_hash":info_hash, "port": port, "token": token}}
    self.sendKRPC(msg,address)
  def join_DHT(self):
      for address in self.BOOTSTRAP_NODES:
          self.findNode(address,self.nodeID)
  def run(self):
    while True:
      (data, address) = self.socket.recvfrom(65536)
      logging.debug("received reply from %s",address)
      msg = bencode.decode(data)
      self.onMessage(msg,address)
  def onMessage(self,msg,address):
    print(msg)
  

  
if __name__ == "__main__":
  dht = DHT(ip='0.0.0.0',port=6882)
  dht.start()
  #print(dht.randomNodeID())
  dht.join_DHT()
  
