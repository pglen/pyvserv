# PROTOCOL

 This is a sketch for pyvserv the protocol. A hybrid between a spec and a design
document. The implementation follows loosely the outline of the interaction
outlined below.

    Client                          Server
    ------                          ------

    TCP connection established.    Send sign on str

Initial state:

    query server                    send commensurate answer
    akey requested                  send randomly selected public key

Akey state:

    ready to establish session
    session key generated,          session key stored
                                    encrypted, transmitted
Session state:

    establish credentials           confirm session state
                                    acknowledge established session
    remember session ID

Transaction state, one transaction:

    send rand str
    send checksum                   seed with random amount of data
    Transactions start              respond with packer data
    send packer data

    repeat ....

... Disconnect ...

    send the Quit command           Server closes connection

... Timeout ...

    when inactivity for N seconds   mark the thread state with timeout
    on the next transaction         send goodbye, close connection

# EOF
