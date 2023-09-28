#!/usr/bin/env python2
'''Utilities for performing Metamac experiments.
Requires Python 2.X for Fabric.
Author: Domenico Garlisi and Alice Lo Valvo
'''

'''

USRP su hendrix

$ ssh fabrizio@hendrix.local
$ cd /home/fabrizio/work/flex5gware/5gppp_rome/srsLTE/

per avviare tutto bisogna lanciare:
$ sh run_enb.sh

e poi anche far partire un iperf client:

$ iperf -c 127.0.0.1 -p 2000 -i 1 -t 100000

si dovrebbero vedere sul canale 6ms di traffico e 4ms di idle 


WMP setup

setu-up network
fab -f fab_wmp_lte.py -u root -H alix02,alix03 setup_testbed:alix02

create network
fab -f fab_wmp_lte.py -u root -H alix02,alix03 network:alix02

load correct radio program
fab -f fab_wmp_lte.py -u root -H alix03 load_active_radio_program

run traffic
fab -f fab_wmp_lte.py -u root -H alix02 start_iperf_server
fab -f fab_wmp_lte.py -u root -H alix03 start_iperf_client:alix02,60000,10M
fab -f fab_wmp_lte.py -u root -H alix03,alix02 stop_iperfd

usare il bytecode-manager per settare la maschera del TDMA wmp
ad ogni bit corrisponde uno slot da un millisecondo del frame da 10ms
1 = slot pieno (WIFI presente)
0 = slot vuoto (WIFI non presente)
bytecode-manager --set-tdma-mask 1100110011


'''

import os
import os.path
import datetime
import random

import fabric.api as fab
import fabric.utils
from StringIO import StringIO
import json
import time
import numpy
DEFAULT_MAC = 'tdma-4.txt'

def shift(l,n):
	return l[n:] + l[:n]

def get_last_psucc(psucc_list,L,est_slot):
	mask=""
	for x in psucc_list:
		if x > 0.5:
			maskval=1
		elif numpy.isinf(x):
			maskval=0
		else:
			maskval=0
		mask="{}{}".format(mask,maskval)

	mask_int = [ int(x) for x in list(mask)]
		mask_sum=0
		n_shift=0
		for x in list(mask_int):
			mask_sum+=x

		target_mask= [1]*mask_sum + [0]*(L-mask_sum)

		while n_shift < L:
			if mask_int != target_mask:
				mask_int=shift(mask_int,-1)
				psucc_list=shift(psucc_list,-1)
				n_shift=n_shift+1
			else:
				break

	psucc = psucc_list[ mask_sum - 1 ]
	return psucc

def update_pattern(mask_int, L, est_slot):
	mask_sum=0
	n_shift=0
	for x in list(mask_int):
		mask_sum+=x

	target_mask= [1]*mask_sum + [0]*(L-mask_sum)
	print("target_mask={}".format(target_mask))
	print("mask_int={}".format(mask_int))

	while n_shift < L:
		if mask_int != target_mask:
			mask_int=shift(mask_int,-1)
			n_shift=n_shift+1;
		else:
			break;

	if n_shift < L:
		if mask_sum < est_slot and est_slot < L:
			print("---------")
			print(mask_int)
			print(mask_sum)
			print(est_slot)
			print("---------")

			for i_mask in range(mask_sum,est_slot):
				print(i_mask)
				mask_int[i_mask]=1

			print n_shift
			mask_int=shift(mask_int,n_shift-(mask_sum-est_slot))
	print("mask_int={}".format(mask_int))
	return mask_int


# def check_all_hosts(interface):
#     hosts = ['alix{0}'.format(i) for i in xrange(1, 21)]
#     with fab.settings(skip_bad_hosts=True, abort_on_prompts=True):
#         results = fab.execute(check_host, interface, hosts=hosts)
#     print '== RESULTS =='
#     for host, has_interface in results.iteritems():
#         if has_interface == True:
#             print '{0} has {1}'.format(host, interface)
#     print '== END RESULTS =='

# def check_host(interface):
#     with fab.settings(warn_only=True):
#         try:
#             return fab.run('ip link show | grep {0}'.format(interface)).succeeded
#         except SystemExit: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
#             return False


'''
RADIO PROGRAM MANAGMENT
'''
# def load_active_radio_program(mac='TDMA_LTE_3.txt'):
#     '''Loads the given MAC protocol onto the WMP firmware. Paths are relative to the
#     '''
#     fab.run('bytecode-manager -l 2 -m ~/wmp-lte/{0}'.format(mac))
#     fab.run('sleep 2')
#     fab.run('bytecode-manager -a 2')
#
# def ap_ify(path):
#     root, ext = os.path.splitext(path)
#     return root + '.ap' + ext


