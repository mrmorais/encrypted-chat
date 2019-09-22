#!/usr/bin/env python3
import sys # for use of stdin, stdout
import argparse
from enum import Enum

from crypto.diffie_hellman import DiffieHellman
from crypto.sdes import SDes
from crypto.rc4 import RC4

from core import ChatCore, InputType, OutputType, NameReference

class CryptoAlg(Enum):
    NONE = 1
    SDES = 2
    RC4 = 3

class EncryptedChat():
    guest_name = "Guest"
    my_name = "You"
    
    enc_alg = CryptoAlg.NONE
    
    def __init__(self, host, port, q, alpha):
        self.prompt()
        
        self.diffie_hellman = DiffieHellman(q, alpha)
        
        self.core = ChatCore(host, port)
        self.core.set_message_handlers(self.input_handler, self.output_handler)
        self.core.set_chat_change_name_handler(self.change_name)
        self.core.set_input_text_stream(sys.stdin)
        self.core.initialize()
        self.core.run_chat_loop()
        
    def change_name(self, who, new_name):
        """
        Change self or guest name
        """
        if who == NameReference.ME:
            self.my_name = new_name
        elif who == NameReference.GUEST:
            self.guest_name = new_name
            
    def prompt(self):
        """
        Clear CLI to new command / message
        """
        
        sys.stdout.write("\r<{}> ".format(self.my_name))
        sys.stdout.flush()
        
    def decrypt_text(self, text):
        """
        Decrypt text if needed
        """

        if self.enc_alg == CryptoAlg.SDES:
            return self.sdes.decrypt(str(text))
        elif self.enc_alg == CryptoAlg.RC4:
            return self.rc4_dec.decrypt(str(text))
        else:
            return str(text)

    def output_handler(self, output_type, text_output):
        """
        CLI printer hook
        """
        
        if output_type == OutputType.LOG:
            sys.stdout.write('\r')
            
        if output_type == OutputType.GUEST:
            sys.stdout.write("\r<{}> ".format(self.guest_name))
        
        sys.stdout.write(text_output)
            
        sys.stdout.write('\n')
        
        self.prompt()
        
    def send_message(self, message):
        """
        Send a message, encrypting it if necessary
        """
        if self.enc_alg == CryptoAlg.SDES:
            self.core.send_message(self.sdes.encrypt(message))
        elif self.enc_alg == CryptoAlg.RC4:
            self.core.send_message(self.rc4_enc.encrypt(message))
        else:
            self.core.send_message(message)
        
    def init_enc_algorithm(self, algorithm, key):
        """
        Initialize a crypt algorithm
        """
        
        if algorithm == "sdes":
            self.enc_alg = CryptoAlg.SDES
            sdes_key = bin(key)[2:].zfill(10)[-10:] # converts to binary and get last 10 bits
            self.sdes = SDes(sdes_key)
        elif algorithm == "rc4":
            self.enc_alg = CryptoAlg.RC4
            self.rc4_enc = RC4(str(key))
            self.rc4_dec = RC4(str(key))
        else:
            self.enc_alg = CryptoAlg.NONE
        
    def parse_input(self, content):
        """
        Extract command and arguments from input text
        """

        if len(content) == 0: pass

        splited = content.split(" ")
        if splited[0].startswith("/"):
            if len(splited) > 1:
                return (splited[0], splited[1:], None)
            else:
                return (splited[0], [], None)
        else:
            return (None, None, content)

    def input_handler(self, input_type, input_text):
        """
        Handle internal and external inputs parsing and executing
        commands.
        """        
        
        if input_type == InputType.INTERNAL:
            # Command from this chat
            command, args, text = self.parse_input(input_text)
            
            # @@ Initialize a connection
            if command == "/connect":
                if len(args) == 2:
                    try:
                        self.core.connect_to(args[0], int(args[1]))
                        self.change_name(NameReference.GUEST, "{}:{}".format(args[0], args[1]))
                        self.output_handler(OutputType.LOG, "[~info] You're now connected to {}".format(self.guest_name))
                    except Exception as exc:
                        self.output_handler(OutputType.LOG, str(exc))
                else:
                    self.output_handler(OutputType.LOG, "[~info] Invalid params to attempt connection")
            # @@ Close the current connection
            elif command == "/bye":
                self.core.close_conn()
                self.prompt()
            # @@ Define a encrypted channel
            elif command == "/crypt":
                if len(args) == 1:
                    y = self.diffie_hellman.calculate_pubkey()
                    self.send_message("/dh_begin {} {}".format(args[0], str(y)))
                    self.output_handler(OutputType.LOG, "[~info] Initializing crypto channel with {} algorithm".format(args[0]))
                else:
                    self.output_handler(OutputType.LOG, "[~info] Invalid params to init a crypto channel")
                self.prompt()
            elif command == "/exit":
                self.output_handler(OutputType.LOG, "[~info] Good bye")
                self.core.close_all()
                sys.exit(0)
            
            # @@ Send a text message [default behaviour]
            else:
                try:
                    self.send_message(text)
                except Exception as exc:
                    self.output_handler(OutputType.LOG, str(exc))
                self.prompt()
            
        elif input_type == InputType.EXTERNAL:
            # Command from guest
            parsed_input = self.decrypt_text(input_text)
            command, args, text = self.parse_input(parsed_input)

            # @@ Guest wants to start a crypto channel
            if command == "/dh_begin":
                if len(args) == 2:
                    self.output_handler(OutputType.LOG, "[~info] Your guest initialized a crypto channel using {} algorithm".format(args[0]))
                    
                    y = self.diffie_hellman.calculate_pubkey()
                    k = self.diffie_hellman.calculate_sessionkey(int(args[1]))
                    
                    self.send_message("/dh_end {} {}".format(args[0], str(y)))
                    
                    self.init_enc_algorithm(args[0], k)
            # @@ Guest fineshed Diffie Hellman initialization
            elif command == "/dh_end":
                if len(args) == 2:
                    k = self.diffie_hellman.calculate_sessionkey(int(args[1]))
                    
                    self.init_enc_algorithm(args[0], k)
            # @@ Receive a guest message
            else:
                self.output_handler(OutputType.GUEST, text)
                self.prompt()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypted chat connector.")
    parser.add_argument("-os", "--offset", dest="offset", help="Binding port offset", default=0)
    parser.add_argument("-addr", "--address", dest="host", help="Host IP address", default="127.0.0.1")
    parser.add_argument("-p", "--port", dest="port", help="Socket port", default=6532)
    parser.add_argument("-q", dest="q", help="Diffie-Hellman q parameter", default=353)
    parser.add_argument("-a", "--alpha", dest="alpha", help="Diffie-Hellman alpha parameter", default=3)

    args = parser.parse_args()
  
    if (int(args.offset) < 0): raise Exception("Port offset cannot be negative")

    port = args.port + int(args.offset)

    chat = EncryptedChat(args.host, port, args.q, args.alpha)