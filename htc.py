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

import sys
import socket
import threading
import urllib.request
import time
import base64
import select

####
#### The method of a first thread which do a GET request for take a command data send these to ssh 
#### socket for execution. 
####
def commandeReader(htcSocket, remote_address, port):
	while (1):
		try:			
			res = urllib.request.urlopen("http://"+remote_address+":"+str(port)).read()
			#res = urllib.request.urlopen("http://127.0.0.1:8080").read()
		except:
			pass
		else:
			htcSocket.send(base64.b64decode(res))
		time.sleep(0.5)

####
#### The methode of 2nd thread that verify on SSH socket il it must send command result 
#### and send it if the result exist
####

def commandeResultWriter(htcSocket, remote_address, port):
	while (1):
		data=bytes("", "UTF-8")
		data_is_full = False
		while not data_is_full:
			read, write, error = select.select([htcSocket], [htcSocket], [])
			if htcSocket in read:
				data += htcSocket.recv(512)
			else:
				data_is_full = True
		try:
			if data:
				res = urllib.request.urlopen("http://"+remote_address+":"+str(port), base64.b64encode(data))
		except:
			time.sleep(0.5)


if __name__ == "__main__":
	if len(sys.argv) < 3 :
		print("Usage htt_client -remote remote_address")
		exit(1)
	elif len(sys.argv) == 3:	 
		if sys.argv[1] == "-remote":
			http_proxy = "" 
			remote_address = sys.argv[2]
		else:
			print("Usage htt_client -remote remote_address")
			exit(1)
	##elif len(sys.argv) == 5:	 
	#	if sys.argv[1] == '-remote' :
	#		http_proxy = sys.argv[2]
	#	else:
	#		print("Usage htt_client -remote remote_address -proxy http_proxy\n")
	#		exit(1)
	#	if sys.argv[3] == "-proxy":
	#		remote_address = sys.argv[4]
	#	else:
	#		print("Usage htt_client -remote remote_address -proxy http_proxy\n")
	#		exit(1)
	else:		
		print("Usage htt_client -remote remote_address -proxy http_proxy\n")
		exit(1)
	port = 8080
	htcSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	htcSocket.connect(("", 22))
	com_th = threading.Thread(None, commandeReader, None, (htcSocket, remote_address, port))
	com_th.start()
	res_th = threading.Thread(None, commandeResultWriter, None, (htcSocket, remote_address, port))
	res_th.start()
