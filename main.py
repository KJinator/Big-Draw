from FingerDetection import *
from cmu_112_graphics import *
from tkinter import *
from PIL import Image, ImageTk
import random

def cvtotk(img):
    b, g, r = cv2.split(rescale_frame(img))
    return ImageTk.PhotoImage(Image.fromarray(cv2.merge((r, g, b))))

class Drawing(object):
    def __init__(self, x, y, color, thickness):
        self.thickness = thickness
        self.startingX = x
        self.startingY = y
        self.color = color
        self.xCoordinates = [self.startingX]
        self.yCoordinates = [self.startingY]

class Eraser(object):
    def __init__(self, x, y):
        self.startingX = x
        self.startingY = y
        self.xCoordinates = [self.startingX]
        self.yCoordinates = [self.startingY]
        self.color = "white"
        self.thickness = 20

class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.splash = mode.loadImage("splash.png")
    def redrawAll(mode, canvas):
        font = 'Arial 26 bold'
        canvas.create_image(mode.width//2, mode.height//2, image=ImageTk.PhotoImage(mode.splash))

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)
        
class MyModalApp(ModalApp):
    def appStarted(app):
        app.gameMode = GameMode()
        app.splashScreenMode = SplashScreenMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)

class HelpMode(Mode):
    def redrawAll(mode, canvas):
            font = 'Arial 26 bold'
            canvas.create_text(mode.width/2, 150,
                               text='This is the help screen!',
                               font=font)
            canvas.create_text(mode.width/2, 250,
                               text='(Insert helpful message here)',
                               font=font)
            canvas.create_text(mode.width/2, 350,
                               text='Press any key to return to the game!',
                               font=font)

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)
        
