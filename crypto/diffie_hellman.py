# Diffie-Hellman
import random

class DiffieHellman():
    def __init__(self, q, alpha):
        self.q = q
        self.alpha = alpha

    def calculate_pubkey(self):
        self.x = random.randrange(0, self.q)
        self.y = (self.alpha ** self.x) % self.q
        return self.y
    
    def calculate_sessionkey(self, foreign_key):
        self.k = (foreign_key ** self.x) % self.q
        return self.k

if __name__ == "__main__":
    dh_a = DiffieHellman(353, 3)
    dh_b = DiffieHellman(353, 3)
    
    yA = dh_a.calculate_pubkey()
    print("Ya = " + str(yA))

    yB = dh_b.calculate_pubkey()
    print("Yb = " + str(yB))

    kA = dh_a.calculate_sessionkey(yB)
    print("Ka = " + str(kA))

    kB = dh_b.calculate_sessionkey(yA)
    print("Kb = " + str(kB))