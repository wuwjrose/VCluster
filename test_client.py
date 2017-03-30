#!/usr/bin/env python
from lib import *
def main():
    jc = JClient(host='127.0.0.1', port=27015, bufsize=1024)
    #data_send = [1,2,(3,4)]
    hash_a={"l1":10,"l2":20}
    hash_b={"l3":30,"l4":40}
    data_send = [1,{"a":hash_a,"b":hash_b},(3,4)]
    data_recv = jc.oneRequest(data_send)
    print data_recv
    jc.close()

if __name__ == '__main__':
    main()
