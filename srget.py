import sys
import socket as skt
import os
from urlparse import urlparse
import os.path
import cPickle as pickle

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
		
		downloadFromStart(my_request,ip,port,meta_doc,filename)
	if type_req == "HEAD":
		
		metaDoc_compare_newHeader(my_request,ip,port,meta_doc,filename)
		


def find_header_response(clientSocket):
	
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
	
	dic = {}
	header_list = header.split("\r\n")
	status_code = header_list[0]
	check_status_code(status_code)
	for i in header_list[1:]:
		i = i.split(":")
		field,value = i[0],i[1]
		dic[field] = value
	meta_doc_w = open(meta_doc,'wb')
	pickle.dump(dic,meta_doc_w)
	meta_doc_w.close()
	return dic

def get_data(clientSocket,content_length,body_so_far,filename,meta_doc,header_dic):
	data_recv = clientSocket.recv(1024)
	body = body_so_far + data_recv
	byte_recv = len(body)
	download = open(filename,'a')
	download.write(body)
	header_dic["byte_recv"] = byte_recv
	meta_doc_w = open(meta_doc,'w')
	pickle.dump(header_dic,meta_doc_w)
	while data_recv and content_length - byte_recv != 0:
		data_recv = clientSocket.recv(1024)
		download = open(filename,'a')
		meta_doc_w = open(meta_doc,'w')
		download.write(data_recv)
		header_dic["byte_recv"] = header_dic["byte_recv"] + len(data_recv)
		pickle.dump(header_dic,meta_doc_w)
	clientSocket.close()
	
def create_meta_doc(filename,path):
	unusable_path = path
	path = ""
	for i in unusable_path:
		if i.isalpha() or i.isdigit():
			path += i
	return filename+path+".txt"
		
def downloadFromStart(my_request,ip,port,meta_doc,filename):
	check_if_filenameExist(filename)
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	clientSocket.connect((ip,port))	
	clientSocket.send(my_request)
	header,body = find_header_response(clientSocket)
	header_dic = get_header_detail(header,meta_doc)
	content_length = int(header_dic["Content-Length"])
	get_data(clientSocket,content_length,body,filename,meta_doc,header_dic)
	os.remove(meta_doc)
	sys.exit(0)

def remove_header_in_resume(clientSocket,my_request):
	clientSocket.send(my_request)
	data_recv = clientSocket.recv(1024)
	data_so_far,body = data_recv,""
	header_not_found = True
   
	while header_not_found:
		data_recv = clientSocket.recv(1024)
		data_so_far += data_recv
		if "\r\n\r\n" in data_so_far:
			header, body = data_so_far.split("\r\n\r\n")
			header_not_found = False
	return body
		
def resumeDownload(my_request,ip,port,meta_doc,filename):
	clientSocket = skt.socket(skt.AF_INET,skt.SOCK_STREAM) 
	clientSocket.connect((ip,port))
	dic = pickle.load(open(meta_doc,'r'))
	body =remove_header_in_resume(clientSocket,my_request)
	download = open(filename,'a')
	download.write(body)
	mdw = open(meta_doc,'w')
	pickle.dump(dic,mdw)
	content_length = int(dic["Content-Length"])
	dic['byte_recv'] = len(body) + dic['byte_recv']
	data_recv = clientSocket.recv(1024)
	download.write(data_recv)
	dic["byte_recv"] = dic["byte_recv"] + len(data_recv)
	while data_recv:
		data_recv = clientSocket.recv(1024)
		download = open(filename,'a')
		meta_doc_w = open(meta_doc,'w')
		download.write(data_recv)
		dic["byte_recv"] = dic["byte_recv"] + len(data_recv)
		pickle.dump(dic,meta_doc_w)
	os.remove(meta_doc)
	clientSocket.close()

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
		Brange = create_Brange(meta_doc_dic)
		my_request = make_request("GET",ip,port,path,Brange)		
		resumeDownload(my_request,ip,port,meta_doc,filename)
	elif CL_metad == CL_newhd and LM_metad == LM_newhd:	
		Brange = create_Brange(meta_doc_dic)
		my_request = make_request("GET",ip,port,path,Brange)
		resumeDownload(my_request,ip,port,meta_doc,filename)
	else:
		downloadFromStart_or_resumeDownload("GET",my_request,ip,port,meta_doc,filename)



parsed_url = parse_URL(sys.argv[-1])

ip,port,path = parsed_url[0],parsed_url[1],parsed_url[2]

filename = sys.argv[2]

meta_doc = create_meta_doc(filename,path)

type_request = decide_if_HEAD_or_GET_request(meta_doc)

my_request = make_request(type_request,ip,port,path,"")

downloadFromStart_or_resumeDownload(type_request,my_request,ip,port,meta_doc,filename)