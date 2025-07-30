import cv2
from ultralytics import YOLO
from playsound import playsound
from ast import literal_eval
import time
from datetime import datetime
from threading import Thread
import sys

md_path = './v8_models/yolov8x.pt'
device = 'cpu'
model = YOLO(md_path,device)
fl = open('classes.txt', 'r')
names = fl.read().split('\n')
fl.close()
names.pop()
#print(names)
#print(len(names))
ALARM = None

def getVid(cam, danger_zone, s_play):
    if cam == '0': cam =0
    cap = cv2.VideoCapture(cam)
    while True:
        try:
            st, frm = cap.read()
            img = doYolo(frm, danger_zone, s_play)
            cv2.imshow('Name',img)
            if cv2.waitKey(1) == 27:
                break
        except Exception as err:
            print(err)
            cap.release()
            cap = cv2.VideoCapture(cam)

def doYolo(pic, danger_zone, play_sound):
    res = model.predict(pic, stream=True)
    drawLine(pic, danger_zone)
    #result here
    boxes=[]
    labels=[]
    prob = []
    cars = 0
    person = 0
    result = pic
    for r in res:
        if len(r) >0:
            # r =r.tolist()
            print(r)
            x1,y1,x2,y2, p2, cl = r
            box = [x1,y1,x2,y2]
            boxes.append(box)
            prob.append(p2)
            labels.append(names[int(cl)])
            if (names[int(cl)] =='person') or (names[int(cl)] =='car') or (names[int(cl)] =='bus') or (names[int(cl)] =='truck') or (names[int(cl)] =='cow'):
                if names[int(cl)] =='person':
                    person += 1
                else:
                    cars += 1
            if len(boxes) > 0:
                result = drawBox(pic, boxes,labels, prob, cars, person,danger_zone,play_sound)
        else:
            story = 'No Car or Person Present'
            result =cv2.putText(pic, story  ,(10,30),cv2.FONT_HERSHEY_PLAIN,0.5,(255,255,255),1)         
    return result    

def drawBox(img, boxes, labels, prob, cars, persons,danger_zone, play_sound):
    try:
        for box, lb in zip(boxes, labels):
            c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            story = 'Cars = ' + str(cars) + ', Persons = ' + str(persons)
            paint = (0,255,0)          
            if lb == 'person' or lb == 'car' or lb == 'bus' or lb == 'truck' or lb == 'cow':
                #print ('x1=', int(box[0]), 'y1=', int(box[1]))
                paint = checkDanger(box, danger_zone, img, play_sound, story)
                #print ('paint= ',paint)
            if lb == 'train' or lb == 'aeroplane':
                lb = 'object'
            img2 = cv2.rectangle(img,c1,c2,paint,2)
            img2 =cv2.putText(img2, lb,(int(box[0]),int(box[1])-7),cv2.FONT_HERSHEY_PLAIN,0.7,(255,255,255),1)
            img2 =cv2.putText(img2, story  ,(10,30),cv2.FONT_HERSHEY_PLAIN,0.7,(255,255,255),1)               
        return img2
    except:
        return img

def drawLine(obj, v1):
    #print(m2)
    pt1 = literal_eval(v1[0])
    pt2 = literal_eval(v1[1])
    cv2.rectangle(obj, pt1,pt2,(0,0,255),1)
    

#check danger zone
def checkDanger(box, dangerZ, pic, play_sound, story):
    #Get the object boudraries
    c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    x1_pers,y1_pers,x2_pers,y2_pers=box
    x1_pers = int(x1_pers)
    y1_pers = int(y1_pers)
    x2_pers = int(x2_pers)
    y2_pers = int(y2_pers)
    #print(dangerZ)
    # get the danger zone
    pt1 = literal_eval(dangerZ[0])
    pt2 = literal_eval(dangerZ[1])
    dx1 = min(pt1[0],pt2[0])
    dx2 = max(pt1[0], pt2[0])
    dy1 = min(pt1[1],pt2[1])
    dy2 = max(pt1[1],pt2[1])
    
    if ((x1_pers in range(dx1, dx2) or x2_pers in range(dx1, dx2)) and (y1_pers in range(dy1,dy2) or y2_pers in range(dy1, dy2))) or ((dx1 in range(x1_pers, x2_pers) or dx2 in range(x1_pers, x2_pers)) and (dy1 in range(y1_pers,y2_pers) or dy2 in range(y1_pers, y2_pers))):
            fn = str(time.time())
            pic2 = pic.copy()
            fn = 'static/' +fn.replace('.','') + '.jpg'
            img2 = cv2.rectangle(pic2,c1,c2,(0,0,255),2)
            cv2.imwrite(fn, img2)
            #print('inside') 
            t1 = Thread(target=report, args=(str(datetime.now()),fn, story,))
            t1.start()
            if 'enable' in play_sound:
                #sounder()
                ts = Thread(target=sounder)
                ts.start()
            return (0,0,255)
    return (0,255,0)

def report(dt, fl, msg):
    f = open('report.txt','a+')
    pp = dt+', '+fl+', '+msg +'\n'
    f.write(pp)
    f.close()
    print('Report Updated!')

def sounder():
    global ALARM
    playsound('sound/classic.wav') 
    ALARM = True
    #print('sound played')

if __name__=='__main__':
    args = sys.argv
    print(args)
    cm = args[1]
    dg = args[2]
    sd = args[3]
    fl = open(dg,'r')
    p=fl.read()
    fl.close()
    print('Danger zone extracted!')
    p2 = p.split('\n')
    getVid(cm,p2,sd) 
