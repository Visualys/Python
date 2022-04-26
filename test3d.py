from tkinter import *
import math

win = Tk()
win.geometry("510x510") #set hight and width of window form  
win.title("Form1")

c = Canvas(win, width=500, height=500, background='#fff', borderwidth=0)
#c.place(x=5, y=5, anchor="nw")
c.place(relx=.5, rely=.5, anchor="c")

def rotateX(p,angle):
  rad = angle * 0.0174532925166667
  c = math.cos(rad)
  s = math.sin(rad)
  y = p[1] * c - p[2] * s
  z = p[1] * s + p[2] * c
  p[1] = y
  p[2] = z

def rotateY(p,angle):
  rad = angle * 0.0174532925166667
  c = math.cos(rad)
  s = math.sin(rad)
  z = p[2] * c - p[0] * s
  x = p[2] * s + p[0] * c
  p[0] = x
  p[2] = z

def rotateZ(p,angle):
  rad = angle * 0.0174532925166667
  c = math.cos(rad)
  s = math.sin(rad)
  x = p[0] * c - p[1] * s
  y = p[0] * s + p[1] * c
  p[0] = x
  p[1] = y

def project(p,viewWidth,viewHeight,FOV,viewDistance):
  Factor = FOV / (viewDistance + p[2])
  x = p[0] * Factor + viewWidth / 2
  y = p[1] * Factor + viewHeight / 2
  p[0] = x
  p[1] = y

face=[[-1,-1,0],[1,-1,0],[0.5,0,0],[1,1,0],[-1,1,0]]
poly1=0
poly2=0
def draw(ang):
    global poly1, poly2
    face2=[]
    for n in range(0,len(face)):
        p = face[n].copy()
        rotateX(p,ang/4)
        rotateY(p,ang)
        project(p,500,500,720,6)
        face2.extend([p[0],p[1]])
    if ang==0:    
        poly1 = c.create_polygon(face2, outline='#aaa', fill='', width=1.5)
        poly2 = c.create_polygon(face2, outline='#333', fill='#568', width=1,activefill='#e68')
    else:
        c.coords(poly1,face2)    
        c.coords(poly2,face2)    
    #c.update
    win.after(30, draw,ang+2)
    
draw(0)    



mainloop()  
