import cv2
import time, os
from movement import Movement
import constant
from tornado import web, ioloop
import threading
import json
import requests
import logging


# take gestures, send gestures
def ManageMotion():
    move = Movement()
    while move.IsActive():

        #FRAME infos
        # Manage movement, gestures
        move.GetInfoFromNextFrame()
        #cv2.imshow('Current FrameDIFFF', move.currFrame)
        if move.ElapsedTimeSinceLastMovement() > 5:
            time.sleep(1)

        gesture = move.TakeGesture()
        threading.Thread(target=SendGesture, args=(gesture,)).start()

    move.FreeDevices()
    os._exit(1)

def SendGesture(gestures):

    try:
        requests.get("http://localhost:3000/movement/gestures?params="+json.dumps(gestures.features))
    except Exception as ex:
        print("Can not send gestures: " + str(ex))


if __name__ == '__main__':
    threading.Thread(target=ManageMotion).start()
    ioloop.IOLoop.current().start()

