#!/usr/bin/env python

import crypt, getpass, pwd, spwd, sys

verbose = False

# ------------------------------------------------------------------------
# Return True for authenticated, user name and message
#

def login(prompt):

    ret = 0, "", ""
    username = raw_input(prompt)
    #print "Authenticating user: '" + username + "'"
    
    try:
        cryptedpasswd = pwd.getpwnam(username)
    except:
        #print "No such user: '" + username + "'" 
        ret = False,  username, "No user entry"
        return ret
        
    #print "user", cryptedpasswd[1]
    
    cleartext = getpass.getpass()
    try:
        if cryptedpasswd[1] == 'x' or cryptedpasswd[1] == '*':
            cryptedpasswd = spwd.getspnam(username)
        flag = crypt.crypt(cleartext, cryptedpasswd[1]) == cryptedpasswd[1]
        if flag:
            ret = flag, username, ""
        else:
            ret = flag, username, "Invalid password"
    except:
        #print "Cannot access shadow file", sys.exc_info()
        ret = False, username, "Cannot access shadow file"
        
    return ret

# ------------------------------------------------------------------------
if __name__ == '__main__':

    ret, user, msg = login('Python login: ')
    if ret:    
        print "Authenticated user:", "'" + user + "'"
    else:
        print "Authention failed:", msg, "for '" + user + "'"



