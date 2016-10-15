import sys
import socket as skt
import os
from urlparse import urlparse
import os.path
import pickle

def check_argument_length_correct():
	if (len(sys.argv) == 4 and sys.argv[1] == "-o"):
		return True
	elif len(sys.argv) == 6 and sys.argv[1] == "-o" and sys.argv[3] == "-c":
		return True
	else: 
		print "Arguments put into command line is incorrect"
		sys.exit(1)
check_argument_length_correct()

def decide_if_HEAD_or_GET_request(meta_doc):
	if os.path.exists(meta_doc):
		return "HEAD"
	else:
		return "GET"
def parse_URL(url):
	url = urlparse(url)
	host,port,path = url.hostname,url.port,url.path
	ip = skt.gethostbyname(host)
	if path =="":
		path = "/"
	return (ip,port,path)

def make_request(GET_or_HEAD,ip,port,path,Brange,DEFAULT_PORT =80):
	return ("{GET_or_HEAD} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: Close\r\n{Brange}Accept: text/html\r\n\r\n".format(GET_or_HEAD = GET_or_HEAD,path = path,Brange =Brange,ip = ip,port = str(port)))

def downloadFromStart_or_resumeDownload(type_req,my_request,ip,port,meta_doc,filename):
	if type_req == "GET":
		print "downloadFromStart function chosen"
		downloadFromStart(my_request,ip,port,meta_doc,filename)
	if type_req == "HEAD":
		print "Entering: metaDoc_compare_newHeader"
		metaDoc_compare_newHeader(my_request,ip,port,meta_doc,filename)
		


def find_header_response(clientSocket):
	print "inside find_header_response"
	header_not_found = True
	data_recv = clientSocket.recv(1024)
	data_so_far,body = data_recv,""
	clientSocket.settimeout(10)
	while header_not_found:
		try:
			data_recv = clientSocket.recv(1024)
			data_so_far += data_recv
		except skt.timeout:
			print "socket time out from find_header_response"
		if "\r\n\r\n" in data_so_far:
			
			header,body = data_so_far.split("\r\n\r\n")
			header_not_found = False
	
	return (header,body)
def check_status_code(status_code):
	if status_code[9] != "2":
		print "Status code is not 200, EXITING"
		sys.exit(1)


def get_header_detail(header,meta_doc):
	print "inside get_header_detail"
	dic = {}
	header_list = header.split("\r\n")
	status_code = header_list[0]
	check_status_code(status_code)
	for i in header_list[1:]:
		i = i.split(":")
		field,value = i[0],i[1]
		dic[field] = value
	meta_doc_w = open(meta_doc,'w')
	pickle.dump(dic,meta_doc_w)
	return dic

def handle_write(body,filename,meta_doc,byte_recv,header_dic):
	download = open(filename,'a')
	download.write(body)
	header_dic["byte_recv"] = byte_recv
	meta_doc_w = open(meta_doc,'w')
	pickle.dump(header_dic,meta_doc_w)
	

def get_data(clientSocket,content_length,body_so_far,filename,meta_doc,header_dic):
	print "inside get_data"
	data_recv = clientSocket.recv(1024)
	body = body_so_far + data_recv
	byte_recv = len(body)
	handle_write(body,filename,meta_doc,byte_recv,header_dic)
	
	while data_recv and content_length - byte_recv != 0:
		data_recv = clientSocket.recv(1024)
		byte_recv += len(data_recv)
		handle_write(data_recv,filename,meta_doc,byte_recv,header_dic)

	print "download complete, bytes recieved =" +str(byte_recv)
	

	clientSocket.close()
	print "socket closed"
	

def create_meta_doc(filename,path):
	unusable_path = path
	path = ""
	for i in unusable_path:
		if i.isalpha() or i.isdigit():
			path += i
	return filename+path+".txt"
		

