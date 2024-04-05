# ------------------------------------------------------------------------

class   FileLock2():

    ''' A working file lock in Linux '''

    def __init__(self):

        ''' Create the lock file '''
        self.lockname = None

    def waitlock(self):

        if not self.lockname:
            self.lockname = globals.passfile + ".lock"
            #print("lockname", self.lockname)

            try:
                self.fpx = open(self.lockname, "rb+")
            except:
                try:
                    self.fpx = open(self.lockname, "wb+")
                except:
                    if lock_pgdebug > 1:
                        print("Cannot create lock file")
                    raise

        if lock_pgdebug > 1:
            print("Waitlock", self.lockname)

        cnt = 0
        while True:
            try:
                buff = self.fpx.read()
                self.fpx.seek(0, os.SEEK_SET)
                self.fpx.write(buff)
                break;
            except:
                if lock_pgdebug > 1:
                    print("waiting", sys.exc_info())

            if cnt > lock_locktout :
                # Taking too long; break in
                if 1: #lock_pgdebug > 1:
                    print("Lock held too long pid =", os.getpid(), cnt)
                self.unlock()
                break
            cnt += 1
            time.sleep(1)
        # Lock NOW
        if fcntl:
            fcntl.lockf(self.fpx, fcntl.LOCK_EX)

    def unlock(self):
        if fcntl:
            fcntl.lockf(self.fpx, fcntl.LOCK_UN)

# ------------------------------------------------------------------------
# Simple file system based locking system
# !!!!! does not work on Linux !!!!!
# Linux can access the filesystem differently than windosw, however the
# file based locking system work well

#def _createlock(fname, raisex = True):
#
#    ''' Open for read / write. Create if needed. '''
#
#    fp = None
#    try:
#        fp = open(fname, "wb")
#    except:
#        print("Cannot open / create ", fname, sys.exc_info())
#        if raisex:
#            raise
#    return fp
#
#def dellock(lockname):
#
#    ''' Lock removal;
#        Test for stale lock;
#    '''
#
#    try:
#        if os.path.isfile(lockname):
#            os.unlink(lockname)
#    except:
#        if pgdebug > 1:
#            print("Del lock failed", sys.exc_info())
#
#def waitlock(lockname, locktout = 30):
#
#    ''' Wait for lock file to become available. '''
#
#    cnt = 0
#    while True:
#        if os.path.isfile(lockname):
#            if pgdebug > 1:
#                print("Waiting on", lockname)
#            #if cnt == 0:
#            #    try:
#            #        fpx = open(lockname)
#            #        pid = int(fpx.read())
#            #        fpx.close()
#            #    except:
#            #        print("Exc in pid test", sys.exc_info())
#            cnt += 1
#            time.sleep(0.3)
#            if cnt > locktout:
#                # Taking too long; break in
#                if pgdebug > 1:
#                    print("Warn: main Lock held too long ... pid =", os.getpid(), cnt)
#                dellock(lockname)
#                break
#        else:
#            break
#
#    # Finally, create lock
#    xfp = _createlock(lockname)
#    xfp.write(str(os.getpid()).encode())
#    xfp.close()

