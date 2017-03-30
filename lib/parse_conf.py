#!/usr/bin/env python
def parse_match_conf(conf):
    fd=open(conf,"r")
    ques=()
    que_attr={}
    for line in fd:
        line=line.strip()
	if line and not line.startswith("#"):
	    #print line
            (key,value)=line.split("=")
            key=key.strip()
            value=value.strip()
	    #print key,"=>", value
            if key=="Que":
                ques=value.split(",")
		###print "ques is ", ques
	    if ques:
		for que in ques:
                    if key.startswith(que):
			if not que_attr.has_key(que):
                            que_attr[que]={}
                        (que_name, attr)=key.split(".")
		        que_attr[que][attr]=value
    fd.close()
    return que_attr

def parse_server_conf(conf):
    fd=open(conf, "r")
    service={}
    for line in fd:
	line=line.strip()
	if line and not line.startswith("#"):
	    (key,value)=line.split("=")
	    key=key.strip()
	    value=value.strip()
	    if key.find("host")>=0: 
		service[key]=value
	    elif key.find("port")>=0:
		service[key]=int(value)
    return service

