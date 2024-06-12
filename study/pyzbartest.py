#!/usr/bin/env python

''' Test reader '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import threading
import queue
import qrcode

import cv2
from pyzbar.pyzbar import decode

# initalize the cam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BACKLIGHT, 0)

# initialize the cv2 QRCode detector
#detector = cv2.QRCodeDetector()

datax = None

def scan():

    global datax, qqq

    while True:
        _, img = cap.read()
        datax = decode(img)
        if datax:
            #print("[+] QR Code detected, data:", datax)
            rrr = datax[0].rect
            ul = tuple((rrr[0], rrr[1]))
            ur = tuple((rrr[0] + rrr[2], rrr[1]))
            ll = tuple((rrr[0], rrr[1] + rrr[3]))
            lr = tuple((rrr[0] + rrr[2], rrr[1] + rrr[3]))
            colx = (0, 255, 0)
            thickx = 2

            cv2.line(img, ul, ur, color=colx, thickness=thickx)
            cv2.line(img, ur, lr, color=colx, thickness=thickx)
            cv2.line(img, ul, ll, color=colx, thickness=thickx)
            cv2.line(img, ll, lr, color=colx, thickness=thickx)

            qqq.put(datax)
            #break

        # display the result
        cv2.imshow("img", img)

        if cv2.waitKey(20) == ord("q"):
            break

def scanfunct():

    global qqq

    qqq = queue.Queue(5)

    ttt = threading.Thread(None, target=scan)
    ttt.daemon = True
    ttt.start()
    last = time.time()

    fp = open("/home/peterglen/Downloads/upc_corpus.csv", "rt")
    fff = fp.read()
    sss = fff.split("\n")
    print("Ready")
    seen = []
    while True:
        fp.seek(0)
        datax = qqq.get()

        if datax[0].data in seen:
            if (time.time() - last) < 2:
                continue
            else:
                last = time.time()
        else:
            seen.append(datax[0].data)

        print("Code detected, data:", datax[0])
        try:
            ddd = datax[0].data.decode()
        except:
            print("exc", sys.exc_info())
            ddd = "None"

        #print("ddd", ddd)
        cnt = 0
        for aa in sss:
            #if cnt < 10:
            #    print("aa", aa)
            if aa.find(ddd) >= 0:
                print(aa)
            cnt += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    scanfunct()

# EOF
