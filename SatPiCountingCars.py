# -*- coding: utf-8 -*-

import cv2
import picamera
import requests #to connect to the web API
import time
import datetime

print(chr(27)+"[2J")

print ("---------------------------SAT-PI--------------------------")
print ("Sistema de Analisis de Transito con Procesamiento de Imagen")
print ("-----------------------------------------------------------")
print ("")
print ("-----------------------------------------------------------")
print ("Por:")
print ("              Maria Sanchez y Maria Fernandez")
print ("-----------------------------------------------------------")

#Cutting-Settings
X_P1=210
X_P2=260
Y_P1=190
Y_P2=207 #Sensor 1 Settings

X_P1b=280
X_P2b=330
Y_P1b=190
Y_P2b=207 #Sensor 2 Settings

X_P1c=200
X_P2c=250
Y_P1c=212
Y_P2c=229 #Sensor 3 Settings

X_P1d=270
X_P2d=320
Y_P1d=212
Y_P2d=229 #Sensor 4 Settings


#Sensors initialization
SENSOR1= False
SENSOR2= False
SENSOR3= False
SENSOR4= False

#Processing Characteristics
THRESHOLD_SENSITIVITY = 20
BLUR_SIZE = 10

#Video Settings
video_src = 'dataset/video3.mp4'
cap = cv2.VideoCapture(video_src)

#Counting Variables initialization
count1=0
count2=0
total=0
first_image = True

start_time = datetime.datetime.now() #init time

print("")
print ("Inicio de conteo.............")
print ("-----------------------------------------------------------")
print ("")

while True:
    #Reading file--------------------------
    ret, img = cap.read()  #ret ->bool which indicates if we ended the file
    
    if (type(img) == type(None)):
        break
    
    img1= img

    #Gray image convertion------------------------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    

    #Drawing Regions Of Interest--------------------------------
    cv2.rectangle(img1,(X_P1,Y_P1),(X_P2,Y_P2),(0,0,255),2)
    cv2.rectangle(img1,(X_P1b,Y_P1b),(X_P2b,Y_P2b),(0,0,255),2)
    cv2.rectangle(img1,(X_P1c,Y_P1c),(X_P2c,Y_P2c),(0,0,255),2)
    cv2.rectangle(img1,(X_P1d,Y_P1d),(X_P2d,Y_P2d),(0,0,255),2)  
    

    #Counting with sensors-----------------------------------------

    #Cutting Regions Of Interest-----------------------------------
    sensor_1= gray[Y_P1:Y_P2, X_P1:X_P2]
    sensor_2= gray[Y_P1b:Y_P2b, X_P1b:X_P2b]
    sensor_3= gray[Y_P1c:Y_P2c, X_P1c:X_P2c]
    sensor_4= gray[Y_P1d:Y_P2d, X_P1d:X_P2d]

    	
    if first_image:
        # first number indicates previous, second one the sensor
        gray1image1 = sensor_1 
        gray1image2 = sensor_2
        gray1image3 = sensor_3
        gray1image4 = sensor_4
        first_image = False
    else:
        gray2image1 = sensor_1
        gray2image2 = sensor_2
        gray2image3 = sensor_3
        gray2image4 = sensor_4
		
	#------------------Counting cars, sensors 1 and 3---------------

        #SENSOR 1
        # Difference between images-----------------------------------
        differenceimage = cv2.absdiff(gray1image1, gray2image1)
        # Difference blured------------------------------------------
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))#Blursize es la dimension de la matriz con la que se hara la conv.
        # Threshold -------------------------------------------------        
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)

        # Counting white pixels 
        indicator = cv2.countNonZero(thresholdimage)
        
        if indicator>620:
            if SENSOR1:
                SENSOR1=False
            else:
                SENSOR1=True
                if SENSOR3:
                    count1+=1
                    #print("Lado izquierdo -> " + str(count1))

        # save gray2image1 to gray1image1 ready for next
        gray1image1 = gray2image1

 	#SENSOR 3
        differenceimage = cv2.absdiff(gray1image3, gray2image3)
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
        
        indicator = cv2.countNonZero(thresholdimage)
        if indicator>620:
            if SENSOR3:
                SENSOR3=False
            else:
                SENSOR3=True
        # save grayimage2 to grayimage1 ready for next image2
        gray1image3 = gray2image3


        #------------------Counting cars, sensors 1 and 3---------------
        #SENSOR 4
        differenceimage = cv2.absdiff(gray1image2, gray2image2)
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)
        indicator = cv2.countNonZero(thresholdimage)
        if indicator>582: 
            if SENSOR4:
                SENSOR4=False
            else:
                SENSOR4=True
                if SENSOR2:
                    count2+=1
                    #print("Lado derecho -> " + str(count2))
                    
        # save grayimage2 to grayimage1 ready for next image2
        gray1image2 = gray2image2
                              
								
        #SENSOR 2
        differenceimage = cv2.absdiff(gray1image4, gray2image4)
        differenceimage = cv2.blur(differenceimage,(BLUR_SIZE,BLUR_SIZE))
        retval, thresholdimage = cv2.threshold(differenceimage,THRESHOLD_SENSITIVITY,255,cv2.THRESH_BINARY)

        indicator = cv2.countNonZero(thresholdimage)
        if indicator>582:
            if SENSOR2:
                SENSOR2=False
            else:
                SENSOR2=True

        # save grayimage2 to grayimage1 ready for next image2
        gray1image4 = gray2image4
       
        # Showing video with drawn sensores-----------------------------
        cv2.imshow('video2', img1)
       # cv2.imshow('Difference image', differenceimage)
        
        
        if cv2.waitKey(33) == 27:
            break
total= count1+count2

finish_time=  datetime.datetime.now()
cv2.destroyAllWindows()

#print ("Found " + str(count1) + " car(s)")
#print ("Found " + str(count2) + " car(s)")
print ("")
print ("-----------------------------------------------------------")
print ("Fin de conteo.........")
print ("-----------------------------------------------------------")
print ("Total carros encontrados: " + str(total))
print ("-----------------------------------------------------------")

# Sending data to DataBase
print ("Enviando datos a Base de Datos")
print ("-----------------------------------------------------------")

process={"$id":"1", "id_proc":"NULL", "count":total, "start_date":start_time,"end_date":finish_time, "id_location":"l2"}
r= requests.post('http://192.168.137.1:54603/api/Processes',process)

print("Datos enviados!")
cv2.waitKey(0)
