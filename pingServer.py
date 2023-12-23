# -*- coding: UTF-8 -*-

import socket
import subprocess
import time
import os

HOST            = ''
PORT            = int(os.environ.get('PingServerPort'))

PingServerToken = os.environ.get('PingServerToken')
PingAim         = os.environ.get('PingAim')

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def read_request(request):
    first = request.find(' ')
    second = request.find(' ', first + 1)
    return request[:first], request[first + 1:second]

def handle_connection(client_connection, client_address):
    client_address = client_address[0]

    token = client_connection.recv(1024).decode('utf-8')

    if token == PingServerToken:
        print("Try to ping " + PingAim)
        try:
            result = (subprocess.check_output(['ping', PingAim, '-c', '5'])).decode('utf-8')
        except:
            result = "5 packets transmitted, 0 received, 100% packet loss, time 4000ms"
        print(result)
        client_connection.send(result.encode('utf-8'))
        client_connection.close()
        # pingServer duty's end
        exit()

    client_connection.close()

if __name__ == "__main__":
    listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen.bind((HOST, PORT))
    listen.listen(5)
    print('Providing Ping Service on port %s ...' % PORT)
    while True:
        client_connection, client_address = listen.accept()
        handle_connection(client_connection, client_address)
