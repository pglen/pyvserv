

def diff(expectx, actualx):

    ''' Compare values, display string in Color '''

    if expectx == actualx:
        print("\t\033[32;1mOK\033[0m")
    else:
        print("\t\033[31;1mERR\033[0m")

# EOF
