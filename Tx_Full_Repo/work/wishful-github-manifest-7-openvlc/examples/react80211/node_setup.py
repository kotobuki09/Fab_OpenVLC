def experiment_setup(exp_file):
	exp_info_file = open(exp_file, 'r').readlines()
	exp_info=[]
	for i in exp_info_file:
		if not i.startswith("#"):
			exp_info.append(i);
	j=0
	src = [i.split(',')[j] for i in exp_info]
	j=j+1
	dst= [i.split(',')[j].replace("\n", "") for i in exp_info]
	j=j+1
	bw_req= [i.split(',')[j].replace("\n", "") for i in exp_info]
	j=j+1
	port= [i.split(',')[j].replace("\n", "") for i in exp_info]
	j=j+1
	t_start= [i.split(',')[j].replace("\n", "") for i in exp_info]
	j=j+1
	t_stop= [i.split(',')[j].replace("\n", "") for i in exp_info]

	return src,dst,bw_req,port,t_start,t_stop

def set_hosts(host_file):
	hosts_info_file = open(host_file, 'r').readlines()
	hosts_info=[]
	for i in hosts_info_file:
		if not i.startswith("#"):
			hosts_info.append(i)
	j=0
	hosts = [i.split(',')[j] for i in hosts_info]
	j=j+1
	driver= [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	eth_ip= [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	freq= [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	tx_power= [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	wlan_ip= [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	mac_address = [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	label = [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	role = [i.split(',')[j].replace("\n", "") for i in hosts_info]
	j=j+1
	iface = [i.split(',')[j].replace("\n", "") for i in hosts_info]

	return hosts,driver,eth_ip,freq,tx_power,wlan_ip,mac_address,label,role,iface
