import time
import cv2
import math
import constant
import movement

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def Dairede(cX, cY, radius, x, y):
    dist = math.sqrt((cX - x) ** 2 + (cY - y) ** 2)
    return dist <= radius

class Gestures(object):
    lastGestureSlideTime = time.time()
    leftPositionsFromTime = []
    rightPositionsFromTime = []
    upPositionsFromTime = []
    downPositionsFromTime = []
    def __init__(self):
        self.BasicGesture()

    def BasicGesture(self):
        self.features = {}
        self.features['elapsedTimeWithSameGesture'] = 0
        self.features['gestPalm'] = False
        self.features['gestThumbsUp'] = False
        self.features['gestThumbsDown'] = False
        self.features['gestSlideUp'] = False
        self.features['gestSlideDown'] = False
        self.features['gestSlideRight'] = False
        self.features['gestSlideLeft'] = False
        self.features['gestAngle'] = -1
        self.features['gestCenterX'] = -1
        self.features['gestCenterY'] = -1
        self.features['gestHandFound'] = False
        self.features['gestNeedPalm'] = False

        self.gestPalmDefects = []
        # ***************
        self.handContour = 0

    def CheckPalmGesture(self):
        #print("CheckPalmGesture")
        self.gestPalmDefects = []
        try:
            for i in range(self.defects.shape[0]):
                #defect bilgileri alinir.
                s,e,f,d = self.defects[i,0]
                start = tuple(self.handContour[s][0])
                end = tuple(self.handContour[e][0])
                far = tuple(self.handContour[f][0])

                #defect dogru yerdemi kontrol edilir.

                #TO DO..
                if not Dairede(int(self.CenterX), int(self.CenterY), int(self.radius / 1.5), far[0], far[1]):
                    continue
                if Dairede(int(self.CenterX), int(self.CenterY), int(self.radius / 3.2), far[0], far[1]):
                    continue

                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57
                self.features['gestAngle'] = angle
                if angle <= 120:
                    self.gestPalmDefects.append((start,end,far))
                    if self.ControlPalmDefects():
                        self.features['gestPalm']=True
                        return True
        except AttributeError:
            print("NOTFOUND..")
        return False


    def ControlPalmDefects(self):
        #print("ControlPalmDefects")
        if len(self.gestPalmDefects) < 4:
            return False
        defectCount=0
        pX = []     #pozisyon
        pY = []     #pozisyon
        for dfct in self.gestPalmDefects:
            if dfct[2][1] < int(self.CenterY):
                defectCount += 1
                pX.append(dfct[2][0])
                pY.append(dfct[2][1])
        if defectCount < 3:
            return False

        #ortalama - pozisyon - constant..
        meanY = sum(pY)/len(pY)
        for p in pY:
            if abs(p - meanY) / self.rectangleH > 0.08:
                return False

        meanX = sum(pX)/len(pX)
        for p in pX:
            if abs(p - meanX) / self.rectangleW > 0.2:
                return False


        return True

    def PalmGestureSearchFromMask(self,MaskedFrame):
        #print("PalmGestureSearchFromMask")
        #her contour u kontrol edilir. özellikleri alinir.
        (_, contours, _) = cv2.findContours(MaskedFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if self.TakeContourFeatureFirst(cnt):
                return self.CheckPalmGesture()
        return False

    def TakeContourFeatureFirst(self,cnt):
        #print("TakeContourFeatureFirst")
        #rectangle ile sinirlanir ve filtrelenir, moment cok zaman alir o yüzden.
        x,y,w,h = cv2.boundingRect(cnt)
        self.rectangleX = x
        self.rectangleY = y
        self.rectangleW = w
        self.rectangleH = h

        #elin minimum ve maximum boyutlari sinir olarak belirlenir o sarta göre contour dan bilgiler alinir.
        if self.rectangleW < 80 or self.rectangleW > 320 or self.rectangleH < 80 or self.rectangleH > 350:
            return False

        self.handContour = cnt
        self.features['gestHandFound'] = True

        #bilgiler.
        self.moments = cv2.moments(cnt)
        self.hull = cv2.convexHull(self.handContour, returnPoints=False)
        self.defects = cv2.convexityDefects(self.handContour, self.hull)

        _, radius = cv2.minEnclosingCircle(self.handContour)
        self.radius = int(radius / 1.2)
        self.CenterX = int(self.moments['m10'] / self.moments['m00'])
        self.CenterY = int(self.moments['m01'] / self.moments['m00'])

        self.features['gestCenterX'] = self.CenterX
        self.features['gestCenterY'] = self.CenterY

        #GestureInit -------
        self.CheckPalmGesture()
        if not self.features['gestPalm']:
            self.CheckThumbsGesture()
        self.CheckSlidingGesture()

        return True

    def CheckThumbsGesture(self):
        #print("CheckThumbsGesture")
        # durumlar var exception icin
        outOfCenterArea = (self.rectangleH - (2*self.radius)) / self.rectangleH
        if outOfCenterArea < (constant.GESTURE_THUMBS_MIN_HEIGHT):
            return
        #thumbsUp veya thumbsDown
        if ((self.rectangleY + self.rectangleH) - (self.CenterY + self.radius)) / self.rectangleH > (constant.GESTURE_THUMBS_MIN_HEIGHT):
            self.features['gestThumbsDown'] = True
        elif((self.CenterY - self.radius) - self.rectangleY) / self.rectangleH > (constant.GESTURE_THUMBS_MIN_HEIGHT):
            self.features['gestThumbsUp'] = True

    def CheckSlidingGesture(self):
        #print("CheckSlidingGesture")
        currTime = time.time()
        if currTime - Gestures.lastGestureSlideTime < (constant.OTHER_SLIDE_GESTURE_DELAY):
            return
        # control left right up down
        self.features["gestSlideUp"],Gestures.downPositionsFromTime = self.CheckSlidingGesturePositionsInFrame(
            Gestures.downPositionsFromTime, self.rectangleY + self.rectangleH, False, currTime)
        self.features['gestSlideDown'],Gestures.upPositionsFromTime = self.CheckSlidingGesturePositionsInFrame(
            Gestures.upPositionsFromTime, self.rectangleY, True, currTime)
        self.features['gestSlideLeft'],Gestures.leftPositionsFromTime = self.CheckSlidingGesturePositionsInFrame(
            Gestures.leftPositionsFromTime, self.rectangleX, True, currTime)
        self.features['gestSlideRight'],Gestures.rightPositionsFromTime = self.CheckSlidingGesturePositionsInFrame(
            Gestures.rightPositionsFromTime, self.rectangleX + self.rectangleW, False, currTime)



    def CheckSlidingGesturePositionsInFrame(self, positionsFromTime, newPosition, newPositionMustBeGreater, currentTime):
        #print("CheckSlidingGesturePositionsInFrame")
        # TO DO
        slideMovement = False
        positionsFromTime = [positionAndTime for positionAndTime in positionsFromTime if currentTime - positionAndTime[1] < (constant.SLIDE_GESTURE_TIME)]

        # TO DO
        if len(positionsFromTime) > 0 and ((not newPositionMustBeGreater and positionsFromTime[-1][0] < newPosition) or ( newPositionMustBeGreater and positionsFromTime[-1][0] > newPosition)):
            positionsFromTime = []

        positionsFromTime.append((newPosition, currentTime))

        positionHandMove = abs(positionsFromTime[0][0] - positionsFromTime[-1][0])
        if len(positionsFromTime) > 1 and positionHandMove >= (constant.TO_SLIDE_GESTURE_MIN_MOVE):
            slideMovement = True
            upPositionsFromTime = []
            downPositionsFromTime = []
            leftPositionsFromTime = []
            rightPositionsFromTime = []
            # TO DO
            Gestures.lastGestureSlideTime = currentTime

        return (slideMovement,positionsFromTime)

    def FindHandFromMaskAndPositions(self,handMask,nearestFromX,nearestfromY):
        #print("FindHandFromMaskAndPositions")
        (_, contours, _) = cv2.findContours(handMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return False

        distanceCnts = []

        for contour in contours:
            cv2.drawContours(movement.Movement.currFrame, [contour], 0, (0, 0, 250), 2)
            moment = cv2.moments(contour)
            centerX = int(moment["m10"] / moment["m00"])
            centerY = int(moment["m01"] / moment["m00"])
            distance = abs(centerX - nearestFromX) + abs(centerY - nearestfromY)
            distanceCnts.append(distance)

        while contours:
            indexNearestContour = min(range(len(distanceCnts)), key=distanceCnts.__getitem__)
            if not self.TakeContourFeatureFirst(contours[indexNearestContour]):
                contours.pop(indexNearestContour)
                distanceCnts.pop(indexNearestContour)
                continue
            return True
        return False

