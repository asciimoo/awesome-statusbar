#!/usr/bin/python

import string, time, sys, os, _statgrab, re


#CONSTANTS
NET_INTERFACES = []
NUM_OF_CPUS = 1
NEEDED_NET_INTERFACES = ['eth1', 'tun0']
PRINT_PREFIX = '0 widget_tell top '

#downloaded bytes ordered by interfaces
NET_D = {}
#uploaded bytes ordered by interfaces
NET_U = {}
NET_LAST_D = {}
NET_LAST_U = {}

try:
    cpu_num = 1
    f = open('/proc/stat', 'r')
    for i in f:
        if re.match('^cpu[1-9].', i):
            cpu_num = cpu_num+1
    f.close()
    NUM_OF_CPUS = cpu_num
except:
    pass
mem = {}
fs = {}

_statgrab.py_sg_init()
def initNetIfaces():
    network_ifaces = _statgrab.py_sg_get_network_iface_stats()
    for i in network_ifaces:
        NET_INTERFACES.append(i['interface_name'])

    for i in NET_INTERFACES:
        netstats = _statgrab.py_sg_get_network_io_stats()
        for j in netstats:
            if j['interface_name'] == i:
                NET_D[i] = NET_LAST_D[i] = j['rx']
                NET_U[i] = NET_LAST_U[i] = j['tx']

def getCPUUsage():
    cpuInfo = _statgrab.py_sg_get_cpu_percents()
    cpuPerc = (cpuInfo['kernel']+cpuInfo['user'])*NUM_OF_CPUS
    if cpuPerc > 100:
        return 100
    return cpuPerc

def getFSUsage():
    fsInfo = _statgrab.py_sg_get_fs_stats()
    for i in fsInfo:
        fs[i['mnt_point']] = float(i['used_blocks'])/i['total_blocks']*100
    return fs

def getWorkingNetInterfaces():
    ret = []
    network_ifaces = _statgrab.py_sg_get_network_iface_stats()
    for i in ifaces:
        if i['up'] is 1:
            ret.append(i['interface_name'])
    return ret

def getMemUsage():
    #from /proc/meminfo without _statgrab
    f = open('/proc/meminfo', 'r')
    for i in f:
        if re.match(r'^Active:', i):
            mem_used_arr = re.findall(r'\d+', i)
            mem_used = int(mem_used_arr[0])
    f.close()
    return mem_used

def getMemUsagePercent():
    #from /proc/meminfo without _statgrab
    f = open('/proc/meminfo', 'r')
    for i in f:
        if re.match(r'^Active:', i):
            mem_used_arr = re.findall(r'\d+', i)
            mem_used = int(mem_used_arr[0])
        if re.match(r'^MemTotal:', i):
            mem_total_arr = re.findall(r'\d+', i)
            mem_total = int(mem_total_arr[0])
    f.close()
    return float(mem_used)/mem_total*100

def getDownDiff(interface):
    if interface not in NET_INTERFACES:
        return 0
    netstats = _statgrab.py_sg_get_network_io_stats()
    for i in netstats:
        if i['interface_name'] == interface:
            NET_LAST_D[interface] = NET_D[interface]
            NET_D[interface] = i['rx']
    return NET_D[interface] - NET_LAST_D[interface]

def getUpDiff(interface):
    if interface not in NET_INTERFACES:
        return 0
    netstats = _statgrab.py_sg_get_network_io_stats()
    for i in netstats:
        if i['interface_name'] == interface:
            NET_LAST_U[interface] = NET_U[interface]
            NET_U[interface] = i['tx']
    return NET_U[interface] - NET_LAST_U[interface]



"""
#{'cache': 325234688L, 'total': 1051410432L, 'free': 240627712L, 'used': 810782720L}
#for k,v in mem.items():
#    print v


fs =  getFSUsage()
for k,v in fs.items():
    if(v > 90):
        print "[!]Warning %s - %f%%" % (k, v)


working_interfaces = getWorkingNetInterfaces()
for i in NEEDED_NET_INTERFACES:
    if i not in working_interfaces:
        print "Warning %s is not working" % i

#print _statgrab.
#print _statgrab.
#print _statgrab.
#print _statgrab.

sys.exit(0)

{'tx': 12219206L, 'rx': 75116040L, 'systime': 1216633145, 'ipackets': 135407L, 'oerrors': 0L, 'collisions': 0L, 'opackets': 101984L, 'ierrors': 5L, 'interface_name': 'eth1'}
"""
initNetIfaces()
while True:
    #clock
    act_time = time.strftime("%y.%m.%d %H:%M:%S")
    #mem_usage
    mem_usageK = getMemUsage()
    if mem_usageK > 1024:
        mem_usage = "%dM" % (mem_usageK/1024)
    else:
        mem_usage = "%dK" % mem_usage
    #cpu_graph / cpu_usage
    cpu_usage = getCPUUsage()
    #down_graph / down_usage
    down = getDownDiff('eth1')
    if down >= 1024:
        down_text = "%.1fK" % (down/1024)
    else:
        down_text = "%.1fB" % down
    #up_graph / up_usage
    up = getUpDiff('eth1')
    if up >= 1024:
        up_text = "%.1fK" % (up/1024)
    else:
        up_text = "%.0fB" % up
    p = os.popen("/usr/bin/awesome-client", "w")
    p.write("0 widget_tell top clock text %s\n\
            0 widget_tell top mem_usage text %s\n\
            0 widget_tell top cpu_graph data cpu_graph %d\n\
            0 widget_tell top cpu_usage text %.1f%%]\n\
            0 widget_tell top down_graph data down_graph %.1f]\n\
            0 widget_tell top up_graph data down_graph %.1f\n\
            0 widget_tell top net_usage text %s/%s]\n" %
            (act_time, 
                mem_usage, 
                cpu_usage,
                cpu_usage,
                down,
                up,
                down_text,
                up_text))
    p.close()
    #print "%scpu_graph graph %.0f" % (PRINT_PREFIX, getCPUUsage())
    time.sleep(1)
