from picamera.array import PiRGBArray
from picamera import PiCamera
from tentacle_pi.TSL2561 import TSL2561
import time
import datetime
import numpy as np
import requests
import cv2


start_time = datetime.datetime.now() #init time
process={"id_process":"NULL","start_date":start_time,"id_location":"l1","count":77,"end_date":start_time}
r= requests.post('http://satpia.azurewebsites.net/api/Processes',process)

#parametros sensor de luz
tsl = TSL2561(0x39,"/dev/i2c-1")
tsl.enable_autogain()
tsl.set_time(0x00)

#DEFINIENDO TODOS LOS PARAMETROS
#------------------------------
#PARAMETROS DE REGION

#Cutting Settings
X_P1=220
X_P2=530
Y_P1=130
Y_P2=290

# PARAMETROS DE CAMARA
camera = PiCamera()
camera.rotation=180
camera.resolution = (640, 480)
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup

time.sleep(0.1)

#PARAMETROS DE CASCADE
cascade_src = 'cascade2.xml'
car_cascade = cv2.CascadeClassifier(cascade_src)

#PARAMETROS DE RASTREO
# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0,255,(100,3))

#Parametros de K Means
criteria= (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10,1.0)
#-----------------------------------
#HASTA AQUI DEFINICION DE PARAMETROS


#DEFINICION DE VARIABLES
arr_p0=[]
arr_p1=[]
arr_good_new=[]
arr_good_old=[]
frames_count=1
frames_count_limit=4
count=0
processes=[]


first_car= True

while(tsl.lux()<10000):
    #print ('no detecto')
    continue