'''
STATISTICS MANAGEMENT
'''
# def stop_read_statistics(trialnum):
#
#     #with fab.settings(warn_only=True):
#     #    fab.run("kill $(ps aux | grep '[p]ython /root/toco/wmp_read_statistics/read_tx_statistics.py' | awk '{print $2}')")
#
#     fab.local('mkdir -p data')
#     localname = 'data/{0}-wmp_statistics_log-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
#     with fab.settings(warn_only=True):
#     #fab.run('cat iperf.out | grep "0,-" | grep -v nan > iperf2.out')
#         fab.get(remote_path='wmp_statistics_log.csv', local_path=localname)
#         #fab.get(remote_path='iperf2.out', local_path=localname_f)
# 	#fab.run('rm iperf2.out')


'''
IPERF TRAFFIC MANAGEMENT
'''
# def start_iperf_server():
#     with fab.settings(warn_only=True):
#         fab.run('killall iperf')
#     fab.local('sleep 3')
#     fab.run('nohup iperf -i 1 -s -u -p12345 -y C > iperf.out 2> iperf.err < /dev/null &', pty=False)
#
#     localname = 'monitor.out'
#     remotename = 'monitor.out'
#
#
#     fh = StringIO();
#     """
#     while True:
# 	res=""
# 	with fab.settings(
# 	    fab.hide('warnings', 'running', 'stdout', 'stderr'),
# 	    warn_only=True
# 	):
# 	    command = 'tail -n 1 iperf.out | awk -F \",\" \'{print $1\",\"$9}\' '
# 	    output = fab.run(command)
# 	    for line in output.splitlines():
# 		 res=line
# 		    #print "line={}".format(line)
# 	    print "res={}".format(res)
# 	    #with fab.settings(warn_only=True):
# 	#	fab.get(remote_path=remotename, local_path=localname)
# 	    fab.local("sleep 1")
#     """

# def start_iperf_client(server, duration, bw, mask="1111111111"):
#     fab.run('bytecode-manager --set-tdma-mask {}'.format(mask))
#     fab.run('iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -p 12345 -u -t {1} -b {2} -l500B'.format(server, duration, bw))
#     #fab.run('iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -p 12345 -l 125 -u -t {1} -b {2}'.format(server, duration, bw))

# def stop_iperf_server(trialnum):
#     with fab.settings(warn_only=True):
#         fab.run('killall iperf')
#     fab.local('mkdir -p data')
#     localname = 'data/{0}-iperf-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
#     localname_f = 'data/{0}-iperf_f-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
#     with fab.settings(warn_only=True):
#         fab.run('cat iperf.out | grep "0,-" | grep -v nan > iperf2.out')
#         fab.get(remote_path='iperf.out', local_path=localname)
#         fab.get(remote_path='iperf2.out', local_path=localname_f)
#         fab.run('rm iperf2.out')

# def run_iperf_dyn_client(server, duration,bw):
#     sleep_dur=duration/len(bw)
#     cmd=''
#     dur=duration
#     for i in range(len(bw)-1):
#         cmd+='nohup iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2} & sleep {3};'.format(server, dur,bw[i],sleep_dur)
#         dur-=sleep_dur
#     cmd+='iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2}'.format(server,dur,bw[len(bw)-1])
#     fab.run(cmd)


def ror(val, r_bits):
	r = lambda val, r_bits, max_bits: \
	    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
	    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
	return r


def shm_reader():
	command = 'bytecode-manager -x 2 | grep -e 0x00D -e 0x00E -e 0x00F'
	output = fab.run(command)
	output=output.replace(":", " ")
	output=output.replace("\t", "")
	output=output.replace("\n", "")
	output=output.replace("\r", "")
	output=output.split(" ")
	output=[x for x in output if 'x' not in x]
	pos=4
	tx_count=[]
	rx_ack_count=[]
	for i in range(0,10):
		val=output[i+4]
		hex_val="0x{}{}".format(val[2:4],val[0:2]);
		val=int(hex_val,16)
		tx_count.append(val)
		val=output[i+14]
		hex_val="0x{}{}".format(val[2:4],val[0:2]);
		val=int(hex_val,16)
		rx_ack_count.append(val)
	tx_count=[float(i) for i in tx_count]
	rx_ack_count=[float(i) for i in rx_ack_count]
	tx_count=numpy.array(tx_count)
	rx_ack_count=numpy.array(rx_ack_count)
	print(tx_count)
	print(rx_ack_count)
	return [tx_count,rx_ack_count]

# def killControllerLTE():
# 	mask="1111111111"
# 	with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
# 		fab.run('bytecode-manager --set-tdma-mask {}'.format(mask))

