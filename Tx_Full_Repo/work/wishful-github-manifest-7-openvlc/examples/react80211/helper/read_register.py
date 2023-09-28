
import subprocess
import time
import json


def run_command(command):
	'''
    	Method to start the shell commands and get the output as iterater object
    '''
	sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out, err = sp.communicate()

	if False:
		if out:
			print("standard output of subprocess: out")
			print(out)

	if True:
		if err:
			print("standard error of subprocess: err")
			print(err)

	return [sp.returncode, out.decode("utf-8"), err.decode("utf-8")]


if True:
	cw_setting_interval = 5
	local_starttime = time.time()
	result = None
	tx_frame = 0
	tx_frame_ = 0
	while True:
		#exec_file = str(os.path.join(self.get_platform_path_iw())) + '/iw'
		#cmd_string = str(exec_file) + " dev " + self.wlan_interface + " surveyfreq dump"
		cmd_string = "sudo cat /sys/kernel/debug/ieee80211/phy0/ath9k/xmit | grep TX-Pkts"
		try:
			[rcode, sout, serr] = run_command(cmd_string)
			result = sout
		except Exception as e:
			print("An error occurred in %s" % (e))

		if result:
			result_dict = result.split()
			tx_frame = int(result_dict[1]) + int(result_dict[4]) - tx_frame_
			print(tx_frame)
			tx_frame_ = int(result_dict[1]) + int(result_dict[4])
		else:
			print("no command result")

		time.sleep(cw_setting_interval - ((time.time() - local_starttime) % cw_setting_interval))

			#
			# #[pkt_stats, reading_time] = get_ieee80211_stats(phy)
			# UPIargs = { 'parameters' : [radio.BUSY_TIME.key, radio.EXT_BUSY_TIME.key, radio.TX_ACTIVITY.key, radio.RX_ACTIVITY.key, radio.NUM_TX_SUCCESS.key, radio.NUM_TX_MULTICAST_FRAME.key, radio.NUM_ACK_FAILURE.key, radio.NUM_RTS_SUCCESS_COUNT.key, radio.NUM_RTS_FAILURE_COUNT.key] }
			# pkt_stats = controller.radio.get_parameters(UPIargs)
			# if pkt_stats:
			# 	if enable_react[0]:
			# 		data_success_count = pkt_stats[radio.NUM_TX_SUCCESS.key] - pkt_stats[radio.NUM_TX_MULTICAST_FRAME.key] - data_success_count_
			# 		rts_count = pkt_stats[radio.NUM_TX_SUCCESS.key] - pkt_stats[radio.NUM_TX_MULTICAST_FRAME.key] + pkt_stats[radio.NUM_ACK_FAILURE.key] - rts_count_
			# 		ack_failure_count = pkt_stats[radio.NUM_ACK_FAILURE.key] - ack_failure_count_
			# 		rts_failure_count = pkt_stats[radio.NUM_RTS_FAILURE_COUNT.key] - rts_failure_count_
			# 		dd = float(reading_time - reading_time_)
			#
			# 		busy_time = pkt_stats[radio.BUSY_TIME.key] - busy_time_
			# 		ext_busy_time = pkt_stats[radio.EXT_BUSY_TIME.key] - ext_busy_time_
			# 		tx_activity = pkt_stats[radio.TX_ACTIVITY.key] - tx_activity_
			# 		rx_activity = pkt_stats[radio.RX_ACTIVITY.key] - rx_activity_
			# 		if data_success_count_ > 0:
			# 			number_of_attempt = rts_failure_count + ack_failure_count + data_success_count
			# 			if number_of_attempt > 5 and tx_activity > 20:
			# 				#airtime_coll = round( tx_activity / (cw_setting_interval * 1000), 4)
			# 				airtime_coll = round( (tx_activity + (tx_activity*15/100) ) / (cw_setting_interval * 1000), 4)
			# 				#airtime_coll_average = round(  tx_activity / number_of_attempt, 4)
			# 				airtime_coll_average = round(  (tx_activity + (tx_activity*15/100) ) / number_of_attempt, 4)
			# 				e_average = round( ((cw_setting_interval * 1000) - (tx_activity + (tx_activity*15/100)) ) / number_of_attempt / (cw_-1) * 2 , 4)
			# 			else:
			# 				airtime_coll = 0
			# 				airtime_coll_average = 0.25
			# 				e_average = 0.009
			#
			# 			if station_claim[0] > 0:
			# 				next_w = 2 * ((1-float(station_claim[0]))/float(station_claim[0])) * float(airtime_coll_average) /  float(e_average)
			# 			else:
			# 				next_w = 32
			#
			# 		data_success_count_ = pkt_stats[radio.NUM_TX_SUCCESS.key] - pkt_stats[radio.NUM_TX_MULTICAST_FRAME.key]
			# 		rts_count_ = pkt_stats[radio.NUM_TX_SUCCESS.key] - pkt_stats[radio.NUM_TX_MULTICAST_FRAME.key] + pkt_stats[radio.NUM_ACK_FAILURE.key]
			# 		ack_failure_count_ = pkt_stats[radio.NUM_ACK_FAILURE.key]
			# 		rts_failure_count_ = pkt_stats[radio.NUM_RTS_FAILURE_COUNT.key]
			# 		reading_time_ = reading_time
			#
			# 		busy_time_ = pkt_stats[radio.BUSY_TIME.key]
			# 		ext_busy_time_ = pkt_stats[radio.EXT_BUSY_TIME.key]
			# 		tx_activity_ = pkt_stats[radio.TX_ACTIVITY.key]
			# 		rx_activity_ = pkt_stats[radio.RX_ACTIVITY.key]
			#
			# 		thr = round( (data_success_count) * 1470 * 8 / float(dd * 1e6), 3 )
			#
			# 	if debug or debug_statistics:
			# 		# if debug_cycle > 3:
			# 		if True:
			# 			# print("t=%.4f,dd=%.4f data_count=%.4f rts_count=%.4f busytx2=%.4f(%.4f) gross_rate=%.4f,avg_tx=%.4f freeze2=%.4f freeze_predict=%.4f tx_goal=%.4f I=%.4f cw=%.4f cw_=%.4f psucc=%.4f thr=%.4f" % (time.time(), dd, data_count, rts_count, busytx2, busytx2/float(dd), gross_rate, avg_tx, freeze2, freeze_predict, tx_goal, I, cw, cw_, psucc, thr))
			# 			print(
			# 				"%.6f - airtime_coll=%.4f tx_activity=%.4f data_success_count=%d ack_failure_count=%d rts_failure_count=%d cw_=%.4f thr=%.4f airtime_coll_average=%.4f e_average=%.4f next_w=%.4f station_claim[0]=%.4f" % (
			# 				reading_time, airtime_coll, tx_activity, data_success_count, ack_failure_count, rts_failure_count, cw_, thr, airtime_coll_average, e_average, next_w, station_claim[0]))
			# 			print(
			# 				"%.6f - busytime=%.4f ext_busy_time=%.4f tx_activity=%.4f rx_activity=%.4f" % (
			# 				reading_time, busy_time, ext_busy_time, tx_activity, rx_activity))
			# 			debug_cycle = 0
			# 		else:
			# 			debug_cycle += 1
			#
			# 	# store statistics for report
			#
			# 	# report_stats['psucc'] = 1
			# 	# if busytx2 < 0:
			# 	# 	busytx2 = 0
			# 	# if busytx2 > 0.8:
			# 	# 	busytx2 = 0.8
			# 	# report_stats['busytx2'] = busytx2
			#
			# 	report_stats['thr'] = thr
			# 	report_stats['cw'] = cw_
			# 	report_stats['busy_time'] = busy_time
			# 	report_stats['a_coll'] = airtime_coll
			# 	report_stats['e_ave'] = e_average
			# 	report_stats['reading_time'] = reading_time
			#
			# if enable_react[0]:
			# 	# ENFORCE CW
			# 	setCW(iface, qumId, aifs, cw_, cw_, burst)