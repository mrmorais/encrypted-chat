# Rivest Cipher 4 - RC4

class RC4:
    i = 0
    j = 0

    def __init__(self, key):
        """
        """
        self.key = key
        self.state = self.key_scheduling_algorithm()

    def key_scheduling_algorithm(self):
        """
        Initialize the permutation in the state array
        based on key and key length
        """

        state = range(256) # Initializing state vector [0..255]
        j = 0
        for i in range(256):
            j = (j + state[i] + ord(self.key[i % len(self.key)])) % 256
            state[i], state[j] = state[j], state[i]

        return state

    def pseudo_random_generator(self):
        """
        """
        self.i = (self.i + 1) % 256
        self.j = (self.j + self.state[self.i]) % 256
        self.state[self.i], self.state[self.j] = self.state[self.j], self.state[self.i]
        
        return self.state[(self.state[self.i] + self.state[self.j]) % 256]

    def next():
        """
        """

    def encrypt(key):
        """
        """

a = RC4('abc')