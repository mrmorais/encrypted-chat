from ..rc4 import RC4 # Our implementation

import unittest

class TestCryptoRC4(unittest.TestCase):
    key = "mtwllnlngebalvble"

    def test_encrypt_against_alt_source(self):
        plain = "some plain text"

        alt_src_response = "dacb65e44646be6605af69e3b4bcea"
        # This alt RC4 encryption was extracted from a RC4 Online Tool:
        # http://rc4.online-domain-tools.com/

        rc4 = RC4(self.key)
        cipher_rc4 = rc4.apply(plain)

        self.assertEqual(alt_src_response, cipher_rc4)
    
    def test_flow_capability(self):
        plain1 = "some plain text"
        plain2 = "continuation of the text"

        alt1 = "dacb65e44646be6605af69e3b4bcea"
        alt2 = "ee44b312d3c5e258af1eb9ebcadefd692fb662feab0a45f8"

        rc4 = RC4(self.key)
        cipher1 = rc4.apply(plain1)
        cipher2 = rc4.apply(plain2)

        self.assertEqual(alt1, cipher1)
        self.assertEqual(alt2, cipher2)

    def test_decrypt_against_alt_source(self):
        encrypted = "ddcc61f24641bb6b00e120f9b2a8ebe94efd01dbc6f24afb15a3ec86c5"

        alt_src_response = "this will include games built"

        rc4 = RC4(self.key)
        decrypted = rc4.apply(encrypted, i_format='hex', o_format='ascii')

        self.assertEqual(decrypted, alt_src_response)

    def test_ping_pong(self):

        alice_e = RC4(self.key)
        alice_d = RC4(self.key)
        
        bob_e = RC4(self.key)
        bob_d = RC4(self.key)

        ## Alice says "ping"
        ping_encd = alice_e.apply("ping")
        ping_decd = bob_d.apply(ping_encd, i_format='hex', o_format='ascii')

        self.assertEqual(ping_decd, "ping")

        ## Bob says "pong"
        pong_encd = bob_e.apply("pong")
        pong_decd = alice_d.apply(pong_encd, i_format='hex', o_format='ascii')

        self.assertEqual(pong_decd, "pong")

        ## Alice says "requirement"
        req_encd = alice_e.apply("requirement")
        req_decd = bob_d.apply(req_encd, i_format='hex', o_format='ascii')

        self.assertEqual(req_decd, "requirement")

if __name__ == '__main__':
    unittest.main()