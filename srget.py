import sys
import socket as skt
import os
from urlparse import urlparse
def error_message(error_code):
	if error_code ==1:
		print "Error: Incorrect input format."
		print "Use this format: srget -o <output file> [-c [<numConn>]] http://someurl.domain[:port]/path/to/file"
	elif error_code ==2:
		print "Error: incorrect protocol"
		print "Use: http protocol"
	elif error_code == 3:
		print "Error: Socket Time Out"


def check_argument_length_correct():
	if (len(sys.argv) == 4 and sys.argv[1] == "-o"):
		return True


	elif len(sys.argv) == 6 and sys.argv[1] == "-o" and sys.argv[3] == "-c":
		return True
		
	else: 
		error_message(1)
		sys.exit(1)
		
check_argument_length_correct()
#gives back the formatted string, the ip address and the port number
def http_head_format(url):
	#split at colon, to remove port from host
	host = url.netloc.split(":")[0]
	path = url.path
	if path == "":
		path = "/"
	
	ip_address = skt.gethostbyname(host)
	port = url.port
	if url.port == None:
		port = 80
		return ("GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip_address,port)
	else:
		return ("GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip,port)
		
#parses the url
def parse_URL():
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		return http_head_format(url)
	
	else:
		error_message(2)

def connect(GETHeader,ip_address,port):
	#some TCP stuff
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	#In case it doesn't connect within 5 seconds
	clientSocket.settimeout(5)
	try:clientSocket.connect((ip_address,port))
	except skt.timeout:
		error_message(3)
		sys.exit(1)
	clientSocket.send(GETHeader)
	
	recieving_data = clientSocket.recv(1024)
	full_string = recieving_data
	while recieving_data:
		recieving_data = clientSocket.recv(1024)
		full_string+=recieving_data
	clientSocket.close()
	print full_string
	print "Website accessed"




#returns a tuple with GET header, ip address and port:
GETHeader_ipAddress_port = parse_URL()
#separate the tuple:
GETHeader = GETHeader_ipAddress_port[0]
ip_address = GETHeader_ipAddress_port[1]
port = GETHeader_ipAddress_port[2]
#puts the separated tuple into a connection function
connect(GETHeader,ip_address,port)
















