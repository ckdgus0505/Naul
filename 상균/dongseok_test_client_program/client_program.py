import socket
from time import sleep
from os.path import exists

HOST = 'localhost'
PORT = 9009

def sendAttendanceSuccess(filename, sock):
    sock.sendall(filename.encode())
def sendAttendanceStatus(filename, sock):
    sock.sendall(filename.encode())

def uploadImage(filename, sock):
    data_transferred = 0
    if not exists('upload/'+filename):  # 파일이 해당 디렉터리에 존재하지 않으면
        return  # handle()함수를 빠져 나온다.

    print('파일[%s] 전송 시작...' % filename)
    with open('upload/'+filename, 'rb') as f:
        try:
            data = f.read(1024)  # 파일을 1024바이트 읽음
            while data:  # 파일이 빈 문자열일때까지 반복
                data_transferred += sock.send(data)
                data = f.read(1024)
                # if not data:
                #     sock.send('\0'.encode())
                #     print('마지막')
                #     break

        except Exception as e:
            print(e)

    print('전송완료[%s], 전송량[%d]' % (filename, data_transferred))
def getResponse(sock):
    response = sock.recv(1024)
    response = response.decode()
    print('respose=%s'%response)

def sendFileToServer(filename):
    data_transferred = 0

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #    sock.connect((HOST, PORT))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    try:
        if (filename[-4:] == '.jpg'):
            uploadImage(filename, sock)
        else:
            sendAttendanceSuccess(filename, sock)
        # elif (200000000<=int(filename) and int(filename)<=201999999):
        #     sendAttendanceSuccess(filename, sock)
        sleep(0.1)

        getResponse(sock)
    except Exception as e:
        print(e)



filename = input('무엇을 보낼까요?:')
sendFileToServer(filename)

#출처: https: // lidron.tistory.com / 42[이프이푸이푸]