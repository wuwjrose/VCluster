#!/usr/bin/env python
import ast
import time
import random
from lib import *
import logging
from daemon import runner

INVALID_STATUS_LIMIT=20
POLL_INTERVAL=30
def get_logger():
    logger = logging.getLogger('vm_match')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler("/var/log/vm_match.log")
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        #self.stdout_path = '/dev/null'
        #self.stderr_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        #self.stdout_path = '/tmp/vm_match.out'
        #self.stderr_path = '/tmp/vm_match.err'
        self.pidfile_path = '/tmp/vm_match.pid'
        self.pidfile_timeout = 5

    def run(self):
        logger = get_logger()
        invalid_vm_status_count={}
        while True:
            run_match(logger,invalid_vm_status_count)
            time.sleep(POLL_INTERVAL)

logging.basicConfig() 
#logger = get_logger()


def get_pbs_que_info(pbs_ques, pbs_server_host, pbs_server_port, logger):
    ## the following code will request information from pbs_server, vm_controller, and vm_job_controller   
    #request pbs que information from pbs server, including running/que jobs for each que
    pbs_que_info={}
    try:
        pbs_client = JClient(host=pbs_server_host, port=pbs_server_port, bufsize=1024)
        msg={}
        msg["msg_type"]="request"
        msg["msg_content"]=pbs_ques
        msg_rec = pbs_client.oneRequest(msg)
        pbs_que_info=msg_rec["msg_content"]
        '''
        for que_name in pbs_ques:
            print que_name, " runing:", pbs_que_info[que_name]['Run']
            print que_name, " queing:", pbs_que_info[que_name]['Que']
        '''
        pbs_client.close()
    except Exception, e:
        print "can not connect to pbs_que server"
        logger.exception(e)
    return pbs_que_info

def get_vm_info(vm_types, vm_control_host, vm_control_port, logger):
    #request vm information from vm controller, including vm limit, and active vm for each image type
    vm_info={}
    try:
        vm_client = JClient(host=vm_control_host, port=vm_control_port, bufsize=1024)
        msg={}
        msg["msg_type"]="request"
        msg["msg_content"]=vm_types
        msg_rec = vm_client.oneRequest(msg)
        vm_info=msg_rec["msg_content"]
        '''
        print "vm_limit: Phost", vm_info["limit"]["Phost"]
        print "vm_limit: CPU", vm_info["limit"]["CPU"]
        for vm_type in vm_types:
            print vm_type, " active:", vm_info["info"][vm_type]['Active']
        '''
        vm_client.close()
    except Exception, e:
        print "can not connect to vm_info server"
        logger.exception(e)
    return vm_info

def get_vm_que_info(pbs_ques, vm_job_host, vm_job_port, logger):
    #request job information from vm job controller, including running/que jobs for each que, and ip_list 
    # of the running vm instances for each que
    vm_que_info={}
    try:
        job_client = JClient(host=vm_job_host, port=vm_job_port, bufsize=1024)
        msg={}
        msg["msg_type"]="request"
        msg["msg_content"]=pbs_ques
        msg_rec = job_client.oneRequest(msg)
        vm_que_info=msg_rec["msg_content"]
        '''
        for pbs_que in pbs_ques:
            print pbs_que, "  running:", vm_que_info[pbs_que]['Run']
            print pbs_que, "  queing:", vm_que_info[pbs_que]['Que']
            print pbs_que, "  iplist:", vm_que_info[pbs_que]['IpList']
        '''
        job_client.close()
    except Exception, e:
        print "can not connect to vm_job server"
        logger.exception(e)
    return vm_que_info

def match_making():
    ##the following code make match decisions
    return 

