import sys
import socket as skt
import os
from urlparse import urlparse
#A Bunch of Error print messages
def error_message(error_code):
	if error_code ==1:
		print "Error: Incorrect input format."
		print "Use this format: srget -o <output file> [-c [<numConn>]] http://someurl.domain[:port]/path/to/file"
	elif error_code ==2:
		print "Error: incorrect protocol"
		print "Use: http protocol"
	elif error_code == 3:
		print "Error: Socket Time Out"

#Just checking that the input in the command line is correct
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
	host = url.hostname
	path = url.path
	if path == "":
		path = "/"
	ip_address = skt.gethostbyname(host)
	print ip_address
	port = url.port
	if url.port == None:
		port = 80
		return ("HEAD {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip_address,port)
	else:
		return ("HEAD {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip_address,port)
		
#parses the url
def parse_URL():
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		return http_head_format(url)
	else:
		error_message(2)
		sys.exit(1)

def connect_to_get_HEAD(GETHeader,ip_address,port):

	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	#In case it doesn't connect within 5 seconds
	clientSocket.settimeout(5)
	try:clientSocket.connect((ip_address,port))
	except skt.timeout:
		error_message(3)
		sys.exit(1)
	clientSocket.send(GETHeader)
	receiving_data = clientSocket.recv(1024)
	full_string = receiving_data
	while receiving_data:
		receiving_data = clientSocket.recv(1024)
		full_string+=receiving_data

	clientSocket.close()
	print "--------------------------EeEEEEEEEEEEEEEEEEEEEEEEEE------------------"
	
	return full_string

def extract_HEAD_information(header):
	print header
	


	

#returns a tuple with GET header, ip address and port:
GETHeader_ipAddress_port = parse_URL()

#GET header is set to a variable
GETHeader = GETHeader_ipAddress_port[0]

#giving ip it's own variable
ip_address = GETHeader_ipAddress_port[1]

#giving port it's own variable
port = GETHeader_ipAddress_port[2]

#puts the separated tuple into a connection function
#the returned output is the header :
header_received = connect_to_get_HEAD(GETHeader,ip_address,port)


#Get useful information from header
extract_HEAD_information(header_received)



















