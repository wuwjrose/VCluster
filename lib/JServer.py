#!/usr/bin/env python

from SocketServer import (ThreadingTCPServer as TTCP,
                          StreamRequestHandler as SRH)
import json
import os, sys
import logging

HOST = ''
PORT = 27015
ADDR = (HOST, PORT)

logging.basicConfig(
#    filename = os.path.join(os.getcwd(), 'logJServer.log'),
    format = '%(asctime)s %(levelname)s:%(module)s:%(message)s',
    level = logging.DEBUG)
LOG = logging.getLogger(__name__)
#LOG.addHandler(logging.StreamHandler(sys.stderr))

def display(displaying):
    if len(displaying) >= 256:
        return '<data not shown>'
    else:
        return displaying

# For reusing the same allowed host:
class ReusableTTCP(TTCP):
    allow_reuse_address = True

class JServerRequestHandler(SRH):
    received = True # dummy
    sending = ''
    data = ''
    
    # Usually you should call the 'main' procedure through this method.
    # What you've received and JSON-decoded(loaded), and would be encoded
    # (dumped into a string) and sent, is in the variable self.data .
    def furtherCallback(self):
        # When not implemented:
        pass
    
    def JSONDecode(self, *args):
        # String (when received) to JSON
        # When not implemented:
        if args:
            data = args[0]
        else:
            data = self.received
        try:
            ret = json.loads(data)
        except Exception, e:
            LOG.exception(e)
            ret = ()
        finally:
            return ret
    
    def JSONEncode(self, *args):
        # JSON to string (then send the string)
        # When not implemented:
        if args:
            data = args[0]
        else:
            data = self.data
        try:
            ret = json.dumps(data)
        except Exception, e:
            LOG.exception(e)
            ret = ''
        finally:
            return ret
    
    def handle(self):
        clnt = self.clnt = str(self.client_address)
        LOG.info('%s connected' % clnt)
        while self.received:
            self.received = self.rfile.readline().strip() # real data
            self.displaying = self.received
            if len(self.displaying) >= 256:
                self.displaying = '<data not shown>'
            LOG.debug('%s RCVD: %s' % (self.clnt, display(self.received)))
            if self.received == '':
                LOG.info('%s Blank string received, stop handling' % self.clnt)
                return
            
            # If furtherCallback() wasn't overridden, then it will just repack
            # and send unchanged JSON objects.
            # Like the "Turret Factory" in Portal 2.
            self.data = self.JSONDecode(self.received)
            self.furtherCallback()
            self.sending = self.JSONEncode(self.data)
            LOG.debug('%s SEND: %s' % (self.clnt, display(self.sending)))
            self.wfile.write('%s%s' % (self.sending, os.linesep))
            if not self.sending:
                LOG.info('%s Nothing to send, stop handling' % self.clnt)
                return

def main():
    class MyRequestHandler(JServerRequestHandler):
        import time
        
        def furtherCallback(self):
            print self.time.strftime('%Y-%m-%d %H:%M:%S')+' '+\
                  '%s JSON: %s' % (self.clnt,display(self.data))
            LOG.debug('%s JSON: %s' % (self.clnt, self.data))

    tcpServ = ReusableTTCP(ADDR, MyRequestHandler)
    tcpServ.daemon_threads = True
    try:
        tcpServ.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        # When shutting down the whole thing:
        LOG.info('exiting')
        tcpServ.shutdown()

if __name__ == '__main__':
    main()
