# coding: utf8
"""
使用多路复用器epoll实现的简单的多进程高性能reactor
"""
import socket
import select
import time
from multiprocessing import Process, Queue, cpu_count


def single_process(socket_queue, process_id):
    epoll = select.epoll()
    my_sockets = {}
    while True:
        if socket_queue.qsize() > 0:
            c = socket_queue.get()
            my_sockets[c.fileno()] = {
                's': c,
                'send_msg': []
            }
            epoll.register(c.fileno(), select.EPOLLIN)
        try:
            events = epoll.poll(1)
            del_list = []
            for fileno, event in events:
                print()
                s = my_sockets[fileno]['s']
                if event & select.EPOLLIN:
                    msg = s.recv(1024)
                    if not msg:
                        del_list.append(fileno)
                        epoll.unregister(fileno)
                    print(process_id, msg)
                    my_sockets[fileno]['send_msg'].append(msg)
                    epoll.modify(fileno, select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    s.send(my_sockets[fileno]['send_msg'].pop())
                    epoll.modify(fileno, select.EPOLLIN)
                else:
                    pass
            for fd in del_list:
                del my_sockets[fd]
        except:
            pass
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




