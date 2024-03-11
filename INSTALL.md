## INSTALL

python 3.x is supported  (py2 support obsoleted)

# Preliminary

This document is obsolete. Use pip to install.

    pip install pyvserv


sudo apt-get update -y
sudo apt-get upgrade -y

1.) Create a pyvserv environment (optional)

sudo useradd -m -s /bin/bash pyvserv
sudo passwd pyvserv
sudo usermod -aG sudo pyvserv

su - pyvserv

On Ubuntu:

    pip install pycrypto
    pip install bcrypt

    (pip is using py3 if newer Linux, else use pip3)

  ... or ...

    apt install python3-psutil
    apt install python3-crypto

On msys2 the following dependencies where needed:

    pacman -S mingw-w64-i686-gcc

    pip install passlib
    pip install pycrypto
    pip install bcrypt

#Switched to pycrypto, no libgcrypt is needed
#pacman -S mingw-w64-i686-libgcrypt

The alternate:

    sudo apt install python3-bcrypt
    sudo apt install pycrypto

On Fedora:

    sudo yum install python3-bcrypt
    sudo yum install pycrypto


# Update:

Pycrypto went thru an update and a name change

pip uninstall pycrypto
pip install pycryptodome

May want to use --force-reinstall option if you have problems.

# EOF
