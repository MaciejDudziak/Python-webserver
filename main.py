#!/usr/bin/python3

from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, HTTPServer
import http.server
import socketserver
import getopt
import sys
import ipaddress
import os
from urllib.parse import urlparse

def errorHandling():
	print("Podany argument nie istnieje")
	sys.exit() 

def is_IP_corect(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False


sys.tracebacklimit = 0 #w terminalu wyswietlamy tylko wiadomosc error, bez tracebacku

argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "p:a:u:d:h")
except:
    errorHandling()

PORT = 9000
ADRESS = ""
URL = ""
DIRECTORY = ""
Handler = http.server.SimpleHTTPRequestHandler

for opt, arg in opts:
    if opt in ["-p"]:
        if arg.isdigit():
            if int(arg) >= 1024 and int(arg) <= 65535:
                PORT = int(arg)
            else:
                print("numer portu musi by z przedzialu 1024-65535")
                sys.exit()
        else:
            print("Numer portu musi byc liczba calkowita")
            sys.exit()
    elif opt in ["-a"]:
        if is_IP_corect(arg):
            ADRESS = arg
        else:
            print("Podaj poprawny adres IP")
            sys.exit()
    elif opt in ["-u"]:
        URL = arg
    elif opt in ["-d"]:
        DIRECTORY = arg
    elif opt in ["-h"]:
        print("""Skrypt do stawiania prostego serwera
              Parametry -u i -d sa wymagane
Parametry:
-p<numer portu> przyjmuje numer portu
-a<adres> przyjmuje adres strony
-u<adres url> przyjmuje adres url do pliku ktory chcemy wyswietlic na stronie
-d<sciezka do katalogu glownego serwera> przyjmuje sicezke do katalogu glownego serwera
-h wyswietla instrukcje uzywania skryptu""")
        sys.exit()

if (len(URL) == 0 or len(DIRECTORY) == 0):
    print("Paramtry -d i -u sa wymagane. Aby wyswietlic instrukcje uruchom program z parametrm -h")
    sys.exit()
    
os.chdir(DIRECTORY) #ustawiamy katalog glowny
URL = urlparse(URL) #wyluskujemy sciezke do pliku
URL = URL.path[1:] #pozbywamy sie poczatkowego znaku /

if os.access(URL, os.F_OK) == False:#jezli url nie istnieje zwracamy error 404 i wyswietlamy go na stronie
    class MyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Error 404')
    with socketserver.TCPServer((ADRESS, PORT), MyHandler) as httpd:
        httpd.serve_forever()

else:#dla katalogu

    if os.path.isdir(URL):
        os.chdir(URL)
        s=os.scandir('.')
        dir=list(s)
        with open("listing.html","w") as listing:
            listing.write("""
<!DOCTYPE html>
<html>
<head>
<title>STRONKA</title>
</head>

<body>
<h1>Zawartosc:</h1>
                          """)
            for i in range(len(dir)):
                if(dir[i].name != 'listing.html'):
                    if dir[i].is_dir():#dla podfolderu link przenosi nas do podfolderu
                        listing.write(f"<p><h3>{dir[i].name}</h3> ostatnia data modyfikacji: {datetime.fromtimestamp(dir[i].stat().st_mtime).strftime('%Y-%m-%d %H:%M')}, rozmiar pliku: {dir[i].stat().st_size}b pobierz plik: <a href={dir[i].name}>{dir[i].name}</a></p>")
                    else:#dla plikow innego typu link pozwala nam je pobrac
                        listing.write(f"<p><h3>{dir[i].name}</h3> ostatnia data modyfikacji: {datetime.fromtimestamp(dir[i].stat().st_mtime).strftime('%Y-%m-%d %H:%M')}, rozmiar pliku: {dir[i].stat().st_size}b pobierz plik: <a href={dir[i].name} download>{dir[i].name}</a></p>")
            listing.write("""
</body>
</html>                         
                          """)
        class MyHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open("listing.html", 'rb') as file:
                    self.wfile.write(file.read())
        httpd = HTTPServer((ADRESS, PORT), Handler) #dla folderu uzywamy domyslnego handlera
        httpd.serve_forever()

    else:#dla pliku
        if URL.endswith(".html"):#pliki html
            class MyHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    with open(URL, 'rb') as file:
                        self.wfile.write(file.read())
        elif URL.endswith(".txt"):#pliki txt
            class MyHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    with open(URL, 'rb') as file:
                        self.wfile.write(file.read())
        elif URL.endswith(".pdf"):#pdfy
            class MyHandler(SimpleHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/pdf')
                    self.end_headers()
                    with open(URL, 'rb') as file:
                        self.wfile.write(file.read())

        httpd = HTTPServer((ADRESS, PORT), MyHandler)
        httpd.serve_forever()
