import threading
import socket


def connect(id):
    host = '127.0.0.1'
    port = 5005
    client = socket.socket()
    client.connect((host, port))
    index = 0
    while index < 5:
        client.send(b'hello server')
        msg = client.recv(1024)
        if msg:
            print(id, msg)
        index += 1
    client.close()


if __name__ == '__main__':
    nums = 100
    for i in range(nums):
        thread = threading.Thread(target=connect, args=(i, ))
        thread.start()
