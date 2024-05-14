#!/usr/bin/env python

from __future__ import print_function

import os, sys, time, random, struct, io

from io import BytesIO

VERSION = 1.0

from pydbase import twincore, twinchain

def search_index(vcore, hashname, textx, hashfunc, ccc = None):

    '''
        Use hash for searching index. Regenerate if not available.
    '''

    #print("Search_index()", os.path.realpath(hashname), textx)

    # Nothing to see here
    if not vcore.getdbsize():
        return []

    if ccc:
        ccc.rec_cnt = 0
    try:
        ifp = open(hashname, "rb")
    except:
        #print("Regenerate hash", hashname)
        append_index(vcore, hashname, hashfunc, None, ccc)
        try:
            ifp = open(hashname, "rb")
        except:
            print("Cannot generate hash", hashname)
            return

    buffsize = vcore.getsize(ifp)
    ifp.seek(twincore.HEADSIZE, io.SEEK_SET)
    datasize = vcore.getdbsize()
    fakedict = {}
    fakedict['name'] = textx
    enc = vcore.packer.encode_data("", fakedict)

    # We populate all indexed entries, as they are the only significant field
    hhh = hashfunc(vcore, [textx, enc])
    #hhh = struct.unpack("I", hhh)[0]
    # reverse
    hhh2  = hhh.to_bytes(4, 'little')
    #print("hhh2",  hhh2)

    ttt = time.time()
    cnt = 0
    ddd3 = []

    # Tried it ... 140 ms
    #while True:
    #    if ccc:
    #        if ccc.stop:
    #            break
    #    val = ifp.read(4)
    #    if not val:
    #        break;
    #    val2 = struct.unpack("I", val)[0]
    #    if hhh == val2:
    #        ddd3.append(cnt)
    #    cnt += 1

    # Tried it .... 7 seconds ! ouch
    #arr4 = array.array('i')
    #arr4.frombytes(data)
    #buf = arr4.buffer()
    #arr4.byteswap()
    #for aa in range(len(arr4)):
    #   if val == hhh:
    #       print("found", aa)
    #       ddd3.append(cnt)

    # Tried it ... 80 ms with the 'in' method 6 ms
    # Algorythm: 1.) Load Slice 2.) bulk search it
    # 3.) Convert it into BytesIO buffer 4.) Detail search it

    slice = 10000        # Make sure it is divisible by 4
    while True:
        if ccc:
            if ccc.stop:
                break
        data = ifp.read(slice)
        if not data:
            break;
        #print("data", data)
        # Bulk search it first
        if not hhh2 in data:
            cnt += slice // 4
            continue
        cnt2 = 0
        fp = BytesIO(data)
        while True:
            val = fp.read(4)
            if not val:
                break
            #if cnt2 < 3:
            #    print(val)
            if val == hhh2:
                ddd3.append(cnt + cnt2)
                #print("Found", cnt2 + cnt)
            cnt2 += 1
        cnt += slice // 4

    ifp.close()

    # Reverse findings, as sequencial read was in forward direction
    ddd4 = ddd3[::-1]
    #print("search delta %.2f ms" % (1000 * (time.time() - ttt)) )

    return ddd4

# ---------------------------------------------------------------

def   append_index(vcore, idxname,  hashx, rrr, ccc = None):

    ''' append hashx to index file.
        generate / re - index if not there. If no hash passed,
        just regenerate
    '''

    #print("append_index", idxname, rrr)

    ttt = time.time()
    ifp = vcore.softcreate(idxname)
    buffsize = vcore.getsize(ifp)
    if buffsize < twincore.HEADSIZE:
        vcore.create_data(ifp)
        ifp.seek(twincore.HEADSIZE, io.SEEK_SET)
        buffsize = vcore.getsize(ifp)

    ifp.seek(0, io.SEEK_END)
    bsize = (buffsize - twincore.HEADSIZE) // 4
    datasize = vcore.getdbsize()
    #print("bsize", bsize, "datasize:", datasize)
    ddiff = datasize - bsize
    if ddiff:
        #print("re-hash:", ddiff)
        ddd2 = []
        cnt = 0
        for aa in range(bsize, datasize):
            rrrr = vcore.get_rec(aa)
            #print("rrrr:", rrrr)
            if not rrrr:
                # Deleted record has empty hash, keeps offset correct
                rrrr.append("")
            try:
                hhh = hashx(vcore, rrrr)
            except:
                hhh = 0

            # Print last entry for timing test
            #if aa == datasize - 1:
            #    print("lastrec: hhh gen", cnt, rrrr)

            # Print progress
            #if cnt % 10000 == 0:
            #    print("hhh gen", cnt, hex(hhh))

            if cnt % 5000 == 0:
                if ccc:
                    ccc.labsss.set_text("Indexing: %d of %d" % (cnt, datasize))
                    pgutils.usleep(5)

            pp = struct.pack("I", hhh)
            ifp.write(pp)
            cnt += 1

        #print("gen_index done %.2fs" % (time.time() - ttt) )

        if ccc:
            ccc.labsss.set_text("Indexing: %d of %d" % (cnt, datasize))
            pgutils.usleep(5)

    else:
        if rrr:
            hhh = hashx(vcore, rrr)
            print("append hashx", hex(hhh))
            pp = struct.pack("I", hhh)
            ifp.write(pp)
    ifp.close()

def hash_id(vcore, rrr):

    ''' Produce a hash of ID from record header '''

    #print("hash_id:", rrr)
    if type(rrr[0]) != type(b""):
        rrr[0] = rrr[0].encode()
    hhh = vcore.hash32(rrr[0])
    return hhh

def hash_name(vcore, rrr):

    ''' Produce a hash of name from record name field
        case and whitespce insensitive.
    '''

    #print("hash_name:", rrr)
    if type(rrr[0]) != type(b""):
        rrr[0] = rrr[0].encode()
    dec = vcore.packer.decode_data(rrr[1])[0]['PayLoad']
    sss = dec['name'].upper().replace(" ", "")
    #print("sss:", sss)
    hhh = vcore.hash32(sss.encode())
    return hhh