"""
@fab.task
def syncAP():
	while True:
		try:
			fp=open('/tmp/lte_ue.json','r')
			lines = fp.readlines()
			if lines:
				first_line = lines[:1]
				last_line = lines[-1]

			print last_line
			stats = json.loads(last_line)
			bler = float(stats.get('PDSCH-BLER'))
			print bler
			val=0
			#if bler > 50 :
			#	val=2000
			#elif bler > 30 :
			#	val=1000
			if bler > 10:
				val=100
			elif bler > 5:
				val=50
			if bler > 5:
				print val
				fab.run('bytecode-manager --set-tsf {}'.format(val))
		except Exception: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
			print "ops!"
		time.sleep(2)
		fp.close()
"""

def syncAP(psucc_thresh=0.75):
	psucc_=0;
	while True:
		try:
			fp=open('/tmp/controllerLTE.log','r')
			lines = fp.readlines()
			if lines:
				first_line = lines[:1]
				last_line = lines[-1]

#			print last_line
			stats = json.loads(last_line)
			psucc = float(stats.get('psucc'))
			mask_sum= float(stats.get('mask_sum'))
			psucc_list= stats.get('psucc_list')
			psucc=get_last_psucc(psucc_list,10,4)
			if numpy.isnan(psucc):
				psucc=float(0);
			from scipy.signal  import butter, lfilter, tf2ss 
			#alpha=0.5
			#psucc_=alpha*psucc+(1-alpha)*psucc_
			#psucc=psucc_

			val=0
#			if psucc < 0.65:
#				val=100
#			if psucc < 0.75:
#				val=200
#			if psucc < 0.85:
			if (mask_sum < 4) or (psucc < float(psucc_thresh)):
				val=10
#			elif psucc < 0.85:
#				val=50
			if val != 0:
				with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
					fab.run('bytecode-manager --set-tsf {}'.format(val))
			print "mask_sum={} psucc={} drift={} psucc_thresh={}".format(mask_sum,psucc,val,psucc_thresh)
		except Exception: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
			print("ops!")
		time.sleep(0.1)
		fp.close()

def controllerLTE(enable_controller=1):
	fh = StringIO();
	[tx_count_,rx_ack_count_]=shm_reader();
	count_round=0
	fp=open('/tmp/controllerLTE.log','w')

	if enable_controller=='2':
		with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
			fab.run('bytecode-manager -a 1')
	else:
		print("ENABLE TDMA")
		with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
			fab.run('bytecode-manager -a 2')
			fab.run('bytecode-manager --set-tdma-mask 1111111111')
	while True:
		count_round=count_round+1
		[tx_count,rx_ack_count]=shm_reader()
		dtx=numpy.mod(tx_count-tx_count_,0xFFFF)
		dack=numpy.mod(rx_ack_count-rx_ack_count_,0xFFFF)
		tx_count_=tx_count
		rx_ack_count_=rx_ack_count
		psucc=numpy.divide(dack,dtx)

		for i in range(0,len(psucc)):
			if numpy.isinf(psucc[i]):
				psucc[i]=0
				continue
			if numpy.isnan(psucc[i]):
				psucc[i]=0
				continue

		psucc_tot=numpy.divide(numpy.sum(dack),numpy.sum(dtx))
		print("rx_ack = {}".format(dack))
		print("tx     = {}".format(dtx))
		numpy.set_printoptions(precision=1)
		print("psucc  = {}".format(psucc))
		print("psucc_tot={}".format(psucc_tot))
		print("count_round={}".format(count_round))
		
		mask=""
		for x in psucc:
			if x > 0.5:
				maskval=1
			elif numpy.isinf(x):
				maskval=0
			else:
				maskval=0

			mask="{}{}".format(maskval,mask)
			mask_int = [ int(x) for x in list(mask)]
		mask_sum=0
		for x in list(mask_int):
			mask_sum+=x

		if mask=="0000000000":
			mask="1111111111"		
		EST_SLOT=4
		L=10
		print(mask)
		p_insert=numpy.random.rand();
		if mask_sum < EST_SLOT:
			p_insert=1;
			mask_int=update_pattern(mask_int,L,mask_sum+1)
#		else: 
#			p_insert=0
#		if p_insert > 0.01:
#			mask_int=update_pattern(mask_int,L,mask_sum+1)
		mask=""
		for x in mask_int:
			mask="{}{}".format(mask,x)
		#count_round=0
		print(mask_int)

		if enable_controller=='0':
			mask="1111111111"
		
		if enable_controller == '0' or enable_controller =='1':	
			with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
				fab.run('bytecode-manager --set-tdma-mask {}'.format(mask))
		
		json_msg={ 'time':time.time(), 'psucc':psucc_tot, 'mask':mask,'enable_controller':enable_controller,'mask_sum':mask_sum, 'psucc_list':list(psucc)}
		print(json_msg)
		fp.write(json.dumps(json_msg))
		fp.write("\n")
		fp.flush()
		time.sleep(1)
	close(fp)

