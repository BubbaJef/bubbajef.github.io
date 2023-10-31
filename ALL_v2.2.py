from tkinter import *
from tkinter import font
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import math
import math
from time import time

#make constants
WIDTH = 400
HEIGHT = 500

#mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

MYHAND = .07 #set scale of tested hand

#Make constants
DEBUG = False
FIND = False
ID = True
CONFIRM = True

#Confirm og values
global Read
global HasRead
global String
global ReadCount
global NewRead
Read = ""
HasRead = ""
String = ""
ReadCount = 0
NewRead = 0
markTime = time()


# Euclidean distance
def compute_distance(landmark1, landmark2):
    return ((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2)**0.5

#initiate camera
vid = cv2.VideoCapture(0)

vid.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

app = Tk()

app.bind('<Escape>', lambda e: app.quit())

label_widget = Label(app)
label_widget.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=NW)

customFont_2 = font.Font(family = "Arial",size = 25)
# Status bar
status_bar1 = Label(app, bd=1, relief=SUNKEN, anchor=W, height=2, font=customFont_2)
status_bar1.grid(row=2, column=0, columnspan=2, sticky=W+E)

# Vertical Status bar (Text widget for live terminal output)
vertical_status_bar = Text(app, wrap=WORD, height=50, width=30)
vertical_status_bar.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky=N)
# Function to write text to the vertical status bar
def write_to_status_bar(text):
    vertical_status_bar.insert(END, text + '\n')
    vertical_status_bar.see(END)  # Auto-scroll to the end of the text

# Redirect stdout to the vertical status bar
import sys
sys.stdout.write = write_to_status_bar

customFont = font.Font(family = "Arial",size = 100)

#status bar
confirmed_letter = Text(app, bd=1, relief=SUNKEN, height=1, width=2, font=customFont)
confirmed_letter.grid(row=0, column=1, padx=10, pady=10, sticky=NE) 
confirmed_letter.tag_configure("center", justify='center')


