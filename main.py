import cv2
import face_recognition
import os
from datetime import datetime
import pyttsx3


def speak(text):
    audio.say(text)
    audio.runAndWait()


def encodings(images):
    encodeList = []
    for img in images:
        encode = face_recognition.face_encodings(
            img)[0]  # Add encodings to the list
        encodeList.append(encode)
    return encodeList


def boxTxt(img, name='Unknown', color=(0, 0, 255)):
    cv2.rectangle(img, (x1*4, y1*4), (x2*4, y2*4),
                  color, 2)  # Draw the box around face
    cv2.rectangle(img, (x1*4, y2*4-35), (x2*4, y2*4),
                  color, cv2.FILLED)  # Below box Label
    cv2.putText(img, name, (x1*4+6, y2*4-6),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)  # Label text


def attendance(name):
    with open('Attendance.csv', 'r+') as report:
        data = report.readlines()
        names = set()
        dates = set()
        for line in data:
            entry = line.split(',')
            names.add(entry[0])  # Get all names in record into names list
            try:
                dates.add(entry[1])
            except IndexError:
                pass
        present = datetime.now()
        dateTime = present.strftime('%d-%m-%Y,%H:%M:%S')
        # Add attendance into record
        if name not in names:
            report.writelines(f'\n{name},{dateTime}')
            attend = name + ", Your attendance is recorded."
        elif name in names and present.strftime('%d-%m-%Y') not in dates:
            report.writelines(f'\n{name},{dateTime}')
            attend = name + ", Your attendance is recorded."
        else:
            attend = name + ", Your attendance is already recorded."
        if(voice_check):
            speak(attend)


voice = input("Do you want voice over? (y/n)").lower()
if(voice == 'y'):
    voice_check = True
elif voice == 'n':
    voice_check = False
else:
    print("Invalid Input...")
    exit(0)

path = 'known/'
images = []
people = []
known_faces = os.listdir(path)  # Get files list
for person in known_faces:
    cImg = cv2.imread(path+person)
    images.append(cImg)  # Load images into list
    # Get name of file without extension
    people.append(os.path.splitext(person)[0])
print(people)

try:
    knownEncodings = encodings(images)
    print('Encoding is completed....')
except IndexError:
    print("Error... \nPossible issues: Provided known pictures' Face is not clear or No Face is Found")
    exit()
except:
    print('Unknown Error Faced....')
    exit()

capture = cv2.VideoCapture(0)  # Assign object to camera 0
if voice_check:
    audio = pyttsx3.init()  # initiate object to speaker

while True:
    # Return 2 variables, if capture was success and the captured image
    success, img = capture.read()
    if success:
        bool_known_face = True  # Assume face is known
        name = 'Unknown'  # Define name to default
        # Scale down to reduce system burden
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        face = face_recognition.face_locations(imgS)
        encoded_face = face_recognition.face_encodings(imgS)

        # for enFc, fcLoc in zip(encoded_face, face):  # For loop to find multiple faces
        if len(face) == 1:
            matches = face_recognition.compare_faces(
                knownEncodings, encoded_face[0])
            face_distance = face_recognition.face_distance(
                knownEncodings, encoded_face[0])
            for i in range(len(face_distance)):
                if min(face_distance) == face_distance[i]:
                    matchIndex = i  # Find corresding matched faces index
            y1, x2, y2, x1 = face[0]
            if matches[matchIndex]:
                name = people[matchIndex]
                boxTxt(img, name, (0, 255, 0))
            else:
                boxTxt(img)
                bool_known_face = False
        elif len(face) == 0:
            pass
        else:
            img = cv2.imread('Multi.jpg')  # If multiple faces Detected
            img = cv2.resize(img, (0, 0), None, 0.3, 0.3)
        if len(face) != 0:  # If any face is found
            cv2.imshow('Cam', img)
        else:
            cv2.destroyAllWindows()
        key = cv2.waitKey(1)  # To record key strokes
        if key == 27:  # If key is 'esc' key
            break
        if bool_known_face:
            if name != 'Unknown':
                attendance(name)
    else:
        print('Please check your Cam...')
        break

capture.release()
cv2.destroyAllWindows()
