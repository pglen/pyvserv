#!/usr/bin/env python

''' Action Handler for open records dialog '''

# pylint: disable=C0103

import os
import sys
import datetime
import time
import threading
import queue
import qrcode

import cv2
# initalize the cam
cap = cv2.VideoCapture(0)
# initialize the cv2 QRCode detector
detector = cv2.QRCodeDetector()
while True:
    _, img = cap.read()
    # detect and decode
    #datax, bbox, img2 = detector.detectAndDecode(img)
    datax, info, bbox, img2 = detector.detectAndDecodeMulti(img)
    # check if there is a QRCode in the image
    if bbox is not None:
        # display the image with lines
        print("bbox:", bbox)
        try:
            for i in range(len(bbox)):
                # draw all lines
                #cv2.line(img, tuple(bbox[i][0]),
                #                tuple(bbox[(i+1) % len(bbox)][0]),
                #                    color=(255, 0, 0), thickness=2)
                cv2.line(img, tuple(bbox[i][0].astype(int)),
                                tuple(bbox[(i+1) % len(bbox)][0]).astype(int),
                                    color=(255, 0, 0), thickness=2)
        except:
            #print("cv2", sys.exc_info()    )
            pass

    if datax:
        print("[+] QR Code detected, data:", datax, info)

    # display the result
    cv2.imshow("img", img)

    if img2:
        #cv2.imshow("img2", img2)
        print("img2:", img2)

    if cv2.waitKey(1) == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
