    def action(self, repcore):

        ''' OBSOLETE
            Scan db and create needed rep action entries
        '''

        dbsize = repcore.getdbsize()
        # Increment count:
        cntstr2 = "00000"
        cntstr3 = "00000"
        cntstr = "%05d" % (int(arr['count1']) + 1)
        arr['count1'] = cntstr
        #print("arr:", arr)
        if  not int(arr['count2']):
            #if  int(cntstr) > 1  and int(cntstr) < 4:

            # condition for transmit try
            tryit =  int(arr['count3'])  > 0 and int(cntstr) == 6
            tryit |= int(arr['count3']) == 0 and int(cntstr) == 1

            if tryit:
                wastrans = True
                success = self.replicate(dirname, rec[0])
                if success:
                    if self.pgdebug > 5:
                        print("Succeeded", rec[0])
                     # Increment success count:
                    cntstr2 = "%05d" % (int(arr['count2']) + 1)
                    arr['count2'] = cntstr2
                else:
                    if self.pgdebug > 0:
                        print("Failed", rec[0])
                     # Increment failure count:
                    cntstr3 = "%05d" % (int(arr['count3']) + 1)
                    arr['count3'] = cntstr3
                    arr['count1'] = 0
        else:
            if self.pgdebug > 2:
                print("Marked done", arr['header'])

        strx = str(self.packer.encode_data("", arr))
        #print("Save rep", rec[0], strx)
        #ttt = time.time()
        ret = repcore.save_data(rec[0], strx, True)
        #print("db save %.3f" % ((time.time() - ttt) * 1000) )

        # Failed? Keep it for a while
        delok = 0
        if int(cntstr3) == 0:
            if int(cntstr) > 6:
                #print("del rec:", rec[0])
                delok = True
        else:
            if int(cntstr3) > 3:
                delok = True
        if delok:
            ret = repcore.del_rec_bykey(rec[0])

        if dbsize > MAX_DBSIZE:

            if self.pgdebug > 2:
                print("vacuuming", dbsize)
            if self.pgdebug > 5:
                ttt = time.time()
            repcore.vacuum()
            if self.pgdebug > 5:
                print("db vacuum %.3f" % ((time.time() - ttt) * 1000) )

        del repcore
        if wastrans:
            if self.pgdebug > 5:
                self._print_handles()


