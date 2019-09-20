from select import select as select_demux # use select as a strem demultiplexer
from enum import Enum
import sys

from connector import ChatConnector

class OutputType(Enum):
    LOG = 1
    GUEST = 2

class InputType(Enum):
    INTERNAL = 1
    EXTERNAL = 2
    
class NameReference(Enum):
    ME = 1
    GUEST = 2

class ChatCore():
    input_socket = None
    chat_input_handler = None
    chat_output_hanlder = None
    connections_list = []
    
    def __init__(self, host, port):
        """
        Initialize server by defining host and port and binding the connector
        """
          
        self.connector = ChatConnector(host, port)
        self.host = host
        self.port = port
        
    def initialize(self):
        self.chat_output_handler(OutputType.LOG, "[core] Initializing chat server on {}:{} ... ".format(self.host, self.port))
        try:
            self.host_socket = self.connector.bind_and_listen()
            self.chat_output_handler(OutputType.LOG, "[core] OK")
        except Exception as exc:
            self.chat_output_handler(OutputType.LOG, "[core] FAILED because: " + str(exc))
            sys.exit(1) # Exit with error 
            
        self.refresh_connections_list()
    
    def set_message_handlers(self, input_handler, output_handler):
        """
        Define input and output chat handlers
        """
        self.chat_input_handler = input_handler
        self.chat_output_handler = output_handler
    
    def set_input_text_stream(self, in_stream):
        """
        Define input socket stream
        """
        self.in_stream = in_stream
    
    def set_chat_change_name_handler(self, change_name_handler):
        """
        Define naming change handler
        """
        self.chat_change_name = change_name_handler
    
    def refresh_connections_list(self):
        """
        Mount a new connections list based on existing connections
        """
        
        conn_list = [self.in_stream]
        
        if self.connector.get_host_socket() != None:
            conn_list.append(self.connector.get_host_socket())
        
        if self.connector.get_guest_socket() != None:
            conn_list.append(self.connector.get_guest_socket())
        
        self.connections_list = conn_list
        
    def connect_to(self, host, port):
        """
        Connect to a guest
        """
        
        self.connector.connect_to(host, port)
        self.refresh_connections_list()
        
    def close_conn(self):
        """
        Close current guest connection
        """
        
        self.connector.close_guest_connection()
        self.refresh_connections_list()
        
    def send_message(self, text):
        """
        Send message to the guest
        """
        
        self.connector.send_message(text)
        
            
    def run_chat_loop(self):
        """
        Treats connections streams
        """
        
        while True:
            
            read_sockets, write_sockets, error_sockets = select_demux(self.connections_list, [], [])
            
            for sock in read_sockets:
                if sock == self.in_stream:
                    # Data received from keyboard
                    
                    user_input = self.in_stream.readline()
                    # Remove trailing \n and whitespace
                    user_input = user_input.strip('\n').strip(' ') 
                    
                    self.chat_input_handler(InputType.INTERNAL, user_input)
                    
                elif sock == self.host_socket:
                    # Binded server port for new connections
                    sock_conn, addr = sock.accept()
                    
                    # Verify if a new connection is allowed
                    if self.connector.get_guest_socket() != None:
                        sock_conn.send(bytes("[~info] The server you're trying to reach is busy", "utf-8"))
                        sock_conn.close()
                    else:
                        self.chat_change_name(NameReference.GUEST, "{}:{}".format(addr[0], addr[1]))
                        self.connector.set_guest_socket(sock_conn)
                        self.chat_output_handler(OutputType.LOG, "[~info] {} is now connected to you".format(addr[0]))
                        self.refresh_connections_list()
                else:
                    # Guest input message
                    try:
                        data = sock.recv(4096)
                        if data:
                            self.chat_input_handler(InputType.EXTERNAL, data.decode('utf-8'))
                    except Exception as exc:
                        self.chat_output_handler(OutputType.LOG, "[~info] your friend is now offline because: " + str(exc))
                        self.connector.close_guest_connection()
                        continue
                        
        self.connector.close_host_connection()