# srget
The srget does not support concurrent downloading. It is used with command line: python srget.py -o filename url.
I have some problems with she bang and terminal so I am not sure if you are able to use it. I put #!/usr/bin/en/env python 
,at the top of the sublime file. And in CP 1 and 2, I did not have shebang.

I used Cpickle for the second checkpoint and I did everything in functions, in the third I used asyncore, unsuccesful with 
concurrent downloading. I did work with normal DL, but merging the files together was a problem, because they got updated to their correct sizes
first after the program had stopped running, so I dropped it. And deliver instead asyncore with normal dl and resume.

