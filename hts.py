#!/usr/bin/python3
### ----------------------------------------------------------------------------------------------------
### CAMARA Alpha Lalmas
### 06 Novembre 2014 -- 23h36
### Development of a HTTP tunnel --  For ARX Course project in master's degree class
### If your all network servers and posts are behind a web proxy, lot of people think 
### that anyone can't execute a jobs on a postes that behind a proxy.
### In this program, we assume that a person which execute this httpTunnel is in company for example.
### It run a progrm htc.py on a poste that he want have a accès from home. 
### And on his home post, he run hts.py program and in other terminal: ssh 127.0.0.1 -p 2222 and
### he can write a commande and it will be execute on a company post
### -----------------------------------------------------------------------------------------------------
import queue
import socket
import socketserver
import http.server
import threading
import base64
import time
import select

# Socket of connexion on port 2222 for ssh commande
htsSocket = None
# FIFO that contains all commande that must send to company's posts
# All commande will be chipher only the first data send by SSH program
commande_fifo = queue.Queue()
# FIFO That contains all command result send by company's posts 
# These result will be show for a user 
resultat_fifo = queue.Queue()

####
#### Handler class of HTTP Request. This class permit to redefine
#### a python web server default GET and POST method
####
class Handler(http.server.SimpleHTTPRequestHandler):
#
# Write a HTPP request response header
#
    def auto_headers(self, data):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", data.__len__())
        self.end_headers()

#
# Method that called when receiv HTTP GET request
#        
    def do_GET(self):      
        global commande_fifo
        if not commande_fifo.empty():
            data = commande_fifo.get()
        else:
            data=bytes("", "UTF-8")
        data = base64.b64encode(data)
        self.auto_headers(data)
        self.wfile.write(data)

#
# When company's post send a POST request that contains
# normally a ssh commands results
#        

    def do_POST(self):
        global resultat_fifo
        content_len = int(self.headers['content-length'])
        data = self.rfile.read(content_len)
        resultat_fifo.put(base64.b64decode(data))
        data = bytes("OK", "UTF-8")
        self.auto_headers(data)
        self.wfile.write(data)


#
# A server principal methode.
# Wait a connexion on localhost 2222 port.
# If receive connexion, and do while(1), receive command
# and send to compagny's post if these do GET request that readed in commande_fifo and
# read a commands results send by company's post and put it in resultat_fifo
#
def htsServer():
    global htsSocket
    global resultat_fifo
    global commande_fifo
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 2222))
    sock.listen(5)
    htsSocket, addr = sock.accept()
    print('Connexion from ', addr)
    while True:
        read, write, error = select.select([htsSocket], [htsSocket], [])
        if htsSocket in read:
            data = htsSocket.recv(512)
            commande_fifo.put(data)
        if htsSocket in write and not resultat_fifo.empty():
            data = resultat_fifo.get()
            htsSocket.send(data)
        time.sleep(0.5)
    sock.close()


if __name__ == "__main__":
    hts_th = threading.Thread(None, htsServer, None)
    hts_th.start()
    #Start HTTP server
    httpd = socketserver.TCPServer(("", 8080), Handler)
    print("serving at port 8080")
    httpd.serve_forever()
