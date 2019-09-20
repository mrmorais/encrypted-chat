from socket import socket as create_socket, AF_INET, SOCK_STREAM

class ChatConnector():
    
    guest_socket = None
    host_socket = None
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def bind_and_listen(self):
        """
        Create and bind the desired port
        """
        
        host_socket = create_socket(AF_INET, SOCK_STREAM)
        try:
            host_socket.bind((self.host, self.port))
            host_socket.listen(10)
            self.host_socket = host_socket
            return host_socket
        except:
            raise Exception("Port binding and listening cannot be performed")
    
    def get_host_socket(self):
        """
        Return the host socket
        """
        return self.host_socket

    def get_guest_socket(self):
        """
        Return the guest socket
        """
        return self.guest_socket

    def set_guest_socket(self, guest_socket):
        """
        Define the guest socket
        """
        
        self.guest_socket = guest_socket
    
    def send_message(self, message_text):
        """
        Send a text message to a guest if connected
        """
        
        if self.guest_socket == None:
            raise Exception("[conn] Not connected to anyone")
        
        try:
            self.guest_socket.send(bytes(message_text, 'utf-8'))
        except Exception as exc:
            self.guest_socket.close()
            self.guest_socket = None
            raise Exception("[conn] Can't reach the guest because: " + str(exc))
    
    def connect_to(self, host, port):
        """
        Connect to a host
        """
        
        if self.guest_socket != None:
            raise Exception("[conn] You are already connected")
        
        guest_socket = create_socket(AF_INET, SOCK_STREAM)
        guest_socket.settimeout(2)
        
        try:
            guest_socket.connect((host, port))
            self.guest_socket = guest_socket
        except Exception as e:
            raise Exception("[conn] Unable to connect because: " + str(e))
    
    def close_host_connection(self):
        """
        Turn the server down
        """
        
        if self.host_socket != None:
            self.host_socket.close()
            self.host_socket = None
            
    def close_guest_connection(self):
        """
        Turn off current connection
        """
        
        if self.guest_socket != None:
            self.guest_socket.close()
            self.guest_socket = None
            
    def __del__(self):
        """
        Default destructor
        """

        self.close_guest_connection()
        self.close_host_connection()