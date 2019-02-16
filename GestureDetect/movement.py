import cv2
import numpy as np
import time
import constant
from gestures import Gestures

if (constant.PI_CAMERA):
    from picamera.array import PiRGBArray
    from picamera import PiCamera


class Movement(object):
    prevFrame = None
    currFrame = None

    def __init__(self):
        self.HSVHandPoint = None
        self.currentGesture = None
        self.timeSinceFoundHandTracked = 0
        self.foundHandGesture = False
        self.onlyTrackedHandGestureArea = None
        self.trackedHandGesture = None
        self.elapsedTimeSinceLastDifferentGesture = time.time()
        self.previousGestureFeatures = None
        self.lastMovementTime = time.time()
        self.movementRatio = 0
        self.gestPalmDebug = False
        self.workedMask=None

        if (constant.PI_CAMERA):
            self.picamera = PiCamera()
            self.picamera.resolution = (constant.CAM_RESOLUTION)
            self.picamera.framerate = (constant.CAM_FRAMRATE)

        else:
            self.videoDevice = cv2.VideoCapture(0)

    def IsActive(self):
        if (constant.PI_CAMERA):
            return not self.picamera.closed

        return self.videoDevice.isOpened()

    def ElapsedTimeSinceLastMovement(self):
        return time.time() - self.lastMovementTime

    def FoundMovement(self):
        return int(self.movementRatio) > (constant.FRAME_DIFF_RATIO_FOR_MOVEMENT)

    def FreeDevices(self):
        if (constant.PI_CAMERA):
            self.picamera.close()
        else:
            self.videoDevice.release()

        cv2.destroyAllWindows()

    def GetFrameDevice(self):
        if not (constant.PI_CAMERA):
            _, Movement.currFrame = self.videoDevice.read()
            return

        # grab an image from the camera and convert it to an array
        rawCapture = PiRGBArray(self.picamera)
        self.picamera.capture(rawCapture, format="bgr")
        Movement.currFrame = rawCapture.array

    def GetInfoFromNextFrame(self):
        # Tut prev frame
        Movement.prevFrame = Movement.currFrame

        # frame-by-frame
        self.GetFrameDevice()
        if Movement.prevFrame is None:
            return

        # take frame diff to avoid doing things when there is no movements
        self.frameDiff = cv2.absdiff(cv2.cvtColor(Movement.currFrame, cv2.COLOR_RGB2GRAY), cv2.cvtColor(Movement.prevFrame, cv2.COLOR_RGB2GRAY))
        cntGray = 0
        for rowGray in self.frameDiff:
            for gray in rowGray:
                cntGray += gray
        self.movementRatio = cntGray / self.frameDiff.size

        if self.FoundMovement() is False:
            return

        # Keep track of last motion
        self.lastMovementTime = time.time()


    def TryHandTrack(self):
        lower_blue_brightness = constant.HSVConf['hsv_palm_max'][2]
        handSearching = Gestures()

        while lower_blue_brightness > 15:
            # define range of blue color in HSV
            lower_blue = np.array([constant.HSVConf['hsv_palm_min'][0], constant.HSVConf['hsv_palm_min'][1], lower_blue_brightness])
            upper_blue = np.array([constant.HSVConf['hsv_palm_max'][0], constant.HSVConf['hsv_palm_max'][1], constant.HSVConf['hsv_palm_max'][2]])

            kernelMask = np.ones((5, 5), np.float32) / 25
            blurredMask = cv2.filter2D(self.currFrame.copy(), -1, kernelMask)
            hsv = cv2.cvtColor(blurredMask, cv2.COLOR_BGR2HSV)

            # Threshold the HSV image to get only blue colors
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            self.workedMask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelMask)

            # Debug Palm Detection
            if self.gestPalmDebug:
                cv2.imshow('Mask from HSV Range', self.workedMask)
                cv2.waitKey(5)

            search_hand_mask = self.workedMask.copy()
            foundPalm = handSearching.PalmGestureSearchFromMask(search_hand_mask)

            if foundPalm:
                # Set infos from tracked hand
                self.trackedHandGesture = handSearching
                self.timeSinceFoundHandTracked = time.time()
                self.HSVHandPoint = hsv[self.trackedHandGesture.CenterY][self.trackedHandGesture.CenterX]
                self.foundHandGesture = True
                return

            lower_blue_brightness -= 10

        self.foundHandGesture = False

    def FindHandFromTrack(self):
        # Get brightness from tracked hand
        kernelM = np.ones((5, 5), np.float32) / 25
        blurredM = cv2.filter2D(self.currFrame.copy(), -1, kernelM)
        hsv = cv2.cvtColor(blurredM, cv2.COLOR_BGR2HSV)

        self.hand_lower_blue = self.AddValueToColorArray([-constant.HSVConf['hsv_hand_dec'][0], -constant.HSVConf['hsv_hand_dec'][1], -constant.HSVConf['hsv_hand_dec'][2]], self.HSVHandPoint.copy())
        self.hand_upper_blue = self.AddValueToColorArray([constant.HSVConf['hsv_hand_inc'][0], constant.HSVConf['hsv_hand_inc'][1], constant.HSVConf['hsv_hand_inc'][2]], self.HSVHandPoint.copy())
        #takes related colors details
        mask = cv2.inRange(hsv, self.hand_lower_blue, self.hand_upper_blue)
        # artifactsler doing
        self.workedMask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelM)
        #opening status state
        search_hand_mask = self.workedMask.copy()
        search_hand = Gestures()
        if search_hand.FindHandFromMaskAndPositions(search_hand_mask, self.trackedHandGesture.CenterX, self.trackedHandGesture.CenterY) is False:
            self.foundHandGesture = False
        else:
            self.timeSinceFoundHandTracked = time.time()
            self.trackedHandGesture = search_hand
            self.HSVHandPoint = hsv[self.trackedHandGesture.CenterY][self.trackedHandGesture.CenterX]
            self.foundHandGesture = True

    def AddValueToColor(self, value, color):
        result = color + value
        if result > 255:
            color = 255
        elif result < 0:
            color = 0
        else:
            color = result
        return color

    def AddValueToColorArray(self, value, colors):
        for idx in range(3):
            colors[idx] = self.AddValueToColor(value[idx], colors[idx])

        return colors

    def TakeGesture(self):
        # retry, thumpUp again
        timeElapsedSinceLastFoundHand = time.time() - self.timeSinceFoundHandTracked
        stillTryingToFindHandFromTrack = timeElapsedSinceLastFoundHand < 1
        if not stillTryingToFindHandFromTrack:
            self.trackedHandGesture = None

        if self.trackedHandGesture is not None or stillTryingToFindHandFromTrack:
            self.FindHandFromTrack()
            #buraya kadar kagitta.
        else:
            self.TryHandTrack()

        self.currentGesture = self.trackedHandGesture
        if not self.foundHandGesture:
            self.currentGesture = Gestures()
            self.currentGesture.features['gestNeedPalm'] = not stillTryingToFindHandFromTrack

        self.SetTimeSameGesture()
        return self.currentGesture

    def SetTimeSameGesture(self):
        if self.previousGestureFeatures is None:
            self.previousGestureFeatures = self.currentGesture.features.copy()

        if self.currentGesture.features['gestPalm'] == self.previousGestureFeatures['gestPalm'] and \
                self.currentGesture.features['gestThumbsUp'] == self.previousGestureFeatures['gestThumbsUp'] and \
                self.currentGesture.features['gestThumbsDown'] == self.previousGestureFeatures['gestThumbsDown'] and \
                self.currentGesture.features['gestSlideRight'] == self.previousGestureFeatures['gestSlideRight'] and \
                self.currentGesture.features['gestSlideLeft'] == self.previousGestureFeatures['gestSlideLeft'] and \
                self.currentGesture.features['gestSlideDown'] == self.previousGestureFeatures['gestSlideDown'] and \
                self.currentGesture.features['gestSlideUp'] == self.previousGestureFeatures['gestSlideUp']:
            self.currentGesture.features['elapsedTimeWithSameGesture'] = time.time() - self.elapsedTimeSinceLastDifferentGesture
        else:
            self.elapsedTimeSinceLastDifferentGesture = time.time()
            self.currentGesture.features['elapsedTimeWithSameGesture'] = 0

        self.previousGestureFeatures = self.currentGesture.features.copy()


