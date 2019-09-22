# Krypto chat
A chat core that uses RC4 and S-DES encryption algorithms

<img src="https://github.com/mrmorais/encrypted-chat/blob/master/krypto.png?raw=true" width="250" />

![](https://github.com/mrmorais/encrypted-chat/blob/master/chat_example.png?raw=true)

## Running

Krypto has no third parties dependencies, so you can run it with a simple:

```bash
./chat.py
```

### Parameters

When initializing a chat server/client you can set up some attributes that krypto needs. Here's the usage helper:

```
$ ./chat.py -h
usage: chat.py [-h] [-os OFFSET] [-addr HOST] [-p PORT] [-q Q] [-a ALPHA]

Encrypted chat connector.

optional arguments:
  -h, --help            show this help message and exit
  -os OFFSET, --offset OFFSET
                        Binding port offset
  -addr HOST, --address HOST
                        Host IP address
  -p PORT, --port PORT  Socket port
  -q Q                  Diffie-Hellman q parameter
  -a ALPHA, --alpha ALPHA
                        Diffie-Hellman alpha parameter
```
