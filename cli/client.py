# /usr/bin/env python3
import socket
import os
import sys
BUFFER = 1000


def list_files(sock):
    try:
        sock.send("LIST".encode())
    except Exception as e:
        print(e)
        return

    files = sock.recv(BUFFER)
    files = files.decode().split('||')
    for f in files:
        print("\t {}".format(f))


def receive_from_server(sock, filename):
    # send req
    try:
        sock.send(("GET "+filename).encode())
    except Exception as e:
        print(e)
        return

    # check for availability of file if available returns file size
    msg = sock.recv(BUFFER).decode()
    if msg == '550':
        print('[-] File Not Found!')
        return

    # conecting to data socket (error or port to connect)
    msg = sock.recv(BUFFER).decode()
    if msg == 'ERROR':
        print('[-] Connection problem')
        return

    datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = sock.getpeername()[0]
    port = int(msg)
    datasock.connect((ip, port))

    # receiving data
    with open(filename, 'wb') as f:
        print('[+] Receiving file ', filename)
        while True:
            data = datasock.recv(BUFFER)
            if not data:
                break
            f.write(data)
        datasock.close()
    print('[+] Received  Successful')


def send_to_server(sock, filename):
    # check file exist in client machine
    if not os.path.exists(filename):
        print('[-] File not found')
        return

    # send put req
    try:
        sock.send(("PUT "+filename).encode())
    except Exception as e:
        print(e)
        return

    # conecting to data socket (error or port to connect)
    msg = sock.recv(BUFFER).decode()
    if msg == 'ERROR':
        print('[-] Connection problem')
        return

    datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = sock.getpeername()[0]
    port = int(msg)
    datasock.connect((ip, port))

    # send file
    with open(filename, "rb") as f:
        print('[+] Sending file ', filename)
        while True:
            data = f.read(BUFFER)
            if not data:
                break
            datasock.send(data)
        datasock.close()

    print('[+] Transfer complete.')


def help():
    print("\tget <file-name> -- receive file from server")
    print("\tput <file-name> -- send file file server")
    print("\tlist         ls -- print list of files")
    print("\tquit          q -- exit from app and close connection")
    print("\thelp          h -- print this")


def main(argv):
    if len(argv) != 2:
        print('** Format eroor:     client.py <IPAdress> <PORT> ')
        print('like: client.py 127.0.0.1 1234')
        exit(1)

    print("--FTP Client--")

    IP = argv[0]
    PORT = int(argv[1])

    # initiation
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect
    try:
        sock.connect((IP, PORT))
        print("[+] Connected sucessfully \n")
    except Exception as e:
        print(e)
        exit(2)

    try:
        while True:
            insertCmd = input('\nFTP> ').strip()

            if ' ' in insertCmd:
                cmd, arg = insertCmd.split(' ')
            else:
                cmd = insertCmd
            cmd = cmd.lower()

            if cmd == "list" or cmd == "ls":
                list_files(sock)

            elif cmd == "get":
                filename = arg
                receive_from_server(sock, filename)

            elif cmd == "put":
                filename = arg
                send_to_server(sock, filename)

            elif cmd == "quit" or cmd == "q":
                print('[*] Exiting...')
                sock.send("QUIT".encode())
                sock.close()
                print("[*] Server connection ended.")
                exit(0)

            elif cmd == "help" or cmd == "h":
                help()

            else:
                sock.send(cmd.encode())
    except (Exception, KeyboardInterrupt) as e:
        sock.send("QUIT".encode())
        sock.close()
        print("[*] Server connection ended.")
        print(e)
        exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
