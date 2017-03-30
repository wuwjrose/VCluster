#!/usr/bin/env python
from lib import *
import random
import ast
def main():
    class MyRequestHandler(JServerRequestHandler):
        def furtherCallback(self):
	    msg=self.data
	    if type(msg)!=type(dict()):
		return
            print '%s => %s XXX' % (self.clnt, self.data)
	    print "further"
	    msg_type=msg["msg_type"]
	    print "msg_type is ", msg_type
	    if msg_type=="request":
	        pbs_ques=msg["msg_content"]
	        que_info={}
                for pbs_que in pbs_ques:
	    	    que_info[pbs_que]={}
	    	    #que_info[pbs_que]['Run']=random.randint(1,50)
	    	    que_info[pbs_que]['Run']=10
	    	    #que_info[pbs_que]['Que']=random.randint(1,100)
	    	    que_info[pbs_que]['Que']=5
	        reply_msg={}
	        reply_msg['msg_type']="reply"
	        reply_msg['msg_content']=que_info
		print reply_msg
                self.data=reply_msg
	    elif msg_type=="reply":
		max_run=msg["msg_content"]
		for que in max_run.keys():
		    print que, " ", max_run[que]["MaxRun"]
            LOG.debug('%s JSON: %s' % (self.clnt, self.data))

    HOST = ''
    PORT = 27015
    ADDR = (HOST, PORT)
    tcpServ = TTCP(ADDR, MyRequestHandler)
    tcpServ.daemon_threads = True
    tcpServ.serve_forever()
    # When shutting down the whole thing:
    #tcpServ.shutdown()

if __name__ == '__main__':
    main()