def open_camera():
    _, frame = vid.read()

    #Read Current Time
    currentTime = time()
    
    global Read, HasRead, String, ReadCount, NewRead

    frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

    results = hands.process(frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            '''Acess Points'''
            Tt = hand_landmarks.landmark[4] #thumb tip
            Pt = hand_landmarks.landmark[20] #pinky tip
            H0 = hand_landmarks.landmark[0] #Hand 0 (wrist)
            Mt = hand_landmarks.landmark[12] #middle tip
            Hi = hand_landmarks.landmark[5] #index start
            Ps = hand_landmarks.landmark[17] #pinky start
            Rt = hand_landmarks.landmark[16] #Ring tip
            It = hand_landmarks.landmark[8] #Index tip
            Ts = hand_landmarks.landmark[2] #Thumb start
            In = hand_landmarks.landmark[6] #Index Nuckle
            H1 = hand_landmarks.landmark[1] #Hand 1 (Thumb Pad)
            
            z_dist = -10000000*H0.z #set z distance constant
            
            z_scale = round(11/z_dist,2)
            
            #set hand scale
            scale = round((round(compute_distance(H0, Hi)*(z_scale), 2)) * (round(compute_distance(Ps, Hi)*(z_scale), 2)),2)
            

            comp = (round(scale/MYHAND,4))
    
            '''Get Distances'''
            PTdist = abs(round(compute_distance(Pt, Tt)*(z_scale), 2)) #Pinky-Thumb
            HPdist = abs(round(compute_distance(H0, Pt)*(z_scale), 2)) #Wrist-Pinky tip
            HTdist = abs(round(compute_distance(H0, Tt)*(z_scale), 2)) #Wrist-Thumb tip
            HMdist = abs(round(compute_distance(H0, Mt)*(z_scale), 2)) #Wrist-Middle tip
            HRdist = abs(round(compute_distance(H0, Rt)*(z_scale), 2)) #Wrist-Ring tip
            HIdist = abs(round(compute_distance(H0, It)*(z_scale), 2)) #Wrist-Index tip
            HTs_dist = abs(round(compute_distance(H0, Ts)*(z_scale), 2)) #Wrist-Thumb start
            TIdist = abs(round(compute_distance(Ts, It)*(z_scale), 2)) #Thumb start - Index tip
            TtPs_dist = abs(round(compute_distance(Tt, Ps)*(z_scale), 2)) #Thumb tip - Pinky start
            IMdist = abs(round(compute_distance(It, Mt)*(z_scale), 2)) #Middle tip - Index tip
            TRdist = abs(round(compute_distance(Tt, Rt)*(z_scale), 2)) #Thumb tip to Ring Tip
            TtIsdist = abs(round(compute_distance(Tt, Hi)*(z_scale), 2)) #Thumb tip - Index start
            
            ''' IDENTIFY HANDS '''
            if (ID):
                if ((Ps.y > H1.y) and (It.y < H0.y)):
                    if ((Mt.x < In.x) and (Rt.x < In.x) and (Pt.x < In.x) and (It.x > In.x)):
                        if (Tt.y < It.y):
                            Read = "G"
                        else:
                            Read = "P"
                    elif ((Mt.x > In.x) and (Rt.x < In.x) and (Pt.x < In.x) and (It.x > In.x)):
                        Read = "H"
                    
                elif ((Mt.y > Hi.y) and (Rt.y > Hi.y) and (Pt.y > Hi.y) and (It.y < Hi.y) and (It.y < H0.y)):
                    if (Tt.x > Hi.x):
                        if (It.y > In.y):
                            Read = "X"
                        elif (Tt.y > Rt.y):
                            Read = "D"
                        elif (Tt.y < Rt.y):
                            Read = "Z"
                    elif ((Tt.x < Hi.x)  and (comp*TtIsdist > 0.7)):
                        Read = "L"
                    else:
                        "-"
                    
                elif ((Mt.y < In.y) and (Rt.y < In.y) and (Pt.y > In.y) and (It.y < In.y)\
                      and (Tt.x > Mt.x) and (It.y < H0.y)):
                    Read = "W"

                elif ((Mt.y < In.y) and (Rt.y < In.y) and (Pt.y < In.y) and (It.y > In.y) \
                      and (Tt.y > Hi.y) and (It.y < H0.y)):
                     Read = "F"
                     
                elif ((Mt.y < In.y) and (Rt.y < In.y) and (Pt.y < In.y) and (It.y < In.y) \
                      and (Tt.y > Hi.y) and (Tt.x > Mt.x)):
                     Read = "B"

                elif ((Mt.y > In.y) and (Rt.y > In.y) and (Pt.y < In.y) and (It.y > In.y) and (It.y < H0.y)):
                    if ((Tt.y > In.y) and (Tt.x > Hi.x) and (Tt.x < Rt.x)):
                        Read = "J"
                    elif ((Tt.y > In.y) and (Tt.x < Hi.x)):
                        Read = "I"
                    elif ((comp*TtPs_dist > 0.2) and (Tt.y < In.y) and (comp*PTdist) > (.4)):
                        Read = "Y"                  
                    
                elif((It.y < Hi.y) and (Pt.y > Ps.y) and (It.y < H0.y)):
                    if ((Mt.y < Hi.y) and (Rt.y > Ps.y)): 
                        if (It.x > Mt.x):
                            Read = "R"
                        elif (comp*IMdist < 0.1):
                            Read = "U"
                        elif ((Tt.x > It.x) and (Tt.y < Hi.y)):
                            Read = "K"
                        elif (comp*IMdist > 0.1):
                            Read = "V"
                            
                elif((Pt.y > Hi.y) and (Rt.y > Hi.y) and (Mt.y > Hi.y) \
                    and (It.y > Hi.y) and (It.y < H0.y)):

                    if ((Tt.x > Hi.x) and (Tt.y < Rt.y)):
                        if ((Tt.x > Hi.x) and (Tt.x < Mt.x)):
                            if (Tt.y > In.y):
                                Read = "S"
                            elif (Tt.y < In.y):
                                Read = "T"
                        elif ((Tt.x > Mt.x) and (Tt.x < Pt.x)):
                            if (Tt.y > In.y):
                                Read = "N"
                            elif (Tt.y < In.y):
                                    Read = "M"
                    elif (Tt.y > Rt.y):
                        Read = "E"
                    elif (Tt.x < Hi.x):
                        Read = "A"

                elif((It.y > In.y) and (Tt.y > In.y) and (It.y > H0.y) and (Pt.y < In.y) and (Mt.y < In.y)):
                    Read = "Q"
                    
                elif((Pt.y > In.y) and (Rt.y > In.y) and (Mt.y > In.y) \
                    and (It.y > In.y) and (It.y < H0.y)):
                    if (comp*TRdist > 0.9):
                        Read = "C"
                    else:
                        Read = "O"
                    
                else:
                    Read = "-"                    

                print("")

            print("Read: {}".format(Read))

            if (CONFIRM):            
                if (NewRead > 10):
                    if (Read != "-"):
                        HasRead = Read
                        print("New letter!")
                        
                    NewRead = 0
                    
                    confirmed_letter.delete("1.0", END)  # Delete current content
                    confirmed_letter.insert(END, Read)   # Insert the new letter
                    confirmed_letter.tag_add("center", "1.0", "end")
                    
                if (Read == HasRead):
                    ReadCount += 1 
                    NewRead -= 1
                    
                    if (NewRead < 0):
                        NewRead = 0
                        
                else:
                    ReadCount -= 1
                    NewRead += 1

                    if (ReadCount < 0):
                        ReadCount = 0

                if ((ReadCount > 10) and (Read != "-") and ((currentTime - markTime) > 3)):
                    print("Confirm Letter: {}".format(Read))
                    
                    NewRead = 0
                    ReadCount = 0
                    String += Read
                    
    status_bar1.config(text=String)

    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    opencv_image = cv2.resize(opencv_image, (1200,700))

    captured_image = Image.fromarray(opencv_image)

    photo_image = ImageTk.PhotoImage(image=captured_image)

    label_widget.photo_image = photo_image

    label_widget.configure(image=photo_image)

    label_widget.after(10, open_camera)

button1 = Button(app, text="Open Camera", command=open_camera)
button1.grid(row=1, column=0, columnspan=2, pady=10, sticky=W)

app.mainloop()
