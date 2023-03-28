"""
使用多路复用器select实现的简单的多进程高性能reactor
"""
import socket
import select
import time
from multiprocessing import Process, Queue, cpu_count


def single_process(socket_queue, process_id):
    my_sockets = {}
    while True:
        if socket_queue.qsize() > 0:
            c = socket_queue.get()
            my_sockets[c.fileno()] = c
        del_list = []
        for fd in my_sockets:
            try:
                s = my_sockets[fd]
                msg = s.recv(1024)
                print(process_id, fd, msg)
                if msg:
                    s.send(msg)
                else:
                    del_list.append(fd)
                    s.close()
            except:
                pass
        for fd in del_list:
            del my_sockets[fd]
        time.sleep(1 / 1000)


if __name__ == '__main__':
    server = socket.socket()
    host = '127.0.0.1'
    port = 5005
    server.bind((host, port))
    server.listen(1000)
    server.setblocking(False)

    cpu_nums = cpu_count()
    sockets_list = []
    for n in range(cpu_nums):
        sockets_list.append(Queue(1000))

    all_process = []
    for n in range(cpu_nums):
        p = Process(target=single_process, args=(sockets_list[n], n))
        all_process.append(p)

    for p in all_process:
        p.start()

    index = 0
    while True:
        try:
            client, addr = server.accept()
            client.setblocking(True)
            if index == cpu_nums:
                index = 0
            sockets_list[index].put(client)
            index += 1
        except:
            pass
        time.sleep(1 / 1000)




