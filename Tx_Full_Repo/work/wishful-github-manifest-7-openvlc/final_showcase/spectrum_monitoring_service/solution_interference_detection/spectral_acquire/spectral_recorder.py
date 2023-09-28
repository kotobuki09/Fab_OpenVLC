#!/usr/bin/env python
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import array
import struct
import sys
import time
import os
import json

from subprocess import call
from operator import itemgetter
from sklearn import preprocessing


import numpy as np
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


class SpectralRecorder:
	mode="manual"		#works
	fft_period=15
	spectral_count=100
	spectral_period=1
	short_repeat=1


	def __init__(self, phy="phy0", dev="wlan0", drv="ath9k",
			mode="manual", fft_period=15, spectral_count=100, spectral_period=1, short_repeat=1, load=False, offline=True, freq=2462e6):
		self.phy 		= phy
		self.dev 		= dev
		self.drv		= drv
		self.mode		= mode
		self.fft_period		= fft_period
		self.spectral_count	= spectral_count
		self.spectral_period	= spectral_period
		self.short_repeat	= short_repeat
		self.f0			= freq #optional useful only if load is True
		#set spectral parameters
		if offline==False:
			self.set_spectral_params()
		if load:
			self.load_monitor()

	def get_spectral_params(self):
		return self.fft_period,self.spectral_count,self.spectral_period,self.short_repeat

	def load_monitor(self):
		#call("bash build.sh --load-module",shell=True)
		call("ifconfig "+self.dev+" down",shell=True)
		call("iwconfig "+self.dev+" mode monitor",shell=True)
		call("ifconfig "+self.dev+" up",shell=True)
		call("iwconfig "+self.dev+" freq "+str(self.f0),shell=True)

	def set_spectral_params(self):
		call("echo "+ self.mode		  		+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_scan_ctl", shell=True)
		call("echo "+ str(self.short_repeat)	  	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_short_repeat",shell=True)
		call("echo "+ str(self.fft_period)	  	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_fft_period",shell=True)
		call("echo "+ str(self.spectral_count-1) 	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_count",shell=True)
		call("echo "+ str(self.spectral_period)		+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_period",shell=True)

	def acquire(self,filename="data",T_acquire=1,T=0.1):
		call("cat /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan0 > {}".format(filename), shell=True)
		# time.sleep(T)
		t0=time.time()
		t0_a=t0
		now=t0
		now_a=t0
		while now_a-t0_a < T_acquire:
			now_a=time.time()
			while now-t0 < T:
				now=time.time()
				call("echo trigger > /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan_ctl", shell=True)
			now=time.time()
			t0=now
			call("cat /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan0 >> {}".format(filename), shell=True)
			#print(now_a-t0_a)

	def fix_timestamp_dict(self,samp_dict,T=50e3):
		ret=samp_dict
		timestamp=[v['tsf'] for v in samp_dict]
		timestamp=np.array(timestamp)-timestamp[0]
		decr=0
		if len(timestamp)!=0:

			tsf_diff=[]
			for i_t in range(0,len(timestamp)-1):
				t_=timestamp[i_t]
				t=timestamp[i_t+1]
				dt=t-t_

				# print("t[{}]={}".format(i_t,t))
				# print("t[{}]_={}".format(i_t,t_))
				if abs(dt) > T:
					#EMERGE ERROR, TSF chagnes
					# print("[E] t[{}]={}".format(i_t,t))
					# print("[E] t_[{}]={}".format(i_t,t_))
					ret.pop(i_t+1)
					decr=decr+1
				else:
					tsf_diff.append(dt)
					tsf_new=sum(tsf_diff)

					ret[i_t-decr]['tsf']=tsf_new
		else:
			print("timestamp is empty")
		ret.pop(len(ret)-1)
		return ret

	def fix_timestamp(self,timestamp,busy,x,T=50e3):
		if len(timestamp)!=0:
			timestamp=np.array(timestamp)-timestamp[0]
			tsf_diff=[]
			for i_t in range(0,len(timestamp)-1):
				t_=timestamp[i_t]
				t=timestamp[i_t+1]
				dt=t-t_

				#print("t={}".format(t))
				#print("t_={}".format(t_))
				if abs(dt) > T:
					#EMERGE ERROR, TSF chagnes
					print("t={}".format(t))
					print("t_={}".format(t_))
					busy.pop(i_t)
					x.pop(i_t)
				else:
					tsf_diff.append(dt)
			timestamp=np.cumsum(tsf_diff)
			busy=busy[0:len(timestamp)]
		else:
			print ("timestamp is empty")
		return timestamp,busy,x

	def extract_samples(self,filename="data",out_file="out_samp.json",T=-1):
		y = []
		p_fft=[]
		freq_fft=[]
		busy = []
		timestamp = []
		out_samp=[]
		take_all_samples=False;
		if T == -1:
			take_all_samples=True;
		with open(filename, "rb") as file:

			data = file.read(76)
			i_pos_tmp=0
#			while data != "":
			while data:


				i_pos_tmp=i_pos_tmp+1
				y_t = []
				x = []

				t, length = struct.unpack(">BH", data[0:3])
				if t != 1 or length != 73:
				    print("only 20MHz supported atm")
				    sys.exit(1)

				### metadata

				max_exp, freq, rssi, noise, max_magnitude, max_index, bitmap_weight, tsf = struct.unpack('>BHbbHBBQ', data[3:20])

				### measurements
				measurements = array.array("B")
				measurements.fromstring(data[20:])
				squaresum = sum([(m << max_exp)**2 for m in measurements])
				if squaresum == 0:
				    data = file.read(76)
				    continue
				fft_sub=[]
				for i, m in enumerate(measurements):
					if m == 0 and max_exp == 0:
						m = 1
					v = 10.0**((noise + rssi + 20.0 * np.log10(m << max_exp) - 10.0 * np.log10(squaresum))/10.0)
					fft_sub.append(v)
				entry={}
				entry['tsf']=tsf
				timestamp.append(int(tsf))
				entry['freq']=freq
				entry['rssi']=rssi
				entry['noise']=noise
				entry['fft_sub']=fft_sub

				out_samp.append(entry)
				data = file.read(76)
				if not(take_all_samples):
					if int(timestamp[len(timestamp)-1])-int(timestamp[0]) < T:
						data = file.read(76)
						continue;
					else:
					    	break
		#with open(out_file, 'w') as file:
		#	out_json=json.dumps(out_samp)
		#	file.write(out_json)
		return out_samp

	def get_feature(self,busy,timestamp):
		W = 1e3; #usec
		ts = timestamp-timestamp[0]
		t_= ts[0];
		t = ts[1];
		b_curr=[];
		b_mean=[];
		b_var =[];
		for b in range(0,len(busy)):
			if t-t_ < W:
				t = ts[b]
			else:
				t_= ts[b]
				b_mean.append(np.mean(b_curr))
				b_var.append(np.var(b_curr))
				b_curr=[]
			b_curr.append(busy[b])

		return b_mean, b_var

	def rrc_f(self, T=1, beta=0.8):
		out = []
		for f in np.linspace(-1 / (2.0 * T), 1 / (2.0 * T), num=5):
			if abs(f) <= (1 - beta) / float(2.0 * T):
				out.append(1.0)
			else:
				if (1 - beta) / float(2.0 * T) < abs(f) and abs(f) <= (1 + beta) / float(2.0 * T):
					v = 0.5 * (1 + np.cos(np.pi * T / float(beta) * (abs(f) - (1 - beta) / float(2.0 * T))))
					out.append(v)
				else:
					out.append(0)
		return out

	def get_freq_list(self,freq, N=1):
		ff = []
		for i in range(0, 56):
			# if m == 0 and max_exp == 0:
			#    m = 1
			if i < 28:
				fr = freq - (20.0 / 64) * (28 - i)
			else:
				fr = freq + (20.0 / 64) * (i - 27)
			ff.append(fr)
		fff = []
		#Overasmpling: unused if N=1
		for f in ff:
			for o in range(0, N):
				fff.append(f + o * (20.0 / 64 / N))
		return fff

	def get_spectrum_scan_features(self, filename="demo.tlv", T=100e3):

		skip = False
		thr_bw = 0.05
		thr_corr = 1e-10
		thr_corr_mean = 1
		P_thr_db = -75
		P_thr = 10 ** (P_thr_db / 10.0)
		dt_thr = 2600

		# OUTPUT FEATURES
		spectrum_features = []
		duration_features = []
		duration_energy_det_features = []
		measurements = self.extract_samples(filename, out_file="not-in-use.json", T=T)

		power_features=[]
		mark_as_failure = False
		csi_data = list(map(itemgetter('fft_sub'), measurements))
		csi_data = np.array(csi_data)
		freq = list(map(itemgetter('freq'), measurements))
		tsf = list(map(itemgetter('tsf'), measurements))

		freq = list(set(freq))
		freq = freq[0]
		ff = self.get_freq_list(freq)
		y = np.array(csi_data[0])

		y_ = y
		y_nofilt_ = y

		tt = tsf[0]
		tt_ = tt

		start_corr = False
		corr_duration = 0
		corr_duration_num = 0
		energy_det_duration = 0
		t_corr_start = tt
		t_energy_det_start = 0

		y_cont=[]
		P_av_w=[]
		P_av_=0

		print("====================================");
		p_av_list = np.convolve(np.mean(csi_data, axis=1), np.array([1, 1, 1, 1])[::-1], 'same')

		for ii, cc in enumerate(csi_data):
			if ii==0:
				start_energy_det = True
				finish_energy_det = False
			skip = False
			yy = []
			start_f = []
			stop_f = []
			START_BW = True
			y_pow = []
			bw_meas = []
			freq_meas = []

			y = np.array(cc)
			tt = tsf[ii]
			dt = tt - tt_

			y_nofilt = y
			weights = self.rrc_f()
			#weights = [1, 1, 1]

			y = np.convolve(y, np.array(weights)[::-1], 'same')

			min_max_scaler = preprocessing.MinMaxScaler()
			y_det = min_max_scaler.fit_transform(y.reshape(-1, 1))
			y_det_ = min_max_scaler.fit_transform(y_.reshape(-1, 1))
			y_det_nofilt = min_max_scaler.fit_transform(y_nofilt.reshape(-1, 1))
			y_det_nofilt_ = min_max_scaler.fit_transform(y_nofilt_.reshape(-1, 1))

			y_det = y_det[:, 0]
			y_det_ = y_det_[:, 0]
			y_det_nofilt = y_det_nofilt[:, 0]
			y_det_nofilt_ = y_det_nofilt_[:, 0]
			P_av = np.mean(y)
			P_av_w = p_av_list[ii]

			power_features.append({"tsf_p": tt, "p_av": P_av,"p_av_w": P_av_w})

			P_av=P_av_w

			# if len(P_av_w) >N_av: #window size = 5
			# 	P_av_w.pop(0) #window step=1

			# ENERGY DETECTION
			# if P_av_ < P_thr and P_av > P_thr and dt < dt_thr:
			# 	start_energy_det=True;
			# 	t_energy_det_start = tt
			# else:
			# 	if P_av_ > P_thr and P_av < P_thr and dt < dt_thr:
			# 		start_energy_det = False;
			# 		energy_det_duration = tt - t_energy_det_start
			# 		duration_energy_det_features.append(
			# 		 	{"tsf": t_energy_det_start, "duration": energy_det_duration})
			# 	else:

			if P_av >= P_thr and start_energy_det:
						t_energy_det_start = tt;
						# print("start:{}",t_energy_det_start);
						start_energy_det = False
						mark_as_failure = False;

			if P_av <= P_thr and not start_energy_det:
						t_energy_det_stop = tt_;
						# print("stop:{}", t_energy_det_stop);
						finish_energy_det = True

			if P_av >= P_thr and not start_energy_det:
				if ii < len(tsf)-1:
					if tsf[ii+1]-tsf[ii] > dt_thr:
						mark_as_failure=True
						# print("[ii={}] failure dt={}".format(ii,tsf[ii+1]-tsf[ii]))

			if P_av <= P_thr and finish_energy_det:
				# if not mark_as_failure:
					# print(" [ OK ] finish:{}", t_energy_det_stop-t_energy_det_start);
				# else:
					# print(" [FAIL] finish:{}", t_energy_det_stop - t_energy_det_start);
				finish_energy_det=False
				start_energy_det=True
				if not mark_as_failure:
						# duration_energy_det_features.append(
						# {"tsf": t_energy_det_start, "duration": t_energy_det_stop-t_energy_det_start})
					duration_energy_det_features.append(
						{"tsf": t_energy_det_start, "tsf_stop": t_energy_det_stop, "duration": t_energy_det_stop - t_energy_det_start})

			P_av_ = P_av
			#print(duration_energy_det_features)
			yy = y_det

			N_av = 10
			if len(y_cont) >= N_av:
				y_cont.pop(0)  # window step=1

			if P_av >= P_thr:
				# collect some consecutive samples and average it!
				y_cont.append(yy)
				yy = np.mean(y_cont, axis=0)
				if len(y_cont) == N_av:
					for i in range(0, len(yy)):
						#print(yy[i])
						if yy[i] > thr_bw and i < len(yy) - 1:
							y_pow.append(yy[i])
							if START_BW:
								# print "START"
								start_f.append(ff[i])
								START_BW = False

						else:
							if not START_BW:
								stop_f.append(ff[i - 1])
								START_BW = True
				for i in range(0, min(len(start_f), len(stop_f))):
					bw_meas.append(stop_f[i] - start_f[i] - 20/64.0)
					freq_meas.append((stop_f[i] + start_f[i]) / 2.0)

				# CORRELATION
				y_corr = np.correlate(y_det, y_det_, "same")
				# y_corr = np.correlate(y_det_nofilt, y_det_nofilt_, "same")
				# if np.median(y_corr) <= thr_corr_mean and P_av >= P_thr:
				if np.median(y_corr) <= thr_corr_mean:
					if start_corr:
						corr_duration = tt - t_corr_start
						if corr_duration != 0:
							duration_features.append({"tsf": t_corr_start, "duration": corr_duration, "duration_num": corr_duration_num })
							corr_duration = 0
							corr_duration_num = 0
						start_corr = False
				else:
					if start_corr == False:
						t_corr_start = tt
						start_corr = True
						corr_duration_num = 1
					else:
						corr_duration_num += 1


				spectrum_features.append({"tsf": tsf[ii], "bw": bw_meas, "freq": freq_meas})
			else:
				y_cont = []


			# update state variables, ready for next round
			tt_ = tt
			y_ = y
			y_nofilt_ = y_nofilt

			#if P_av <= P_thr:
			#	skip = True
			#else:
			# print(spectrum_features)

		return measurements, spectrum_features, duration_energy_det_features, duration_features, freq,power_features

	def plot_waterfall(self,ax,measurements,exp_name):
		csi_data = list(map(itemgetter('fft_sub'), measurements))
		timestamp = list(map(itemgetter('tsf'), measurements))
		freq = list(map(itemgetter('freq'), measurements))
		freq=list(set(freq))
		freq=freq[0]
		timestamp=np.array(timestamp)-timestamp[0]

		T=np.max(timestamp)
		N=len(timestamp)
		y=self.get_freq_list(freq)
		x=timestamp[0:N]
		Z=10.0 * np.log10(csi_data[0:N])
		X,Y = np.meshgrid(y,x)

		cc=ax.pcolormesh(X,Y,Z,vmin=-140, vmax=-20)
		fmin=min(y)
		fmax=max(y)
		ax.set_xlim([fmin,fmax])
		ax.set_ylim([0,T])
		ax.set_ylabel('Time [us]')
		ax.set_xlabel('freq [MHz]')
		ax.set_title(exp_name)
		return ax

	def get_freq_list(self,freq, N=1):
		ff = []
		for i in range(0, 56):
			# if m == 0 and max_exp == 0:
			#    m = 1
			if i < 28:
				fr = freq - (20.0 / 64) * (28 - i)
			else:
				fr = freq + (20.0 / 64) * (i - 27)
			ff.append(fr)
		fff = []
		for f in ff:
			for o in range(0, N):
				fff.append(f + o * (20.0 / 64 / N))
		return fff

		# return ff
