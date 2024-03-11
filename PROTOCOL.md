# PROTOCOL

 This is a sketch for pyvserv the protocol. A hybrid between a spec and a design
document. The implementation follows loosely the outline of the interaction
outlined below.

    Client                          Server

    TCP connection estabilished.    Send signon str

Initial state:

    query server                    send appropriate answer
    akey requested                  send rendomly selected pub key

akey state:

    ready to estabilish session
    session key generated,          session key stored
                                    encrypted, transmitted
session state:

    estabilish credencials          confirm transaction state

transaction state:

    send rand str                   acknowledge estabilished session
    with checksum                   seed with random amount of data

    Transactions start              respond with packer data
    send packer data

... disconnect ...
