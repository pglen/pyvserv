# login
import sys, passlib

def login():
    print "Enter pass", 
    sys.stdout.flush()
    
    username = raw_input('Python login:\n')
    print "username '"+ username + "'"
    cryptedpasswd = bcrypt.hashpw(username, bcrypt.gensalt())
        
    cryptedpasswd = pwd.getpwnam(username)[1]
    if cryptedpasswd:
        if cryptedpasswd == 'x' or cryptedpasswd == '*':
            raise NotImplementedError(
                "Sorry, currently no support for shadow passwords")
        #cleartext = getpass.getpass()
        
        return crypt.crypt(cleartext, cryptedpasswd) == cryptedpasswd
    else:
        return 1



if __name__ == '__main__':
    login()

