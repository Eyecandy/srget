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
	elif error_code == 4:
		print "Bad request"


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
def http_head_format(url,type_request):
	#split at colon, to remove port from host
	host = url.hostname
	path = url.path
	if path == "":
		path = "/"
	ip_address = skt.gethostbyname(host)
	port = url.port
	if url.port == None:
		port = 80
		return ("{type_request} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(type_request = type_request,path = path,ip = ip_address,port = str(port)),ip_address,port)
	else:
		return ("{type_request} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(type_request = type_request,path = path,ip = ip_address,port = str(port)),ip_address,port)
		
#parses the url
def parse_URL():
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		return http_head_format(url,"HEAD")
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
	head_split = header.split("\r\n")
	status_code = head_split[0]
	if status_code=="HTTP/1.1 200 OK":
		for i in range(1,len(head_split)-1):
			#just wanna check if the length is large enough and that the first letter is not C
			#if it is not C or smaller than 16 continue
			if len(head_split[i]) < 16 or head_split[i][0] != "C":
				continue
			elif head_split[i].split(":")[0] == "Content-Length":
				print head_split[i].split(":")[1]
				return head_split[i].split(":")[1]

	else:
		error_message(4)
		sys.exit(1)

def write_data(GETHeader,ip_address,port,content_length):
	print GETHeader
	print ip_address
	print port
	print content_length









	


	

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
content_length = extract_HEAD_information(header_received)

write_data(GETHeader,ip_address,port,content_length)



















