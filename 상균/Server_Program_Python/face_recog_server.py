import pymysql.cursors
import socketserver
import socket
import pymysql.cursors
import face_recognition
import cv2
import os
import numpy as np
import time

from time import sleep
import tkinter.messagebox
from os.path import exists

HOST = ''
PORT = 9009
class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        #self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name[0:9])
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def __del__(self):
        del self.camera

    def get_frame(self):
        try:
            # Grab a single frame of video
            #frame = self.camera.get_frame()
            frame = cv2.imread('download/image.jpg')

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if self.process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    min_value = min(distances)

                    # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                    # 0.6 is typical best performance.
                    name = "Unknown"
                    if min_value < 0.6:
                        index = np.argmin(distances)
                        name = self.known_face_names[index]
                        print('[%s] 로 판별' %name)
                        #response = tkinter.messagebox.askyesnocancel("출석", "출석취소")

                    self.face_names.append(name)
            return name
        except Exception as e:
            print(e)
            name = 'Unknown'
            return name

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


def downloadImage(self, data):
    startTime = time.time()
    data_transferred =0
    endTime = time.time() - startTime
    print(endTime)
    print('errorfunc1')
    with open('download/' + 'image.jpg', 'wb') as f:
        try:
            while data:
                f.write(data)
                data_transferred += len(data)
                data = self.request.recv(1024)

        except Exception as e:
            print(e)
        print('파일[%s] 전송종료. 전송량 [%d]' % ('image.jpg', data_transferred))
    print('errorfunc2')

def findStudentCode(self, student_code, class_code):
    try:
        curs = conn.cursor(pymysql.cursors.DictCursor)

        # sql = "select * from EA0017_1 where student_code=%s and date=CURDATE()"
        # curs.execute(sql, (student_code))

        # sql = "select * from EA0017_1 where student_code=%s and date=CURDATE()"
        # curs.execute(sql, (student_code))
        print(class_code)

        sql = 'SELECT * FROM ' + str(class_code) + ' where student_code= '+str(student_code) +' and date=CURDATE()' + ';'
        curs.execute(sql)

        print('hello')


        #test
        # sql = "select * from EA0017_1 where student_code=%s and date=%s"
        # curs.execute(sql, (201511041, '2019-05-26'))

        conn.commit()

        rows = curs.fetchall()
        if not rows:
            curs = conn.cursor(pymysql.cursors.DictCursor)
            # sql = "INSERT INTO EA0017_1 (student_code, date, attended) VALUES(%s, CURDATE(), 'O');"
            # curs.execute(sql, (student_code))
            sql = "INSERT INTO " +class_code +" (student_code, date, attended) VALUES("+str(student_code)+", CURDATE(), 'O');"
            curs.execute(sql)

            conn.commit()

            print('success insert')
        else:
            print('Already have')
        message = 'success'
        self.request.send(message.encode())

            #insert here to send success message
    except Exception as e:
        print(e)
        message = 'fail'
        self.request.send(message.encode())

def findAttentionsAndSendData(self, class_code):
    try:
        curs = conn.cursor(pymysql.cursors.DictCursor)

        queryString = 'SELECT * FROM ' + str(class_code) + ' where date=CURDATE()' + ';'
        curs.execute(queryString)

        conn.commit()

        rows = curs.fetchall()
        if not rows:
            print('nothing in table')
        else:
            print('select * from %s is complete' %class_code)
            print(rows)

            #print(type(rows))
            #message = '-'.join(rows)
            message = str(rows)
            self.request.send(message.encode())
    except Exception as e:
        print('finderror')
        print(e)
        message = 'fail'
        self.request.send(message.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        #https://stackoverflow.com/questions/21810151/python-how-to-set-a-timeout-on-receiving-data-in-socketserver-tcpserver
        self.request.settimeout(5)
        data_transferred = 0
        print('[%s] 연결됨' % self.client_address[0])
        data = self.request.recv(1024)  # 클라이언트로부터 무언가를 전달받음

        try:
            message = data.decode()[0:9]
            print(message)
            if(200000000 <= int(message) and int(message) <= 201999999):  # 파일이름 이진 바이트 스트림 데이터를 일반 문자열로 변환
                print('학번 이구나!')
                findStudentCode(self, int(message), data.decode()[9:17])
                return
        except Exception as e:
            print(e)

        try:
            message = data.decode()[0:8]
            print('강의코드구나!')
            findAttentionsAndSendData(self, message)
            return
        except Exception as e:
            print(e)

        downloadImage(self, data)
        name = face_recog.get_frame()
        print('[%s 을 클라이언트로 보내기_코드는 여기에]'%name)

        message = name
        self.request.send(message.encode())


def runServer():

    print('++++++파일 서버를 시작++++++')
    print("+++파일 서버를 끝내려면 'Ctrl + C'를 누르세요.")

    try:
        server = socketserver.TCPServer((HOST, PORT), MyTcpHandler)
        server.socket.settimeout(5)
        server.serve_forever()
        #server.handle_timeout()

    except KeyboardInterrupt:
        print('++++++파일 서버를 종료합니다.++++++')

try:
    # db = pymysql.connect(host="localhost",user="yann",passwd="yann",db="doctorat")

    conn = pymysql.connect(host='localhost',
                       user='connectuser',
                       password='connect123',
                       db='helloworld',
                       charset='utf8mb4')
except Exception:
    print("Error in MySQL connexion")
else:
    print("Success to connect database")

face_recog = FaceRecog()
print(face_recog.known_face_names)
runServer()
#출처: https: // lidron.tistory.com / 42[이프이푸이푸]