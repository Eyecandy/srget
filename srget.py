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
def http_head_format(url,DEFAULT_PORT = 80):
	#split at colon, to remove port from host
	host = url.hostname
	path = url.path
	if path == "":
		path = "/"
	ip_address = skt.gethostbyname(host)
	#print ip_address
	port = url.port
	if url.port == None:
		port = DEFAULT_PORT
		return ("GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip_address,port)
	else:
		return ("GET {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\nAccept: text/html\r\n\r\n".format(path = path,ip = ip_address,port = str(port)),ip_address,port)
		
#parses the url
def parse_URL():
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		return http_head_format(url)
	else:
		error_message(2)
		sys.exit(1)

def extract_HEAD_information(header):
	head_split = header.split("\r\n")
	status_code = head_split[0]
	content_length = 0
	resume_document = open("rdoc","wb")
	if status_code=="HTTP/1.1 200 OK":
		for i in range(1,len(head_split)-1):
			field_and_content = head_split[i].split(":")
			field = field_and_content[0]
			content = field_and_content[1]
			#just wanna check if the length is large enough and that the first letter is not C
			#if it is not C or smaller than 16 continue
			if (field[0] != "C" and field[0] != "E" and field[0] != "L"):
				continue
			elif field == "Content-Length":
				content_length = int(content)	
			elif field =="ETag":
				resume_document.write(content+"\r\n")
			elif field == "Last-Modified":
				resume_document.write(content+"\r\n")

		return content_length
	else:
		error_message(4)
		sys.exit(1)

def check_rdoc():
	#what you have to do for next time:
	#Send the header, the compare this header with the rdoc Etag and the Last-Modified
	#if these are the same then you resume download, with GET header with an range of bytes in the header
	pass
def write_data(GETHeader,ip_address,port,filename):
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	#In case it doesn't connect within 5 seconds
	clientSocket.connect((ip_address,port))
	clientSocket.send(GETHeader)
	receiving_data = clientSocket.recv(1024)

	full_string = receiving_data
	left_over_string_from_header = ""
	header = ""
	body = ""
	header_found = False
	more_data = True
	byte_rec = 0
	clientSocket.settimeout(10)
	while more_data and receiving_data:
		if not header_found:
			try:
				receiving_data = clientSocket.recv(1024)
			except skt.timeout:
				sys.exit(1)


			full_string+=receiving_data
		if not header_found and "\r\n\r\n" in full_string:
			header_leftOver = full_string.split("\r\n\r\n")
			header = header_leftOver[0]
			left_over_string_from_header= header_leftOver[1]
			content_length = extract_HEAD_information(header)
			body = left_over_string_from_header
			byte_rec = len(left_over_string_from_header)
			header_found = True
		else:
			y = min(content_length-byte_rec,4096)
			try:
				receiving_data = clientSocket.recv(y)
			except skt.timeout:
				sys.exit(1)
			body += receiving_data
			
			byte_rec = len(body)
			if content_length-byte_rec ==0:
				more_data = False

	downloaded = open(filename,'wb')

	downloaded.write(body)

	clientSocket.close()
	
	
#returns a tuple with GET header, ip address and port:
GETHeader_ipAddress_port = parse_URL()

#GET header is set to a variable
GETHeader = GETHeader_ipAddress_port[0]

#giving ip it's own variable
ip_address = GETHeader_ipAddress_port[1]

#giving port it's own variable
port = GETHeader_ipAddress_port[2]

#write data to filename
write_data(GETHeader,ip_address,port,sys.argv[2])







#create a dictionary and store all the information of the header