def downloadFromStart(my_request,ip,port,meta_doc,filename):
	print "inside downloadFromStart"
	print "Connecting...."
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	clientSocket.connect((ip,port))	
	print "Sending GET request"
	clientSocket.send(my_request)
	print "ENTERING: find_header_response"
	header,body = find_header_response(clientSocket)
	print "ENTERING: get get_header_detail"
	header_dic = get_header_detail(header,meta_doc)
	content_length = int(header_dic["Content-Length"])
	print "ENTERING: get_data"
	get_data(clientSocket,content_length,body,filename,meta_doc,header_dic)
	os.remove(meta_doc)

	sys.exit(0)
		
def resumeDownload(my_request,ip,port,meta_doc,filename):

	print "inside resumeDownload"
	print my_request




def check_if_filenameExist(filename):
	if os.path.exists(filename):
		os.remove(filename)

def HEAD_request_detail(header):
	newhead_dic = {}
	header_list = header.split("\r\n")
	status_code = header_list[0]
	check_status_code(status_code)
	for i in header_list[1:]:
		i = i.split(":")
		if i[0] != '':
			field,value = i[0],i[1]
			newhead_dic[field] = value
	return newhead_dic
def create_Brange(meta_doc_dic):
	byteRange_metadoc = meta_doc_dic["byte_recv"]
	byteRange = "Range: bytes={byteRange}-".format(byteRange = byteRange_metadoc)
	return byteRange.strip()+"\r\n"




def metaDoc_compare_newHeader(my_request,ip,port,meta_doc,filename):
	print "inside metaDoc_compare_newHeader"
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	clientSocket.connect((ip,port))
	clientSocket.send(my_request)
	head_recv = clientSocket.recv(1024)
	head_string = head_recv
	while head_recv:
		head_recv = clientSocket.recv(1024)
		head_string+= head_recv
	clientSocket.close()
	newhead_dic = HEAD_request_detail(head_string)

	meta_doc_dic = pickle.load(open(meta_doc,'r'))
	CL_metad, CL_newhd = meta_doc_dic["Content-Length"],newhead_dic["Content-Length"]
	E_metad, E_newhd = meta_doc_dic["ETag"],newhead_dic["ETag"]
	LM_metad,LM_newhd = meta_doc_dic["Last-Modified"],newhead_dic["Last-Modified"]
	

	if CL_metad == CL_newhd and E_metad == E_newhd:
		print "create BrangeString"
		Brange = create_Brange(meta_doc_dic)
		print "making new Brange request"
		my_request = make_request("GET",ip,port,path,Brange)
		print "Entering: resumeDownload"
		resumeDownload(my_request,ip,port,meta_doc,filename)
	elif CL_metad == CL_newhd and LM_metad == LM_newhd:
		print "create BrangeString"
		Brange = create_Brange(meta_doc_dic)
		print "making new Brange request"
		my_request = make_request("GET",ip,port,path,Brange)
		print "Entering: resumeDownload"
		resumeDownload(my_request,ip,port,meta_doc,filename)

	else:
		"Have to start download from start"
		downloadFromStart_or_resumeDownload("GET",my_request,ip,port,meta_doc,filename)


	







	


	


print "URL PARSED:"
parsed_url = parse_URL(sys.argv[-1])
print parsed_url
print "------------------------"
ip,port,path = parsed_url[0],parsed_url[1],parsed_url[2]

filename = sys.argv[2]
check_if_filenameExist(filename)
print "Creating meta_doc"
meta_doc = create_meta_doc(filename,path)


type_request = decide_if_HEAD_or_GET_request(meta_doc)
print "THIS IS THE REQUEST CHOSEN BASED ON IF META DOC EXISTS:"
my_request = make_request(type_request,ip,port,path,"")
print "CHOOSE TO RESUME OR DOWNLOAD FROM START"
downloadFromStart_or_resumeDownload(type_request,my_request,ip,port,meta_doc,filename)


	

