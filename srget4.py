#!/usr/bin/en/env python
import sys,os
import asyncore, socket
import logging
from cStringIO import StringIO
from urlparse import urlparse
def check_argumentLength():
    if (len(sys.argv) == 4 and sys.argv[1] == "-o"):
        return True
    elif len(sys.argv) == 6 and sys.argv[1] == "-o" and sys.argv[3] == "-c":
        return True
    else: 
        print "Arguments put into command line is incorrect"
        sys.exit(1)

 
def make_request(req_type, what, details, ver="1.1"):
    NL = "\r\n"
    req_line = "{verb} {w} HTTP/{v}".format(
        verb=req_type, w=what, v=ver
    )
    print req_line
    details = [
        "{name}: {v}".format(name=n,v=v) for (n,v) in details.iteritems()
    ]
    detail_lines = NL.join(details)
    full_request = "".join([req_line, NL, detail_lines, NL, NL])
    return full_request
def parse_URL(url):
    url = urlparse(url)
    host,port,path = url.hostname,url.port,url.path
    ip = socket.gethostbyname(host)
    if path =="":
        path = "/"
    return (ip,port,path)
def decide_if_HEAD_or_GET_request(meta_doc,filename):
    
    if os.path.exists(meta_doc) and os.path.exists(filename):
        return "HEAD"
    else:
        return "GET"
def create_meta_DocName(filename,path):
    return filename+".rdoc"+".txt"

def metaDoc_sameAs_newHeader(my_request,rdl,ip,port):
    same_content = True
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    clientSocket.connect((ip,port))
    clientSocket.send(my_request)
    head_recv = clientSocket.recv(1024)
    head_string = head_recv
    while head_recv:
        head_recv = clientSocket.recv(1024)
        head_string+= head_recv
    clientSocket.close()
    head_string = head_string.split("\r\n")
    for i in head_string[1:]:
        i = i.split(':')
        if i[0] == "Content-Length":
        
            if i[1].strip() != rdl[0].strip():
                same_content= False
             
        elif i[0] == "Last-Modified":
            
            if i[1].strip() != rdl[1].strip():
                same_content = False
             

        elif i[0] == "ETag":
            
            if i[1].strip() != rdl[2].strip():
                same_content =False

    return same_content
    
    


def make_request2(GET_or_HEAD,ip,port,path,Brange,DEFAULT_PORT =80):
    if port == None:
        port = DEFAULT_PORT

    return ("{GET_or_HEAD} {path} HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: Close\r\n{Brange}Accept: text/html\r\n\r\n".format(GET_or_HEAD = GET_or_HEAD,path = path,Brange =Brange,ip = ip,port = str(port)))



def downloadFromStart_or_resumeDownload(type_req,ip,path,port,filename,meta_doc):
    print "inside downloadFromStart_or_resumeDownload"
    print type_req
    Brange = 0
    my_request = make_request2('GET',ip,port,path,Brange)
    if type_req == "GET":
        print "Removing filename"
        if os.path.exists(filename):
            os.remove(filename)
        return my_request,Brange
        
    if type_req == "HEAD":
        print "Opening meta_doc_r"
        meta_doc_r = open(meta_doc,'r')
        rdl = meta_doc_r.readlines()
        print 'create HEAD request'
        my_request = make_request('HEAD', path,
            {'Host': ip,
             'Connection': 'close'}
        )

        print "Entering metaDoc_compare_newHeader"
        same_content = metaDoc_sameAs_newHeader(my_request,rdl,ip,port)
        if same_content:
            Brange = rdl[-1].strip()
            Brange = os.path.getsize(filename)
            byteRange = "Range: bytes={byteRange}-\r\n".format(byteRange = Brange)
            my_request = make_request2('GET',ip,port,path,byteRange)
            
            print Brange

        return my_request,Brange

        

def write_header_respone(data_recv,meta_doc_w):
    content_length = -1
    header,body = data_recv.split("\r\n\r\n")
    print header
    NL = "\r\n"
    for i in header.split("\r\n")[1:]:
        i = i.split(":")
        field,atrribute = i[0],i[1]
        if field == "Content-Length":
            content_length = int(atrribute)
            
            meta_doc_w.write(atrribute+NL)
                
        elif field == "ETag":
           
            meta_doc_w.write(atrribute+NL)

        elif field == "Last-Modified":
            
            meta_doc_w.write(atrribute+NL)
    return body,content_length

#HTTPClient inherits from asyncore.dispatcher
class HTTPClient(asyncore.dispatcher):
    ## Size of the buffer for each recv
    RECV_CHUNK_SIZE = 8192
 
    def __init__(self, url,filename):
        asyncore.dispatcher.__init__(self)
        print "check_argumentLength"
        #check_argumentLength()
        print "create filename"
        self.filename = filename
        print "Parse url"
        self.ip,self.port,self.path  = parse_URL(url)
        print "create_meta_DocName"
        self.meta_doc = create_meta_DocName(self.filename,self.path)
        print "decide_if_HEAD_or_GET_request"
        self.type_request = decide_if_HEAD_or_GET_request(self.meta_doc,self.filename)
        print "downloadFromStart_or_resumeDownload"
        my_request,Brange = downloadFromStart_or_resumeDownload(self.type_request,self.ip,self.path,self.port,self.filename,self.meta_doc)
        
        
        self.full_string = ''
        # Create a TCP socket to host at the right port
        print "connecting"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.ip, self.port))
        self.header_found = False
        self.full_string = ""
        self.head , self.body= "", ""
        print "open meta doc w"
        self.meta_doc_w = open(self.meta_doc,'a')
        print "open filename doc w"
        self.filename_w = open(self.filename,'a')
       
        self.len_recv_bytes = int(Brange)
        self.content_length = -1
        self.EveryByteDownloaded = False
        print self.len_recv_bytes
       
        # Create recv buffer and send buffer
        (self.recvbuf, self.sendbuf) = ("", "")
        # Make an initial request & deliver it
        
        self.port = int(self.port)
        print my_request
        self.write(my_request)
        
        

 
    def write(self, data):
        """ Schedule to deliver data over the socket """
        self.sendbuf += data
 
    def handle_connect(self):
        pass
        
 
    def handle_close(self):
        print "In handle_close"
        print "removing meta_doc"

        print "total_bytes: "+str(self.len_recv_bytes)
        os.remove(self.meta_doc)
        self.close()

 
    def writeable(self):
        """ Check if there is anything to send """
        return len(self.sendbuf) > 0
 
    def handle_write(self):
        bytes_sent = self.send(self.sendbuf)
        self.sendbuf = self.sendbuf[bytes_sent:]
 
    def handle_read(self):
        
        recv_bytes = self.recv(HTTPClient.RECV_CHUNK_SIZE)
        self.full_string += recv_bytes
        if not self.header_found and "\r\n\r\n" in self.full_string:
            self.header_found = True
            print "write_header_respone"
            self.body, self.content_length = write_header_respone(self.full_string,self.meta_doc_w)
            self.filename_w.write(self.body)
            self.len_recv_bytes += len(self.body)
            self.meta_doc_w.write(str(self.len_recv_bytes)+"\r\n")
        elif self.header_found and not self.EveryByteDownloaded:
            self.filename_w.write(recv_bytes)
            self.len_recv_bytes += len(recv_bytes)
            #self.meta_doc_w.write(str(self.len_recv_bytes)+"\r\n")
            



 
if __name__ == "__main__":
    
    clients = [HTTPClient("http://10.27.8.20:8080/bigfile.xyz","ok.txt")]
    asyncore.loop()