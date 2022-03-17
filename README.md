# FTP socket cli-srv 
A simple FTP client-server w/ python socket programming.

Can connect and access server directory to download and upload files using client application, that do all of this through a socket connection.

## HOW TO USE
- First have to run `server.py` on specefic port 
```bash
cd srv
# python3 server.py <PORT>
python3 server.py 2323
```
- now in client side run `client.py` to connect server w/ ip and port of server
```bash
cd cli
# python3 client.py <server-IP> <PORT>
python3 client.py 127.0.0.1 2323
```
- client provides a interactive command line that provide this commands:
    - `ls` or `list` -- get list of files and directories of server(where server is run)
    - `get <FILE-NAME>` -- download file from server.
    - `put <FILE-NAME>` -- upload file to server. 
    - `q` or `quit` -- close client connection.
    - `h` or `help` -- print help page.

## server.py
This application get instructions then run it for each.

Using multi thread for supporting multi client connection and for each one create a thread to handle requests.

for upload and download files: server first stablish another port(random between `1025`, `65535`) and share the file across selected port.

## client.py
This application send instructions to the server through socket connection and receive proper response from it. 