# Take first frame and find corners in it
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    old_frame=frame.array
    #cv2.imshow("Frame", old_frame)
    #Convierto a gris
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    #Corto el frame
    old_region=old_gray[Y_P1:Y_P2, X_P1:X_P2]
    
    
    #Deteccion
    car= car_cascade.detectMultiScale(old_region, 1.09, 3)

    
    if len(car)!=0:
        for (x,y,w,h) in car:
            first_car= False        
            #print ("encontre el primer carro")
            focused_area= old_region[y:y+h, x: x+w]
            #cv2.imshow('focused_area',focused_area)
            #cv2.rectangle(old_frame,(x+X_P1,y+Y_P1),(x+w+X_P1,y+h+Y_P1),(0,0,255),2)
            p0= cv2.goodFeaturesToTrack(focused_area, mask= None, **feature_params)
        
            for a,b in enumerate(p0):
                for c,d in enumerate(p0[a]):
                    for e,f in enumerate(p0[a][c]):
                        if (e==0):
                            p0[a][c][e]=f+x+X_P1
                        else:
                            p0[a][c][e]=f+y+Y_P1
            #K means
            #print("valor p0 despues:1 " + str(p0))
            #p0=np.int32(p0)
            ret, label, center= cv2.kmeans(p0,1,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
            p0=[]
            p0.append(center)
           #print("valor p0 centro " + str(p0))
            p0= np.float32(p0)
            #print("valor p0 centro despues" + str(p0))
            arr_p0.append(p0)
            start_time = datetime.datetime.now() #init time
            process={"id_process":"NULL","start_date":start_time,"id_location":"l1","count":0,"end_date":0}
            processes.append(process)

    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break

    if(first_car!=True):
        break
    
    while(tsl.lux()<10000):
        #print ('no detecto')
        continue

#print("sali del while")
mask = np.zeros_like(old_frame)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
# grab the raw NumPy array representing the image, then initialize the timestamp
# and occupied/unoccupied text
    img = frame.array
    frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #Corto el frame
    old_region=frame_gray[Y_P1:Y_P2, X_P1:X_P2]
    
    if (frames_count==frames_count_limit):
        frames_count=1
        #Deteccion
        car= car_cascade.detectMultiScale(old_region, 1.09, 3)

        if len(car)!=0:
            for (x,y,w,h) in car:
                #print ("encontre un carro")
                cv2.rectangle(img,(x+X_P1,y+Y_P1),(x+w+X_P1,y+h+Y_P1),(0,0,255),2)
                #Verificando si los puntos de arr_p0 pertenecen al rectangulo
                bandera=True
                lim1X= x+X_P1
                lim2X= x+w+X_P1
                lim1Y= y+Y_P1
                lim2Y= y+h+Y_P1
                for i in arr_p0:
                    for j in i:
                        a=j[0]
                        #print ("JOTA: " + str(j))
                        if((a[0]>=lim1X and a[0]<=lim2X)
                           or(a[0]-10>=lim1X and a[0]-10<=lim2X)
                           or(a[0]+10>=lim1X and a[0]+10<=lim2X)):
                            if((a[1]>=lim1Y and a[1]<=lim2Y)
                               or(a[1]-10>=lim1Y and a[1]-10<=lim2Y)
                               or(a[1]+10>=lim1Y and a[1]+10<=lim2Y)):
                               # print('ESTABAAAAAAAAAAAAAA')
                                bandera=False
                if (bandera==True):
                    focused_area= old_region[y:y+h, x: x+w]
                    p0= cv2.goodFeaturesToTrack(focused_area, mask= None, **feature_params)
                    for a,b in enumerate(p0):
                        for c,d in enumerate(p0[a]):
                            for e,f in enumerate(p0[a][c]):
                                if (e==0):
                                    p0[a][c][e]=f+x+X_P1
                                else:
                                    p0[a][c][e]=f+y+Y_P1

                    #print("valor p0 despues:1 " + str(p0))
                    ret, label, center= cv2.kmeans(p0,1,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
                    p0=[]
                    p0.append(center)
                    #print("valor p0 centro " + str(p0))
                    p0= np.float32(p0)
                    #print("valor p0 centro despues" + str(p0))
                    arr_p0.append(p0)

                    start_time = datetime.datetime.now() #init time
                    process={"id_process":"NULL","start_date":start_time,"id_location":"l1","count":0,"end_date":0}
                    processes.append(process)
                #print ('p0' + str(p0))

            #print ('arr_p0' + str(arr_p0))

    #print ('arr_p0 antes de calculo of' + str(arr_p0))
    arr_p1=[]
    # calculate optical flow
    st=[]
    for i in arr_p0:
        p1, st1, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, i, None, **lk_params)
        st.append(st1)
        arr_p1.append(p1)
    arr_good_new=[]
    arr_good_old=[]
   # print ('st'+str(st))
    #print ('arr_p0 despues de calculo of' + str(arr_p0))
    for i,p in enumerate(arr_p0):
        #print ('valor de p' + str(p))
        good_old=p[st[i]==1]
        arr_good_old.append(good_old)
    for i,p in enumerate(arr_p1):
        good_new=p[st[i]==1]
        arr_good_new.append(good_new)
        
    indexes=[]
    for i,n in enumerate(arr_good_new):
        if (np.all(n)==None):
            indexes.append(i)
    for i in range(len(indexes)-1,-1,-1):
        arr_p0.pop(indexes[i])
        arr_good_new.pop(indexes[i])
        finish_time=  datetime.datetime.now()
        processes[indexes[i]]['count']=1
        processes[indexes[i]]['end_date']=finish_time
        #print (datetime.datetime.now())
        r= requests.post('http://satpia.azurewebsites.net/api/Processes',processes[indexes[i]])
        #print (datetime.datetime.now())
        processes.pop(indexes[i])
        count+=1
        
    #print ('arr_p0'+str(arr_p0))
    
    #print ('arr_p0 despues' + str(arr_p0))
    # draw the tracks
    for j,n in enumerate(arr_good_new):
        for i,(new,old) in enumerate(zip(arr_good_new[j],arr_good_old[j])):
            a,b = new.ravel()
            c,d = old.ravel()
            #mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            cv2.circle(img,(a,b),10,color[i].tolist(),-1)

    #img3 = cv2.add(img,mask)
    
    frames_count+=1
        # Now update the previous frame and previous points
    old_gray = frame_gray
    
    for i,p in enumerate(arr_good_new):
        arr_p0[i] = arr_good_new[i].reshape(-1,1,2)
    #print ('arr_p0 antes de reshape' + str(arr_p0))
    indexes=[]
    for i,p in enumerate(arr_p0):
        if(len(p)==0):
            indexes.append(i)
    for i in range(len(indexes)-1,-1,-1):
        arr_p0.pop(indexes[i])
        finish_time=  datetime.datetime.now()
        processes[indexes[i]]['count']=1
        processes[indexes[i]]['end_date']=finish_time
        #print (datetime.datetime.now())
        r= requests.post('http://satpia.azurewebsites.net/api/Processes',processes[indexes[i]])
        #print (datetime.datetime.now())
        processes.pop(indexes[i])
        count+=1
        #print('KLK')
    #print ('arr_p0 DESPUES DE RESHAPE'+str(arr_p0))
    
    #print ('CONTEO '+str(count))

    
    #cv2.imshow('frame',img)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break
    while(tsl.lux()<10000):
        #print ('no detecto')
        continue
rawCapture.truncate(0)
cv2.destroyAllWindows()


