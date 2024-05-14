def get_rtest_func(self, strx):

    if pyservsup.globals.conf.pgdebug > 1:
        print( "get_rtest_func()", strx[:4])

    if len(strx) < 2:
        response = [ERR, "Must specify blockchain kind", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 3:
        response = [ERR, "Must specify link or sum", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    if len(strx) < 4:
        response = [ERR, "Must specify record id or ids", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    tmpname = os.path.join(pyservsup.globals.chaindir, strx[1])
    dname = check_chain_path(self, tmpname)

    if not dname:
        response = [ERR, "No Access to directory.", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return
    if not os.path.isdir(dname):
        response = [ERR, "Directory does not exis.t", strx[1]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    core = twincore.TwinCore(os.path.join(dname, pyservsup.chainfname + ".pydb"), 0)

    if  strx[2] == "sum":
        funcx = core.checkdata
    elif strx[2] == "link":
        funcx = core.linkintegrity
    else:
        response = [ERR, "One of 'link' or 'sum' is required.", strx[0]]
        self.resp.datahandler.putencode(response, self.resp.ekey)
        return

    errx = False; cnt = -1; arrx = []
    sss = len(strx[3:])
    for aa in strx[3:]:
        #print("test:", aa)
        try:
            ddd = core.get_payoffs_bykey(aa)
        except:
            pass
        if len(ddd) == 0:
            response = [ERR, "Data not found.", aa,]
            self.resp.datahandler.putencode(response, self.resp.ekey)
            return
        if self.pgdebug > 4:
            try:
                rec = core.get_rec(ddd[0])
                print("rec:", rec)
            except:
                print("exc: get_rec", sys.exc_info())
                raise
        ppp = funcx(ddd[0])
        if not ppp:
            arrx.append(aa)

    if len(arrx):
        response = [ERR,  arrx, len(arrx), "errors", strx[2]]
    else:
        response = [OK,  "No errors.", strx[2], sss, "records checked."]
    self.resp.datahandler.putencode(response, self.resp.ekey)