class GameMode(Mode):
    def appStarted(mode):
        mode.startGame()
        mode.color = "black"
        mode.thickness = 2
        mode.numberSet = {i for i in range(10)}
        mode.eraser = False
        mode.screenShotMode = False
        mode.timerDelay = 1
        mode.is_hand_hist_created = False
        mode.capture = cv2.VideoCapture(0)
        mode.tkimage = None
        mode.cx, mode.cy = None, None
        mode.drawingnow = False
        mode.juststarted = False
        mode.distanceerror = True

    def keyPressed(mode, event):
        if event.key == "Up":
            if not mode.thickness == 10:
                mode.thickness += 1  
        if event.key == "Down":
            if not mode.thickness == 1:
                mode.thickness -= 1
        if event.key in mode.numberSet:
            mode.thickness = event.key
        if event.key == "b":
            mode.color = "blue"
        if event.key == "g":
            mode.color = "green"
        if event.key == "y":
            mode.color = "yellow"
        if event.key == "p":
            mode.color = "pink"
        if event.key == "o":
            mode.color = "orange"
        if event.key == "n":
            mode.color = "brown"
        if event.key == "v":
            mode.color = "purple"
        if event.key == "r":
            mode.color = "red"
        if event.key == "w":
            mode.color = "white"
        if event.key == "Space":
            mode.color = "black"
        #if event.key == "q":
        if (event.key == 'q'):
            snapshotImage = mode.app.getSnapshot()
        elif (event.key == 's'):
            mode.app.saveSnapshot()
        if event.key == "t":
            mode.screenShotMode = True
        if event.key == "d":
            mode.screenShotMode = False
        if event.key == "Tab":
            mode.startGame()
        if event.key == "u":
            if mode.eraser == False:
                if not mode.drawingList == []:
                    mode.drawingList.pop()
        if event.key == 'z' and not mode.is_hand_hist_created:
            mode.is_hand_hist_created = True
            _, frame = mode.capture.read()
            frame = cv2.flip(frame, 1)
            mode.hand_hist = hand_histogram(frame)
        if event.key == "a":
            mode.drawingnow = True
            mode.juststarted = True
        if event.key == "d":
            mode.drawingnow = False

    def timerFired(mode):
        _, frame = mode.capture.read()
        frame = cv2.flip(frame, 1)

        if mode.is_hand_hist_created:
            fullframe = frame
            mask = cv2.imread("mask.png", 0)
            frame = cv2.bitwise_and(frame,frame,mask = mask)
            far_point = manage_image_opr(frame, mode.hand_hist, fullframe)
            if far_point == None:
                mode.cx, mode.cy = None, None
            else:
                mode.cx = far_point[0] * 1.3
                mode.cy = far_point[1] * 1.3
                mode.distanceerror = True

                if mode.juststarted:
                    newDrawing = Drawing(mode.cx, mode.cy, mode.color, mode.thickness)
                    mode.drawingList.append(newDrawing)
                    mode.juststarted = False
                elif mode.drawingnow:
                    lastIndex = mode.getLastIndex(mode.drawingList)
                    lastx = mode.drawingList[lastIndex].xCoordinates[-1]
                    lasty = mode.drawingList[lastIndex].yCoordinates[-1]
                    distance = ((mode.cx - lastx)**2+(mode.cy-lasty)**2)**0.5
                    if distance < 100:
                        mode.distanceerror = False
                        mode.drawingList[lastIndex].xCoordinates.append(mode.cx)
                        mode.drawingList[lastIndex].yCoordinates.append(mode.cy)
                        mode.drawingList[lastIndex].color = mode.color
                        mode.drawingList[lastIndex].thickness = mode.thickness
            frame = fullframe
        else:
            frame = draw_rect(frame)

        mode.tkimage = cvtotk(frame)
            
    def getLastIndex(mode, lst):
        if len(lst) == 1:
            return 0
        else:
            return len(lst) - 1

    def startGame(mode):
        mode.drawingList = []

    def mousePressed(mode, event):
        if mode.eraser == False:
            newDrawing = Drawing(event.x, event.y, mode.color, mode.thickness)
            mode.drawingList.append(newDrawing)

    def mouseDragged(mode, event):
        if mode.eraser == False:
            lastIndex = mode.getLastIndex(mode.drawingList)
            mode.drawingList[lastIndex].xCoordinates.append(event.x)
            mode.drawingList[lastIndex].yCoordinates.append(event.y)

    def redrawAll(mode, canvas):
        if not mode.tkimage == None:
            canvas.create_image(mode.width//2, mode.height//2, image=mode.tkimage)
        font = 'Arial 20 bold'
        if mode.screenShotMode == False:
            canvas.create_text(mode.width//2, 30,
                               text=f"Current Color: {mode.color}",
                               font=font,
                               fill='white')
            canvas.create_text(mode.width//2, 50,
                               text=f"Current thickness: {mode.thickness}",
                               font=font,
                               fill='white')
            canvas.create_text(mode.width//2, 70,
                               text="Drawing Mode!",
                               font=font,
                               fill='white')
        mode.drawLines(canvas)
        if mode.cx != None and mode.cy != None:
            if mode.distanceerror:
                canvas.create_oval(mode.cx-10, mode.cy-10, mode.cx + 10, mode.cy + 10, fill="red")
                lastIndex = mode.getLastIndex(mode.drawingList)
                if len(mode.drawingList) > 0:
                    lastx = mode.drawingList[lastIndex].xCoordinates[-1]
                    lasty = mode.drawingList[lastIndex].yCoordinates[-1]
                    canvas.create_oval(lastx-10, lasty-10, lastx + 10, lasty + 10, fill="red")
            else:
                canvas.create_oval(mode.cx-10, mode.cy-10, mode.cx + 10, mode.cy + 10, fill="green")

    def drawLines(mode, canvas):
        for drawing in mode.drawingList:
            for i in range(len(drawing.xCoordinates)-1):
                canvas.create_line(drawing.xCoordinates[i],
                                   drawing.yCoordinates[i],
                                   drawing.xCoordinates[i+1],
                                   drawing.yCoordinates[i+1],
                                   fill=drawing.color,
                                   width=drawing.thickness,
                                   smooth=1)
 

app = MyModalApp(width=832, height=624)
               
