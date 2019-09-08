#!/usr/bin/env python3
import argparse
import threading
from socket import socket, AF_INET, SOCK_STREAM
import time

class EncryptedChat():

  socket = None
  friend = None
  messages = []

  def __init__(self, host, port):
    self.host = host
    self.port = port

    print("Initializing chat server on {}:{} ... ".format(host, port), end='')
    self.bind_and_listen()

  def bind_and_listen(self):
    self.socket = socket(AF_INET, SOCK_STREAM)
    try:
      self.socket.bind((self.host, self.port))
      self.socket.listen()
      print("OK")
    except:
      print("FAIL")
      raise Exception("Chat initialization failed.")

  def serve(self):
    if (self.socket == None): raise Exception("The socket must be bound.")

    handler_thread = threading.Thread(target=self.handle_conn)
    messager_thread = threading.Thread(target=self.send_message)
    handler_thread.start()
    messager_thread.start()

  def send_message(self):
    print(self.friend)
    while True:
      time.sleep(5)
      if self.friend != None and len(self.messages) > 0:
        print("Has to send")
        msg = self.messages.pop()
        print("sending {}".format(msg))
        with socket(AF_INET, SOCK_STREAM) as temp_sock:
          temp_sock.connect((self.friend[0], self.friend[1]))
          temp_sock.sendall(bytes(msg, 'utf-8'))
          while True:
              data = temp_sock.recv(1024)
              if not data:
                break
              print("received: {}".format(data.decode('utf-8')))

  def parse_input(self, content):
    if len(content) == 0: pass

    splited = content.split(" ")
    if splited[0].startswith("/"):
      if len(splited) > 1:
        return (splited[0], splited[1:], None)
      else:
        return (splited[0], [], None)
    else:
      return (None, None, content)


  def exec_input(self, origin, who, content):
    print("BBBBB")
    command, args, text = self.parse_input(content)

    print("log", origin, who, content)

    if (origin == "EXT"):
      ## Command from other chat
      if (command == "/connect"):
        if len(args) == 2:
          self.friend = (args[0], int(args[1]))
          print("Connected to {} at {}".format(args[0], args[1]))
          return "/info connection accepted"
        else:
          return "/info invalid params to attempt connection"
      else:
        ## Only prints and parse others types of commands for friend
        if self.friend != None and self.friend[0] == who:
          print("{} says: {}".format(who, text))
          return "/sys 0"
        else:
          return "/info you are not connected. Use /connect [host] [port]"
    else:
      ## Command from this chat
      if (command == "/connect"):
        if len(args) == 2:
          self.friend = (args[0], int(args[1]))
          self.messages.append("/connect {} {}".format(self.host, self.port))
      else:
        self.messages.append(text)

  def handle_conn(self):
    while True:
      conn, addr = self.socket.accept()
      with conn:
        while True:
          data = conn.recv(1024)
          if not data:
            break
          output = self.exec_input("EXT", addr[0], data.decode('utf-8').strip())
          conn.sendall(bytes(output, "utf-8"))

  def __del__(self):
    if (socket != None):
      self.socket.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Encrypted chat connector.")
  parser.add_argument("-os", "--offset", dest="offset", help="Binding port offset", default=0)
  parser.add_argument("-a", "--address", dest="host", help="Host IP address", default="127.0.0.1")
  parser.add_argument("-p", "--port", dest="port", help="Socket port", default=6532)

  args = parser.parse_args()
  
  if (int(args.offset) < 0): raise Exception("Port offset cannot be negative")

  port = args.port + int(args.offset)

  chat = EncryptedChat(args.host, port)
  chat.serve()

  while True:
    inp = input()
    chat.exec_input("INT", args.host, inp)