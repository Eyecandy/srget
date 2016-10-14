import sys
import socket as skt
import os
from urlparse import urlparse
import os.path
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
def http_head_format(verb,url,Brange,DEFAULT_PORT = 80):
	#split at colon, to remove port from host
	host = url.hostname
	path = url.path
	if path == "":
		path = "/"
	ip_address = skt.gethostbyname(host)
	port = url.port
	if url.port == None:
		port = DEFAULT_PORT
		return ("{verb} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\n{Brange}Accept: text/html\r\n\r\n".format(verb = verb,path = path,Brange =Brange,ip = ip_address,port = str(port)),ip_address,port)
	else:
		return ("{verb} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\n{Brange}Accept: text/html\r\n\r\n".format(verb = verb,path = path,Brange = Brange,ip = ip_address,port = str(port)),ip_address,port)
		
#parses the url
def parse_URL(verb,Brange):
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		return http_head_format(verb,url,Brange)
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

def check_Etag():
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	clientSocket.connect((ip_address,port))
	head = parse_URL("HEAD","")
	clientSocket.send(head[0])
	receiving_data = clientSocket.recv(1024)
	full_header = receiving_data
	while receiving_data:
		receiving_data = clientSocket.recv(1024)
		full_header += receiving_data
	rdoc = open("rdoc","r")
	rdoc_line = rdoc.readlines()
	
	"""My rdoc has 3 lines, the first Last-Modified
	The Second is for Etag, third is byte downloaded
	hence if the if my document only contains less than than 3 elements
	We have to download from scratch. This can happens since the Etag is optional 
	in the HTTP response"""
	if len(rdoc_line) > 3:
		return False
	"""this loop run through through the head information
	and compares is to the rdoc information
	if last modified dates are not the same return false,if etags are not the same return false
	if Etag is not found return false"""
	Etag_found = False
	header_split = full_header.split("\r\n")
	for line in header_split:
		field_content = line.split(":")
		field = field_content[0]
		
		if field == "Last-Modified":
			content = field_content[1]
			if content.strip() != rdoc_line[0].strip():
				clientSocket.close()
				return False
		if field == "ETag":
			Etag_found = True
			content = field_content[1]
			if content.strip() != rdoc_line[1].strip():
				clientSocket.close()
				return False
	clientSocket.close()
	print rdoc_line[-1]
	return Etag_found



def write_data(GETHeader,ip_address,port,filename):
	
	
	#If there is no rdoc it also means there is no Etag
	"""If the rdoc doesn't exists that means that there is no information stored
	If there is no information stored then that means that the program went smoothly
	because I delete the rdoc at the end of program. 
	That means that all data is written
	However if all data is not written the files exists and we will check for Etag and more """
	can_resume_download = False
	if os.path.exists("rdoc"):
		can_resume_download = check_Etag()
	
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	
	clientSocket.connect((ip_address,port))
	if not can_resume_download:
		clientSocket.send(GETHeader)
	else:
		print "Can resume"

		#range_header = parse_URL("GET",)
		sys.exit(1)
	
	receiving_data = clientSocket.recv(1024)
	full_string = receiving_data
	left_over_string_from_header = ""
	header = ""
	body = ""
	header_found = False
	more_data = True
	byte_rec = 0

	"""Append if there exists and Etag that matches current file"""
	if os.path.exists(filename):
		os.remove(filename)

	download2 = open(filename,"a") #currently appending

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
			download2.write(left_over_string_from_header)
			byte_rec = len(left_over_string_from_header)
			header_found = True
		else:
			y = min(content_length-byte_rec,4096)
			try:
				receiving_data = clientSocket.recv(y)
			except skt.timeout:
				sys.exit(1)
			download2.write(receiving_data)
			body += receiving_data
			byte_rec = len(body)
			f = open("rdoc","r")
			rdoc_lines = f.readlines()
			w = open("rdoc","wb")
			for line in rdoc_lines:
				w.write(line)
			w = open("rdoc","a")
			w.write(str(byte_rec)+"\r\n")
			
		
			if content_length-byte_rec ==0:
				more_data = False
	os.remove("rdoc")
	clientSocket.close()
	
	
#returns a tuple with GET header, ip address and port:
GETHeader_ipAddress_port = parse_URL("GET","")


#GET header is set to a variable
GETHeader = GETHeader_ipAddress_port[0]


#giving ip it's own variable
ip_address = GETHeader_ipAddress_port[1]

#giving port it's own variable
port = GETHeader_ipAddress_port[2]

#write data to filename
write_data(GETHeader,ip_address,port,sys.argv[2])







#create a dictionary and store all the information of the header






