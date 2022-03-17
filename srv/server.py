# /usr/bin/env python3
import subprocess
import socket
import os
import sys
from threading import Thread
from random import randint
BUFFER = 1000


def getexistport(ip):
    exsistport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        port = randint(1025, 65535)
        res = exsistport.connect_ex((ip, port))
        # 111 means connection refused (no one listen on that port)
        if res == 111:
            break
    exsistport.close()
    return port


def list_files(client):
    list =subprocess.check_output(['ls','-l'])
    client.send(list)
    print('[+] list of files sent.')


def send_to_client(client, filename):
    # check file is available
    if not os.path.exists(filename):
        print('[-] 550 File not found')
        client.send('550'.encode())  
        return
    else:
        print('[+] file Exsist')
        client.send('[+] file Exsist'.encode())

    # socketing data connection on port+1
    ip = client.getsockname()[0]
    datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = getexistport(ip)
    try:
        datasock.bind((ip, port))
        datasock.listen(1)
        client.send(str(port).encode())
    except Exception as e:
        print(e)
        client.send(b'ERROR')
        return

    # connection is open for receiving data
    dataconn, _ = datasock.accept()

    # send file
    with open(filename, "rb") as f:
        print('[+] Sending file ', filename)
        while True:
            data = f.read(BUFFER)
            if not data:
                break
            dataconn.send(data)
        datasock.close()
    print('[+] Transfer complete.')


def receive_from_client(client, filename):
    # socketing data connection on port+1
    ip = client.getsockname()[0]
    datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = getexistport(ip)
    try:
        datasock.bind((ip, port))
        datasock.listen(1)
        client.send(str(port).encode())
    except Exception as e:
        print(e)
        client.send(b'ERROR')
        return

    # connection is open for receiving data
    dataconn, _ = datasock.accept()

    # receiving data
    with open(filename, 'wb') as f:
        print('[+] Receiving file ', filename)
        while True:
            data = dataconn.recv(BUFFER)
            if not data:
                break
            f.write(data)
        datasock.close()

    print('[+] Received  Successful')


def conInfo(addr):
    return "{}:{}".format(addr[0], addr[1])


def connection(client, addr, id):
    print('******')
    print('[{}] Connection started -- {}'.format(id, conInfo(addr)))

    reqnum = 0
    while True:
        reqnum += 1

        data = client.recv(BUFFER)
        recvCmd = data.decode()
        cmd, arg = "", ""

        if ' ' in recvCmd:
            cmd, arg = recvCmd.split(' ')
        else:
            cmd = recvCmd
        cmd = cmd.upper()

        if not data:
            break

        print('***')
        print("[{}] Received instruction number {}: {} {}".format(
            id, reqnum, cmd, arg))

        if "LIST" == cmd:
            list_files(client)

        elif "GET" == cmd:
            send_to_client(client, arg)

        elif "PUT" == cmd:
            receive_from_client(client, arg)

        elif "QUIT" == cmd:
            client.close()
            print('[{}] Connection closed -- {}'.format(id, conInfo(addr)))
            exit(0)

        else:
            print('[-] Bad request!')

        data = None


def main(argv):
    if len(argv) != 1:
        print('** Format eroor:     server.py <PORT> ')
        print('like: server.py 1234')
        exit(1)

    IP = '0.0.0.0'
    PORT = int(argv[0])

    # initiation
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(3)

    print('-- FTP Server - {}:{} -- '.format(IP, PORT))

    numberOfConnections = 0
    try:
        while True:
            client, addr = server.accept()
            numberOfConnections += 1
            Thread(target=connection, args=(
                client, addr, numberOfConnections)).start()

    except Exception as e:
        print(e)
        exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
