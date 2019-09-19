#!/usr/bin/env python3
import argparse
import select
import sys
from socket import socket, AF_INET, SOCK_STREAM
import time
from crypto.diffie_hellman import DiffieHellman
from crypto.sdes import SDes
from crypto.rc4 import RC4

class EncryptedChat():

  CONNECTION_LIST = [sys.stdin]
  guest_name = "guest"
  my_name = "you"
  enc_mode = "none"

  def __init__(self, host, port, q, alpha):
    """
    Initialize server by defining host and port and binding the connector
    """

    self.host = host
    self.port = port

    self.diffie_hellman = DiffieHellman(q, alpha)

    sys.stdout.write("Initializing chat server on {}:{} ... ".format(host, port))
    self.bind_and_listen()
    self.prompt()
  
  def prompt(self):
    """
    Clear CLI to new command
    """

    sys.stdout.write("\r<{}> ".format(self.my_name))
    sys.stdout.flush()

  def bind_and_listen(self):
    """
    Create and bind the desired port
    """

    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
      server_socket.bind((self.host, self.port))
      server_socket.listen(10)
      self.CONNECTION_LIST.append(server_socket)
      sys.stdout.write("OK\n")
    except:
      sys.stdout.write("FAIL\n")
      raise Exception("Chat initialization failed.")

  def get_guest_sock(self):
    """
    Return the guest socket
    """
    if len(self.CONNECTION_LIST) > 2:
      return self.CONNECTION_LIST[2]
    else:
      return None

  def send_message(self, message):
    """
    Send a text message to a pair if connected
    """

    guest_sock = self.get_guest_sock()

    if not guest_sock:
      sys.stdout.write("/info you're not connected to anyone. Use /connect host port\n")
    else:
      try:
        guest_sock.send(message)
      except:
        guest_sock.close()
        sys.stdout.write("/error cannot reach your guest\n")
        self.CONNECTION_LIST.remove(guest_sock)

  def connect_to(self, host, port):
    """
    Connect to a new host
    """

    if not self.get_guest_sock():
      guest_sock = socket(AF_INET, SOCK_STREAM)
      guest_sock.settimeout(2)

      try:
        guest_sock.connect((host, port))
        self.CONNECTION_LIST.append(guest_sock)
        self.guest_name = "{}:{}".format(host, port)
      except:
        sys.stdout.write("/error unable to connect\n")
    else:
      sys.stdout.write("/error you are already connected. Use /bye to exit.\n")
  
  def change_name(self, new_name):
    """
    Change user nickname
    """

    self.my_name = new_name

    guest_sock = self.get_guest_sock()

    if guest_sock:
      guest_sock.send("/set_guest_name {}".format(new_name))
  
  def close_connection(self):
    """
    Turn off the chat
    """

    guest_sock = self.get_guest_sock()

    if guest_sock:
      guest_sock.close()
      self.CONNECTION_LIST.remove(guest_sock)
      
  def parse_input(self, content):
    """
    Extract command and arguments from input text
    """

    if len(content) == 0: pass

    splited = content[:-1].split(" ")
    if splited[0].startswith("/"):
      if len(splited) > 1:
        return (splited[0], splited[1:], None)
      else:
        return (splited[0], [], None)
    else:
      return (None, None, content)
  
  def init_enc_algorithm(algorithm, key):
    """
    """

    if algorithm == "sdes":
      self.enc_mode = "sdes"
      sdes_key = bin(key)[2:].zfill(10)[-10:] # converts to binary and get last 10 bits
      self.sdes = SDes(sdes_key)
    elif algorithm == "rc4":
      self.enc_mode = "rc4"
      self.rc4_enc = RC4(str(key))
      self.rc4_dec = RC4(str(key))
    else:
      self.enc_mode = "none"

  def exec_input(self, origin, content):
    """
    Handle internal and external inputs parsing and executing
    commands.
    """

    command, args, text = self.parse_input(content)

    if (origin == "EXT"):
      # command from other chat
      if self.get_guest_sock():
        if (command == "/set_guest_name"):
          if len(args) == 1:
            self.guest_name = args[0]
        elif (command == "/crypt"):
          if len(args) == 2:
            y = self.diffie_hellman.calculate_pubkey()
            k = self.diffie_hellman.calculate_sessionkey(int(args[1]))
            
            self.init_enc_algorithm(args[0], k)
            
            self.send_message("/crypt_ {}".format(str(y)))
        elif (command == "/crypt_"):
          if len(args) == 1:
            k = self.diffie_hellman.calculate_sessionkey(int(args[1]))

            self.init_enc_algorithm(self.enc_mode, k)
        else: # It is a message -- just print the input
          sys.stdout.write("\r") # clear prompt
          sys.stdout.write("<{}> {}".format(self.guest_name, content))
    else:
      # command from this chat
      if (command == "/connect"): # connect to host
        if len(args) == 2:
          self.connect_to(args[0], int(args[1]))
        else:
          sys.stdout.write("/info invalid params to attempt connection\n")
      elif (command == "/set_name"): # changes user nickname
        if len(args) == 1:
          self.change_name(args[0][:-1])
      elif (command == "/bye"): # close connection
        self.close_connection()
      elif (command == "/crypt"):
        if len(args) == 1:
          y = self.diffie_hellman.calculate_pubkey()
          self.enc_mode = args[0]
          self.send_message("/crypt {} {}".format(args[0], str(y)))
        else:
          sys.stdout.write("/info invalid params to init crypto\n")
      else:
        if (text):
          self.send_message(text)
        else:
          sys.stdout.write("/error invalid command\n")

  def serve(self):
    """
    Starts serving the chat
    """

    while True:

      read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])

      for sock in read_sockets:
        if sock == self.CONNECTION_LIST[0]: # User text input
          # Data received from keyboard
          user_input = sys.stdin.readline()
          self.exec_input("INT", user_input)

          self.prompt()
        elif sock == self.CONNECTION_LIST[1]: # Binded port for new connections
          sock_conn, addr = sock.accept()

          # Verify if a new connection is allowed
          if len(self.CONNECTION_LIST) == 3:
            sock_conn.send("/info the chat line you're trying to reach is busy\n")
            sock_conn.close()
          else:
            self.CONNECTION_LIST.append(sock_conn)
            self.guest_name = "{}:{}".format(addr[0], addr[1])
            sock_conn.send(bytes("/info connection established\n", 'utf-8'))
            sys.stdout.write("{} is now connected to you\n".format(addr))

            self.prompt()
        else: # Friend input message from socket
          try:
            data = sock.recv(4096)
            if data:
              self.exec_input("EXT", data)
              self.prompt()
          except:
            sys.stdout.write("/info your friend is now offline\n")
            sock.close()
            self.CONNECTION_LIST.remove(sock)
            continue

    self.CONNECTION_LIST[1].close()

  def __del__(self):
    """
    Default destructor
    """
    if (len(self.CONNECTION_LIST) > 1):
      self.CONNECTION_LIST[1].close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Encrypted chat connector.")
  parser.add_argument("-os", "--offset", dest="offset", help="Binding port offset", default=0)
  parser.add_argument("-addr", "--address", dest="host", help="Host IP address", default="127.0.0.1")
  parser.add_argument("-p", "--port", dest="port", help="Socket port", default=6532)
  parser.add_argument("-q", dest="q", help="Diffie-Hellman q", default=353)
  parser.add_argument("-a", "--alpha", dest="alpha", help="Diffie-Hellman alpha", default=3)

  args = parser.parse_args()
  
  if (int(args.offset) < 0): raise Exception("Port offset cannot be negative")

  port = args.port + int(args.offset)

  chat = EncryptedChat(args.host, port, args.q, args.alpha)
  chat.serve()