def advertise(pbs_ques, vm_types, img2q, que_weight, vm_que_info, pbs_que_info, vm_info, service, logger):
    ## the following code send replies to pbs_server and vm_controller
    # send reply to pbs_server
    pbs_client = JClient(host=service["pbs_server_host"], port=service["pbs_server_port"], bufsize=1024)
    msg_send={}
    msg_send['msg_type']="reply"
    que_info={}
    for pbs_que in pbs_ques:
        que_info[pbs_que]={}
        que_info[pbs_que]['MaxRun']=int(round(int(vm_info['limit']['CPU'])*que_weight[pbs_que]))
        msg_send['msg_content']=que_info
        msg_rec=pbs_client.oneRequest(msg_send)
        print "sending msg to pbs_que ",msg_rec
        logger.info("sending msg to pbs_que %s"%str(msg_rec))
    pbs_client.close()

    # send reply to vm_controller
    vm_client = JClient(host=service["vm_control_host"], port=service["vm_control_port"], bufsize=1024)
    msg_send={}
    msg_send['msg_type']="reply"
    run_info={}
    for vm_type in vm_types:
        ques=img2q[vm_type]
        run_info[vm_type]={}
        run_info[vm_type]['TotalRun']=0
        run_info[vm_type]['IpList']=[]
        for que in ques:
            TotalRun=int(pbs_que_info[que]['Run'])+int(pbs_que_info[que]['Que'])
            if TotalRun<=int(que_info[que]['MaxRun']):
                TR=TotalRun
            else:
                TR=int(que_info[que]['MaxRun'])
            run_info[vm_type]['TotalRun']+=TR
            run_info[vm_type]['IpList']+=vm_que_info[que]['IpList']
    print "run_info ", run_info
    msg_send['msg_content']=run_info
    msg_rec=vm_client.oneRequest(msg_send)
    print "sending msg to vm_control ", msg_rec
    print "\n"
    logger.info("sending msg to vm_control %s"%str(msg_rec))
    vm_client.close()
    
def run_match(logger,invalid_vm_status_count):
    CONF="/root/VirtualCluster/match.conf"
    que_attr=parse_match_conf(CONF)
    service=parse_server_conf(CONF)
    #print "que_attr=", que_attr
    #print "service=", service
    pbs_ques=que_attr.keys()
    pbs_ques.sort()
    vm_types=[]
    img2q={}
    que_weight={}
    total_weight=0
    for que in pbs_ques:
        vm_type=que_attr[que]['image']
        total_weight+=int(que_attr[que]['weight'])
        if not vm_type in vm_types:
            vm_types.append(vm_type)
        if img2q.has_key(vm_type):
            img2q[vm_type].append(que)
        else:
            img2q[vm_type]=[]
            img2q[vm_type].append(que)

    for que in pbs_ques:
        que_weight[que]=int(que_attr[que]['weight'])*1.0/total_weight
    print "pbs_ques=", pbs_ques
    print "vm_types=", vm_types
    print "que_weight=",que_weight
    print "img2q=", img2q
    
    log_msg="pbs_ques="+str(pbs_ques)+"\tvm_types="+str(vm_types)+"\tque_weight="+str(que_weight)+"\timg2q="+str(img2q)
    logger.info(log_msg)
    
    pbs_que_info=get_pbs_que_info(pbs_ques, service["pbs_server_host"], service["pbs_server_port"], logger=logger)
    print "pbs_que_info: ", pbs_que_info
    log_msg="received pbs_que_info : "+str(pbs_que_info)
    logger.info(log_msg)
    
    vm_que_info=get_vm_que_info(pbs_ques, service["vm_job_host"], service["vm_job_port"], logger=logger)
    print "vm_que_info: ", vm_que_info
    log_msg="received vm_que_info : "+str(vm_que_info)
    logger.info(log_msg)
    
    vm_info=get_vm_info(vm_types, service["vm_control_host"], service["vm_control_port"], logger=logger)
    print "vm_info: ", vm_info
    log_msg="received vm_control_info : "+str(vm_info)
    logger.info(log_msg)
    
    active_vm_types=[]
    for vm_type in vm_types:
        if invalid_vm_status_count.has_key(vm_type) and invalid_vm_status_count[vm_type]>INVALID_STATUS_LIMIT:
            print "ALERT: %s exceeds the limit of invalid vm status.."%vm_type
            log_msg="ALERT: %s exceeds the limit of invalid vm status.."%str(vm_type)
            logger.error(log_msg)
    if len(pbs_que_info)!=0 and len(vm_que_info)!=0 and len(vm_info)!=0:
        for vm_type in vm_types:
            if vm_info["info"][vm_type]['Active']>=0:
                active_vm_types.append(vm_type)
                invalid_vm_status_count[vm_type]=0
            else:
                if invalid_vm_status_count.has_key(vm_type):
                    invalid_vm_status_count[vm_type]+=1
                else:
                    invalid_vm_status_count[vm_type]=1
                print vm_type, " does not have a clear status yet."
                log_msg= str(vm_type)+ " does not have a clear status yet."
                logger.info(log_msg)
        if len(active_vm_types)>0:
            advertise(pbs_ques, active_vm_types, img2q, que_weight, vm_que_info,pbs_que_info, vm_info, service,logger)
        else:
            print "non of the vm types detected a clear status, will pass the advertising this time...\n"
            logger.info("non of the vm types detected a clear status, will pass the advertising this time...")
    else:
        print "some of the services may be down, havn't collected enough information to do the match!"
        logger.warning("some of the services may be down, havn't collected enough information to do the match!")

if __name__ == '__main__':
    app = App()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
