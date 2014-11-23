Http_Tunnel
===========

This python program permit to etablished a ssh session between your home computer and you company server behind a web proxy. A web proxy refuse all soonexion on other port that 80. A program will encapsul a ssh in a HTTP request and a dialogue beetwen a 2 computers is as a Web communication.

Run
====

#### Server

    python3 hts.py

on other terminal:

    ssh 127.0.0.1 -p 2222

You can execute a commands that you wants

#### Client

I assume that a system proxy configured on all network computers ( if not change session http_proxy environnement variable)
if proxy configured
    
    python3 htc.py -remote server_address

if proxy not configured

    export http_proxy=http_proxy_address:3128
    python3 htc.py -remote server_address
