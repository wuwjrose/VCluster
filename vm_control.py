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
            vm_types=msg["msg_content"]
	    if msg_type=="request":
	        vm_info={}
		vm_info["limit"]={}
		vm_info["info"]={}
	        vm_info["limit"]["Phost"]=10
	        vm_info["limit"]["CPU"]=40
                for vm_type in vm_types:
		    vm_info["info"][vm_type]={}
  		    vm_info["info"][vm_type]["Active"]=random.randint(-5,5)
	        reply_msg={}
	        reply_msg['msg_type']="reply"
	        reply_msg['msg_content']=vm_info
                self.data=reply_msg
	    elif msg_type=="reply":
		run_info=msg["msg_content"]
		for vm_type in run_info.keys():
		    print vm_type, ": TotalRun=", run_info[vm_type]["TotalRun"], "IpList=",run_info[vm_type]["IpList"]
            LOG.debug('%s JSON: %s' % (self.clnt, self.data))

    HOST = ''
    PORT = 27016
    ADDR = (HOST, PORT)
    tcpServ = TTCP(ADDR, MyRequestHandler)
    tcpServ.daemon_threads = True
    tcpServ.serve_forever()
    # When shutting down the whole thing:
    #tcpServ.shutdown()

if __name__ == '__main__':
    main()
