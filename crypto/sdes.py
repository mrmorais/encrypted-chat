import sys
import numpy as np

class Des:
    def __init__(self):
        self.p10 = [3,5,2,7,4,10,1,9,8,6]
        self.p8 = [6,3,7,4,8,5,10,9]
        self.p4 = [2, 4, 3, 1]
        self.ip = [2, 6, 3, 1, 4, 8, 5, 7]
        self.ip_1 = [4, 1, 3, 5, 7, 2, 8, 6]
        self.ep = [4, 1, 2, 3, 2, 3, 4, 1]
        self.s_0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
        self.s_1 = [[1, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]
        self.key = '1010000010'

    def permutation(self, chain, permut):
        p = []
        newChain = ''
        if permut == 'p10': 
            p = self.p10; 
        elif permut == 'p8': 
            p = self.p8
        elif permut == 'p4':
            p = self.p4
        elif permut == 'ip':
            p = self.ip
        elif permut == 'ip_1':
            p = self.ip_1
        elif permut == 'ep':
            p = self.ep
        for i in p:
            newChain = newChain + chain[i-1]
        return newChain
    
    def shiftLeft(self, chain, x):
        newChain = chain
        for i in range(x):
            newChain = newChain[1:] + newChain[:1]
        return newChain

    def keyGenerate(self):
        mainChain = self.permutation(self.key, 'p10') 
        chainL = mainChain[:5]
        chainR = mainChain[5:]
        chainL = self.shiftLeft(chainL, 1)
        chainR = self.shiftLeft(chainR, 1)
        mainChain = chainL + chainR
        k1 = self.permutation(mainChain, 'p8')

        newChainL = self.shiftLeft(chainL, 2)
        newChainR = self.shiftLeft(chainR, 2)
        newMainChain = newChainL + newChainR
        k2 = self.permutation(newMainChain, 'p8')
        keys = (k1, k2)
        return keys
    
    def getBinarySet(self, num):
        binaryNumber = bin(num)
        setBits = binaryNumber[2:]
        return setBits

    def getBinaryText(self, plainText):
        textBinarySet = []
        for t in plainText:
            textBinarySet.append(self.getBinarySet(ord(t)).zfill(8))
        return textBinarySet

    def xor(self, chain1, chain2):
        result =''
        for i in range(len(chain1)):
            if((chain1[i] == '1' and chain2[i] == '1') or (chain1[i] == '0' and chain2[i] == '0')):
                result = result + '0'
            else:
                result = result + '1'
        return result
    
    def sBox(self, chain, whatS):
        s = None
        if whatS == 's0':
            s = self.s_0
        elif whatS == 's1':
            s = self.s_1
        chain_s = chain[:4]
        row = int((chain_s[0] + chain_s[3]), 2)
        column = int((chain_s[1] + chain_s[2]), 2)
        chainBinary_s = bin(s[row][column])[2:]
        if chainBinary_s == '1':
            chainBinary_s = '01'
        elif chainBinary_s == '0':
            chainBinary_s = '00'
        return chainBinary_s


    def fkFunction(self, bytePlainText, k1, k2):      
        #IP
        bytePlainText = self.permutation(bytePlainText, 'ip')
        textL1 = bytePlainText[:4] #fazer o xor no final
        textR1 = bytePlainText[4:] #sera usado no começo e na outra volta
        #E/P
        epChain1 = self.permutation(textR1, 'ep')
        #XOR
        resultXor1 = self.xor(epChain1, k1)
        #S0
        chainBinary_s0_1 = self.sBox(resultXor1[:4], 's0')
        #S1
        chainBinary_s1_1 = self.sBox(resultXor1[4:], 's1')
        #P4
        chain_p4_1 = chainBinary_s0_1 + chainBinary_s1_1
        chain_p4_1 = self.permutation(chain_p4_1, "p4")
        #XOR
        resultXor2 = self.xor(chain_p4_1, textL1)
        
        #SW
        textL2 = textR1 #Fará o xor no final
        textR2 = resultXor2
        #E/P
        epChain2 = self.permutation(textR2, 'ep')
        #XOR
        resultXor3 = self.xor(epChain2, k2)
        #S0_2
        chainBinary_s0_2 = self.sBox(resultXor3[:4], 's0')
        #S1
        chainBinary_s1_2 = self.sBox(resultXor3[4:], 's1')
        #P4
        chain_p4_2 = chainBinary_s0_2 + chainBinary_s1_2
        chain_p4_2 = self.permutation(chain_p4_2, 'p4')
        #XOR
        resultXor4 = self.xor(chain_p4_2, textL2)
        cipherText = resultXor4 + textR2
        #IP-1
        cipherText = self.permutation(cipherText,'ip_1')
        return cipherText


    def binaryToHexa(self, listByteText):
        return ''.join(["{:02x}".format(int(bt, 2)) for bt in listByteText])
    
    def hexaToBinary(self, hexaText):
        textBytes = []
        for i in range(0, len(hexaText), 2):
            textBytes.append(bin(int(hexaText[i:i+2], 16))[2:].zfill(8))
        return textBytes

    def binaryToText(self, binaryText):
        text = ''
        for bt in binaryText:
            text += chr(int(bt,2))
        return text

    def decrypt(self, cipherText):
        keys = self.keyGenerate()
        k1 = keys[0]
        k2 = keys[1]
        plainText = []
        cipherBinary = self.getBinaryText(cipherText)
        for bt in cipherBinary:
             plainText.append(self.fkFunction(bt, k2, k1))
        return self.binaryToText(plainText)
    

    def encrypt(self, plainText):
        keys = self.keyGenerate()
        k1 = keys[0]
        k2 = keys[1]
        cipherText = []
        byteTextSet = self.getBinaryText(plainText)
        for bt in byteTextSet:
            cipherText.append(self.fkFunction(bt, k1, k2))
        return self.binaryToText(cipherText)

def main():
    des = Des()
    cipher = des.encrypt('pronto para encriptar campeão?')
    print(cipher)

    plain = des.decrypt(cipher)
    print(plain)
if __name__ == '__main__':
    main()