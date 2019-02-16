import cv2
import time
from tornado import web, ioloop
import threading
import os
import constant
from movement import Movement
import main

def nothing(x):
    pass

def ManageMotion():
    motion = Movement()

    # Params to change on the fly
    cv2.namedWindow('MinMaxValues')
    cv2.createTrackbar('MAX H', 'MinMaxValues', 1, 255, nothing)
    cv2.createTrackbar('MAX S', 'MinMaxValues', 1, 255, nothing)
    cv2.createTrackbar('MAX V', 'MinMaxValues', 1, 255, nothing)
    cv2.createTrackbar('MIN H', 'MinMaxValues', 1, 255, nothing)
    cv2.createTrackbar('MIN S', 'MinMaxValues', 1, 255, nothing)
    cv2.createTrackbar('MIN V', 'MinMaxValues', 1, 255, nothing)

    cv2.setTrackbarPos('MAX H', 'MinMaxValues', constant.HSVConf['hsv_palm_max'][0])
    cv2.setTrackbarPos('MAX S', 'MinMaxValues', constant.HSVConf['hsv_palm_max'][1])
    cv2.setTrackbarPos('MAX V', 'MinMaxValues', constant.HSVConf['hsv_palm_max'][2])
    cv2.setTrackbarPos('MIN H', 'MinMaxValues', constant.HSVConf['hsv_palm_min'][0])
    cv2.setTrackbarPos('MIN S', 'MinMaxValues', constant.HSVConf['hsv_palm_min'][1])
    cv2.setTrackbarPos('MIN V', 'MinMaxValues', constant.HSVConf['hsv_palm_min'][2])

    cv2.namedWindow('SearchRangeHand')
    cv2.createTrackbar('INC H', 'SearchRangeHand', 1, 255, nothing)
    cv2.createTrackbar('INC S', 'SearchRangeHand', 1, 255, nothing)
    cv2.createTrackbar('INC V', 'SearchRangeHand', 1, 255, nothing)
    cv2.createTrackbar('DEC H', 'SearchRangeHand', 1, 255, nothing)
    cv2.createTrackbar('DEC S', 'SearchRangeHand', 1, 255, nothing)
    cv2.createTrackbar('DEC V', 'SearchRangeHand', 1, 255, nothing)

    cv2.setTrackbarPos('INC H', 'SearchRangeHand', constant.HSVConf['hsv_hand_inc'][0])
    cv2.setTrackbarPos('INC S', 'SearchRangeHand', constant.HSVConf['hsv_hand_inc'][1])
    cv2.setTrackbarPos('INC V', 'SearchRangeHand', constant.HSVConf['hsv_hand_inc'][2])
    cv2.setTrackbarPos('DEC H', 'SearchRangeHand', constant.HSVConf['hsv_hand_dec'][0])
    cv2.setTrackbarPos('DEC S', 'SearchRangeHand', constant.HSVConf['hsv_hand_dec'][1])
    cv2.setTrackbarPos('DEC V', 'SearchRangeHand', constant.HSVConf['hsv_hand_dec'][2])
    frameIdx = 0
    currentSliding = "None"
    timeElapsedSinceLastSlide = time.time()

    if not motion.IsActive():
        print("Kamera Yok")
        return

    # Debug Palm Tracking (See palm color detection in real time - consuming)
    motion.debugPalm = False

    while motion.IsActive():
        # Refresh OpenCV Windows
        cv2.waitKey(1)

        # main.ManageCommands(motion)

        # Refresh config from param
        constant.HSVConf['hsv_palm_max'] = [cv2.getTrackbarPos('MAX H', 'MinMaxValues'), cv2.getTrackbarPos('MAX S', 'MinMaxValues'), cv2.getTrackbarPos('MAX V', 'MinMaxValues')]
        constant.HSVConf['hsv_palm_min'] = [cv2.getTrackbarPos('MIN H', 'MinMaxValues'), cv2.getTrackbarPos('MIN S', 'MinMaxValues'), cv2.getTrackbarPos('MIN V', 'MinMaxValues')]
        constant.HSVConf['hsv_hand_inc'] = [cv2.getTrackbarPos('INC H', 'SearchRangeHand'), cv2.getTrackbarPos('INC S', 'SearchRangeHand'), cv2.getTrackbarPos('INC V', 'SearchRangeHand')]
        constant.HSVConf['hsv_hand_dec'] = [cv2.getTrackbarPos('DEC H', 'SearchRangeHand'), cv2.getTrackbarPos('DEC S', 'SearchRangeHand'), cv2.getTrackbarPos('DEC V', 'SearchRangeHand')]

        # Manage motion and gestures
        motion.GetInfoFromNextFrame()

        # Infos movement
        try:
            cv2.putText(motion.frameDiff, "Elapsed: " + str(motion.TimeElapsedSinceLastMotion()) + "/" + str(5), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(motion.frameDiff, "Movement: " + str(motion.movementRatio) + "/" + str(constant.FRAME_DIFF_RATIO_FOR_MOVEMENT), (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Movement detected', motion.frameDiff)
        except:
            pass

        if motion.ElapsedTimeSinceLastMovement() > 5:
            cv2.putText(motion.currFrame, "SLEEPY MODE NO MOVEMENT", (5, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow('Current Frame', motion.currFrame)
            time.sleep(1)

        gestures = motion.TakeGesture()

        if gestures.features['gestPalm']:
            print("PALM EL HAREKET")
        threading.Thread(target=main.SendGesture, args=(gestures,)).start()

        # Gesture infos
        try:
            #print("Frame: " + str(frameIdx))
            frameIdx += 1
            #print(gesture.properties)

            if motion.trackedHandGesture is None:
                cv2.putText(motion.currFrame, "Hareket Ara...??", (5, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 1)

            cv2.imshow('Current Frame', motion.currFrame)

            cv2.imshow('Mask from HSV Range', motion.workedMask)
            cv2.putText(motion.currFrame, "Width: " + str(gestures.rectangleW), (5, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 1)
            cv2.putText(motion.currFrame, "Height: " + str(gestures.rectangleH), (5, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 1)
            cv2.putText(motion.currFrame, "SRatio: " + str(gestures.rectangleH / gestures.rectangleW), (5, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 1)
            cv2.rectangle(motion.currFrame, (gestures.rectangleX, gestures.rectangleY), (gestures.rectangleX + gestures.rectangleW, gestures.rectangleY + gestures.rectangleH), (0, 255, 0), 2)

            cv2.putText(motion.currFrame, "MSize: " + str(gestures.moments['m00']), (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 200, 1)
            cv2.drawContours(motion.currFrame, [gestures.handContour], 0, (0, 255, 0), 3)
            cv2.circle(motion.currFrame, (int(gestures.CenterX), int(gestures.CenterY)), int(gestures.radius / 1.5), [255, 0, 255], 1)
            cv2.circle(motion.currFrame, (int(gestures.CenterX), int(gestures.CenterY)), int(gestures.radius / 3.2), [255, 0, 255], 1)
            cv2.putText(motion.currFrame, "A: " + str(gestures.features['gestAngle']), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 200)

            if gestures.features['gestPalm']:
                cv2.putText(motion.currFrame, "PALM HAREKET", (5, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, 150, 3)
            elif gestures.features['gestThumbsUp']:
                cv2.putText(motion.currFrame, "THUMBS UP", (5, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, 150, 3)
            elif gestures.features['gestThumbsDown']:
                cv2.putText(motion.currFrame, "THUMBS DOWN", (5, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, 150, 3)
            if gestures.features['gestSlideUp'] or gestures.features['gestSlideDown'] or gestures.features['gestSlideRight'] or gestures.features['gestSlideLeft']:
                timeElapsedSinceLastSlide = time.time()
                currentSliding = "UP" if gestures.features['gestSlideUp'] else "DOWN" if gestures.features['gestSlideDown'] else "RIGHT" if gestures.features['gestSlideRight'] else "LEFT"
            if time.time() - timeElapsedSinceLastSlide < 1:
                cv2.putText(motion.currFrame, "Sliding " + currentSliding, (5, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, 150, 3)

            for defect in gestures.gestPalmDefects:
                cv2.line(motion.currFrame, defect[0], defect[1], [255, 0, 0], 2)
                cv2.circle(motion.currFrame, defect[2], 6, [0, 0, 255], -1)

            cv2.imshow('Current Frame', motion.currFrame)
        except:
            pass


        pressedKey = cv2.waitKey(33)
        if pressedKey == 27:  # Esc key to stop
            break

    motion.FreeDevices()
    os._exit(1)

if __name__ == '__main__':
    threading.Thread(target=ManageMotion).start()
    ioloop.IOLoop.current().start()
