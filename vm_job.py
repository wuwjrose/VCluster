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
            print '%s => %s' % (self.clnt, self.data)
	    msg_type=msg["msg_type"]
	    if msg_type=="request":
	        pbs_ques=msg["msg_content"]
	        vm_que_info={}
                for pbs_que in pbs_ques:
		    vm_que_info[pbs_que]={}
	    	    #vm_que_info[pbs_que]['Run']=random.randint(1,50)
	    	    #vm_que_info[pbs_que]['Que']=random.randint(1,100)
	    	    vm_que_info[pbs_que]['Run']=2
	    	    vm_que_info[pbs_que]['Que']=8
	    	    vm_que_info[pbs_que]['IpList']=["192.168.10.1","192.168.10.2"]
	        reply_msg={}
	        reply_msg['msg_type']="reply"
	        reply_msg['msg_content']=vm_que_info
                self.data=reply_msg
            LOG.debug('%s JSON: %s' % (self.clnt, self.data))
    HOST = ''
    PORT = 27021
    ADDR = (HOST, PORT)
    tcpServ = ReusableTTCP(ADDR, MyRequestHandler)
    tcpServ.daemon_threads = True
    tcpServ.serve_forever()
    # When shutting down the whole thing:
    #tcpServ.shutdown()

if __name__ == '__main__':
    main()
