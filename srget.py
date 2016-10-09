import sys
import socket as skt
import os
from urlparse import urlparse
def error_message(error_number):
	if error_number ==1:
		print "Error: Incorrect input format."
		print "Use this format: srget -o <output file> [-c [<numConn>]] http://someurl.domain[:port]/path/to/file"


def check_argument_length_correct():
	#print len(sys.argv)
	#print sys.argv[1]
	#print sys.argv[3]
	if (len(sys.argv) == 4 and sys.argv[1] == "-o"):
		print "Input length correct"
		return True


	elif len(sys.argv) == 6 and sys.argv[1] == "-o" and sys.argv[3] == "-c":
		print "input length correct"
		return True
		
	else: 
		error_message(1)
		sys.exit(0)
		
check_argument_length_correct()





def parse_URL():
	url = urlparse(sys.argv[-1])
	if url.scheme == "http":
		print "correct it is a http address"
		#Format the string
	
	else:
		print "No it is not an http address"




parse_URL()














