# Load libraries
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import requests
# Pronounce
import googletrans
import speech_recognition as sr
import gtts
import playsound
import csv
from tempfile import NamedTemporaryFile
import shutil


counter = 0
recognizer = sr.Recognizer()
translator = googletrans.Translator()
input_lang = 'fr-FR'
output_lang = 'en'
# Chemin vers notre dossier d'images
path = "Pictures"
images = [] # List of images from the folder
classNames = []# list of images' names
# Grab the list of images in the folder
myList = os.listdir(path)
# print(myList)
# Read images fro the folder
for cl in myList:
    # print(f'{path}/{cl}')
    curImg = cv2.imread(f'{path}/{cl}')
    # print(curImg)
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(myList)
print(classNames)


# make transmission to the database
def transmission(name, time,entries):
    # picture = ''
    # for pick in myList:
    #     Names = os.path.splitext(pick)[0]
    #     print(Names)
    #     if Names.upper() == name:
    #         picture = pick
    #         break
    photoname = name+'.jpg'
    url = 'http://localhost:3116/presence'
    myobj = {'name': name, 'datetime': time, 'photo': photoname, 'entries': entries}
    x = requests.post(url, data=myobj)
    return (x.text)
    print (x.text)



# make update transmission to the database
def updateTransmission(name, time,entries):

    photoname = name+'.jpg'
    url = 'http://localhost:3116/updateUser/:name'
    myobj = {'name': name, 'datetime': time, 'photo': photoname, 'entries': entries}
    x = requests.put(url, data=myobj)
    return (x.text)
    print("updated in DB successfully")
    print(x.text)



# Mark Attendance
def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        # retrieve existing name
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            counter =1
            now = datetime.now()
            dtString = now.strftime('%H: %M: %S')
            f.writelines(f'\n{name}, {dtString} , {counter}')

            # print(name, " Sucessfully identified!")
            text = name + " Successfully identified!"
            translated = translator.translate(text, dest=output_lang)
            print(translated.text)
            converted_audio = gtts.gTTS(translated.text, lang=output_lang)
            converted_audio.save(f'confirm{name}.mp3')
            playsound.playsound(f'confirm{name}.mp3')
            # print(googletrans.LANGUAGES)
            transmission(name, dtString, str(counter))
            print("transmission onbject:"+ name +","+ dtString +","+ str(counter))
        else:

            with open("Attendance.csv") as f:
                reader = csv.reader(f)
                for row in reader: # choose a specific row
                    # if(row[0]==name):
                    print("I found this name in order to update:" + name)
                    text = name + " Successfully identified!"
                    translated = translator.translate(text, dest=output_lang)
                    print(translated.text)
                    # converted_audio = gtts.gTTS(translated.text, lang=output_lang) # in 2 khat ra comment kardam chon ejazeye save yek payam rooye khodash ra nadarim, yani yek seda rooye yek file soty digar zabt shvad. pas dar khat badi faght an ra play mikonim
                    # converted_audio.save(f'confirm{name}.mp3')
                    playsound.playsound(f'confirm{name}.mp3')
                    # print(googletrans.LANGUAGES)
                    # ////// update file
                    filename = 'Attendance.csv'
                    tempfile = NamedTemporaryFile(mode='w+t', delete=False)
                    fields = ['NAME', 'TIME', 'COUNTER']
                    with open(filename, 'r') as csvfile, tempfile:
                        reader = csv.DictReader(csvfile, fieldnames=fields)
                        writer = csv.DictWriter(tempfile, fieldnames=fields)
                        for row in reader:
                            if row['NAME'] == name:
                                counter = int(row['COUNTER']) +1
                                now = datetime.now()
                                dtString = now.strftime('%D , %H: %M: %S')
                                print('updating row', row['NAME'])
                                row['NAME'], row['TIME'], row['COUNTER'] = name , dtString , counter
                            row = {'NAME': row['NAME'],'TIME': row['TIME'], 'COUNTER':row['COUNTER']}
                            writer.writerow(row)
                    updateTransmission(name, dtString, counter)
                    print("updateTransmission onbject:" + name + "," + dtString + "," + str(counter))
                    shutil.move(tempfile.name, filename)
                    # updateTransmission(name, dtString, counter)


# Compute encoding of images
def findEncoding(myImgs): # myImgs is the list of images (matrix of pixels)
    encodeList = []
    for myimg in myImgs:
        img = cv2.cvtColor(myimg, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Encode all the images
encodeListFinal = findEncoding(images)
print("Images were encoded successfully!")
i =0
# Read from camera
cap = cv2.VideoCapture(0)
while True:# Get the frame one by one
    success , img = cap.read()
    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    # (0,0): original image
    # None: define any pixel size
    # scale: 1/4 of the size
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    # Find face location of our webcam
    facesCurFrame = face_recognition.face_locations(imgS)
    # print(len(facesCurFrame))
    # Encode face
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListFinal, encodeFace)
        faceDis = face_recognition.face_distance(encodeListFinal, encodeFace)
        # print(matches)
        # print(faceDis)

        for fd in faceDis:
            if fd < 0.50:
                i = i + 1
        # print(i)
        # if i == 2:   # in baraye vaghty hast ke az shakhs 2 ta aks hast.
        #     print('inconnu2')
        if i < 1:  # baraye vaghty ke shakhs na shenas hast
            print('inconnu1')
        elif i == 1:
            # return the element with smallest distance
            matchIndex = np.argmin(faceDis)
            # print(matchIndex.size)
            if matches[matchIndex]:
                name = classNames[matchIndex].upper()  # retrieve name and convert in UpperCase
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 10, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

    cv2.imshow("Webcam", img)
    cv2.waitKey(1)















