import tkinter
from PIL import ImageTk,Image
import cv2
import face_recognition
from threading import Thread
from time import time
from tkinter import messagebox
import numpy as np
from multiprocessing import Process, Queue
import os

flag = False
person = 0
class mainAppication():
    def __init__(self):
        super().__init__()
        self.appName = "Image Processing"
        self.chooseValue = "Choose your Camera"
        self.window = tkinter.Tk()
        self.window.title(self.appName)
        self.optionList= ["Choose your Camera"]
        self.camera = count_camera().numberOfCamera()
        self.label = tkinter.Label(self.window, text = "Number of person= 0")
        self.label.grid(row = 0, column = 1)
        self.frame = tkinter.Frame(self.window, width = 25)
        self.frame.grid(row = 1)
        self.btnStart = tkinter.Button(self.frame, text = "START", width = 25, command= self.buttonStartEvent)
        self.btnStart.pack()
        self.btnStop = tkinter.Button(self.frame, text = "STOP", width = 25, state = 'disabled', command= self.buttonStopEvent)
        self.btnStop.pack()
        self.canvas = tkinter.Canvas(self.window, bg = 'black')
        self.canvas.grid(row = 1, column = 1)
        for i in range(self.camera):
            self.optionList.append("Camera "+str(1 + i))
        self.variable = tkinter.StringVar(self.window)
        self.variable.set(self.optionList[0])
        self.opt = tkinter.OptionMenu(self.window, self.variable, *self.optionList)
        self.opt.config(width = 25)
        self.opt.grid(row = 0)
        self.variable.trace("w",self.callbackOptionList)
        self.window.protocol("WM_DELETE_WINDOW", self.exit_callback)
        self.window.mainloop()
        
    def callbackOptionList(self, *args):
        self.chooseValue = self.variable.get()
    def buttonStartEvent(self):
        global flag
        person = 0;
        flag = True
        prevTime = time()
        known_encoding = []
        if self.chooseValue != "Choose your Camera":
            choosenChamera = (int)(self.chooseValue[-1]) - 1
            self.btnStop['state'] = 'normal'
            self.btnStart['state'] = 'disabled'
            self.capture = cv2.VideoCapture(choosenChamera)
            self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.canvas.config(width = self.width, height = self.height, bg = 'black')
            self.frameQueue = Queue()
            self.flagQueue = Queue()
            self.checkFrame = Process(target=display_number_of_person, args=(self.frameQueue,self.flagQueue))
            self.checkFrame.start()
            self.showframe = Thread(target=showFrames, args=[self.capture,self.canvas,self.window,self.label, self.frameQueue, self.flagQueue])
            self.showframe.start()
        else:
            messagebox.showinfo("Alert","Choose any webcam!!!")

    def buttonStopEvent(self):
        global flag
        flag = False
        self.btnStop['state'] = 'disabled'
        self.btnStart['state'] = 'normal'

    def exit_callback(self):
        global flag
        if flag:
            messagebox.showwarning("Warning", "Stop the webcam first!!!")
        else:
            self.window.destroy()   


def showFrames(capture, canvas, window, label, frameQueue, flagQueue):
    global flag,person
    width = (int)(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = (int)(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    prevtime = 0;
    while flag:
        coloredFrame = count_camera().getFrame(capture)
        rgbframe = cv2.cvtColor(coloredFrame,cv2.COLOR_BGR2RGB)
        frame = cv2.cvtColor(rgbframe,cv2.COLOR_BGR2GRAY)
        face_location = face_recognition.face_locations(frame)
        if len(face_location) != 0 and (time() - prevtime) > 5:
            frameQueue.put(rgbframe)
            flagQueue.put(1);
            prevtime = time();
        for x,y,h,w in face_location:
            cv2.rectangle(coloredFrame,(w,x),(y,h),(255,255,255),2)
        photo =  ImageTk.PhotoImage(image= Image.fromarray(coloredFrame))
        canvas.create_image(0, 0, image = photo, anchor = 'nw')
    capture.release()
    flagQueue.put(-1);
    photo =  ImageTk.PhotoImage(image= Image.fromarray(np.zeros((height,width,3),np.uint8)))
    canvas.create_image(0, 0, image = photo, anchor = 'nw')
    return


def check_match(frameQueue, flagQueue, label, window):
    known_encoding = []
    person = 0
    while 1:
        if(flagQueue.get() == -1): break
        unknown_encoding = face_recognition.face_encodings(frameQueue.get())
        for face in unknown_encoding:
            result = face_recognition.compare_faces(known_encoding, face)
            if not result:
                person += 1
                print(f"persion {person}")
                label.config(text = "Number of person= " + str(person))
            for i in result:
                if not i:
                    person += 1
                    print(f"persion {person}")
                    label.config(text = "Number of person= " + str(person))
        if len(unknown_encoding) != 0:
            known_encoding = unknown_encoding
    print("process finished")
    os._exit(0)

    

def display_number_of_person(frameQueue,flagQueue):
    window = tkinter.Tk()
    label = tkinter.Label(window, text = f"Number of person= 0", font=("Helvetica", 16), padx=20, pady=20)
    label.pack()
    checkMatch = Thread(target=check_match, args=(frameQueue, flagQueue, label, window))
    checkMatch.start()
    window.mainloop()
    
    

class count_camera():
    def numberOfCamera(self):
        camera = 0;
        for i in range(5):
            capture = cv2.VideoCapture(i)
            if not capture.isOpened():
                break;
            else:
                capture.release()
                camera += 1;
        return camera
    def getFrame(self,capture):
        check, frame = capture.read()
        if check:
            return frame
        else:
            return None

if __name__ == "__main__":
    mainAppication()