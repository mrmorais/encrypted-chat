# Rivest Cipher 4 (RC4) Implementation

"""
How it works? (a better explanation you can find on Wikipedia article https://en.wikipedia.org/wiki/RC4)

RC4 is a stream cipher algorithm, it's mainly based on 2 steps:

a) Generate a initial permuted state which is based on a provided key. The key must have
a length up to 256 bytes.

b) For each interation over a pseudo-random generator a value is return to be used for encrypt
1 byte by applying a bitwise exclusive (XOR) generating a ciphertext or plaintext. This process requires
variables i and j to be stored.
"""

class RC4:
    def __init__(self, key):
        """
        Set initial attributes and calculates the permutation state array.
        """

        self.i = 0
        self.j = 0
        self.key = key
        self.state = self.key_scheduling()

    def key_scheduling(self):
        """
        Initialize the permutation state in the identity permuted state array,
        it's based on key and key length.

        Reference: https://en.wikipedia.org/wiki/RC4
        """

        state = list(range(256)) # Initializing state vector [0..255]
        j = 0
        for i in range(256):
            j = (j + state[i] + ord(self.key[i % len(self.key)])) % 256
            state[i], state[j] = state[j], state[i]

        return state

    def reset(self, key):
        """
        Reset the algorithm state and recalculates the permutation state array based on a new key.
        """

        self.i = 0
        self.j = 0
        self.key = key
        self.state = self.key_scheduling()

    def gen_pseudo_random(self):
        """
        PRGA (Pseudo-random generation algorithm) implementation. It returns the
        next 8 bits sub-key.
        """

        self.i = (self.i + 1) % 256
        self.j = (self.j + self.state[self.i]) % 256
        self.state[self.i], self.state[self.j] = self.state[self.j], self.state[self.i]
        
        return self.state[(self.state[self.i] + self.state[self.j]) % 256]

    def apply(self, text, i_format='ascii', o_format='hex'):
        """
        Encrypt or Decrypt a plain/ciphered text.
        """

        parsed_text = ''
        if i_format == 'hex':
            for i in range(0, len(text), 2):
                parsed_text += chr(int(text[i:i+2], 16))
        elif i_format == 'ascii':
            parsed_text = text
        else:
            raise Exception("Invalid input format")

        converted_bytes = []
        for char in parsed_text:
            next_pseudo_rand = self.gen_pseudo_random()
            converted_bytes.append(ord(char) ^ next_pseudo_rand) # apply bitwise XOR
        
        # Next we're concatenating while formats the bytes to hex or ASCII char.
        if o_format == 'hex':
            # The {:02x} is a python format especification for 2 padding hex.
            # https://docs.python.org/3.4/library/functions.html#format
            return ''.join(["{:02x}".format(enc) for enc in converted_bytes])
        elif o_format == 'ascii':
            return ''.join([chr(enc) for enc in converted_bytes])
        else:
            raise Exception("Invalid output format")
    
    def encrypt(self, text):
        return self.apply(text, i_format='ascii', o_format='hex')

    def decrypt(self, text):
        return self.apply(text, i_format='hex', o_format='ascii')

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    key = sys.argv[2]
    text = str(sys.argv[3])
    cipher = RC4(key)
    if (mode == 'enc'):
        print(cipher.encrypt(text))
    elif (mode == 'dec'):
        print(cipher.decrypt(text))