#!/usr/bin/env python
from lib import *
def main():
    class MyRequestHandler(JServerRequestHandler):
        def furtherCallback(self):
            print '%s JSON: %s' % (self.clnt, self.data)
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
