

def diff(expectx, actualx):

    ''' Compare values, display string in Color '''

    if expectx == actualx:
        print("\tOK")
    else:
        print("\t\033[31;1mERR\033[0m")

# EOF
