#include <math.h>
#include <stdlib.h>
#include <signal.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <getopt.h>

#include "int-aloha.h"
#include "protocols.h"
#include "vars.h"
#include "dataParser.h"

void INThandler(int);
/* Performs the computation for emulating the suite of protocols
for a single slot, and adjusting the weights. */
void update_weights(struct protocol_suite* suite, struct meta_slot current_slot)
{
	/* If there is no packet queued for this slot, consider all protocols to be correct
	and thus the weights will not change. */
	if (current_slot.packet_queued) {
		/* z represents the correct decision for this slot - transmit if the channel
		is idle (1.0) or defer if it is busy (0.0) */
		double z = (!current_slot.channel_busy) ? 1.0 : 0.0;

		for (int p = 0; p < suite->num_protocols; ++p) {
			/* d is the decision of this component protocol - between 0 and 1 */
			double d = suite->protocols[p].emulator(suite->protocols[p].parameter, 
				current_slot.slot_num, suite->last_slot);
			suite->weights[p] *= exp(-(suite->eta) * fabs(d - z));
		}

		/* Normalize the weights */
		double s = 0;
		for (int p = 0; p < suite->num_protocols; ++p) {
			s += suite->weights[p];
		}

		for (int p = 0; p < suite->num_protocols; ++p) {
			suite->weights[p] /= s;
		}
	}

	suite->last_slot = current_slot;
}

void init_protocol_suite(struct protocol_suite *suite, int num_protocols, double eta)
{
	int p;
	suite->num_protocols = num_protocols;
	suite->best_protocol = -1;
	suite->slot1_protocol = -1;
	suite->slot2_protocol = -1;
	suite->active_slot = 0;

	suite->protocols = (struct protocol*)calloc(num_protocols, sizeof(struct protocol));
	suite->weights = (double*)malloc(sizeof(double) * num_protocols);

	for (p=0; p < num_protocols; ++p) {
		suite->weights[p] = 1.0 / num_protocols;
	}

	suite->eta = eta;
	suite->last_slot.slot_num = -1;
	suite->last_slot.packet_queued = 0;
	suite->last_slot.transmitted = 0;
	suite->last_slot.channel_busy = 0;
}

void int_aloha_init(struct debugfs_file * df, struct protocol_suite *suite)
{
//	printf("%d\n", suite->num_protocols);
	if (suite->num_protocols < 1) {
		return;
	}

	/* Best protocol could be already initialized based on predictions/heuristics */
	if (suite->best_protocol < 0) {
		/* Select the best protocol based on weights. At this point, they
		should be the same, so the first protocol will be selected. */
		int p = 0;
		double w = suite->weights[0];
		for (int i = 1; i < suite->num_protocols; ++i) {
			if (suite->weights[i] > w) {
				p = i;
				w = suite->weights[i];
			}
		}
		suite->best_protocol = p;
	}

	
	struct options opt;
	init_options(&opt);
	
//	printf("first : 1\n");
	opt.do_up = " ";
	opt.load = "2";
	opt.name_file = suite->protocols[suite->best_protocol].fsm_path;
	parser(df, &opt);
	sleep(3);
	
//	printf("first : 2\n");
	
	suite->slot1_protocol = suite->best_protocol;
	suite->active_slot = 2;
	opt.active = "2";
	activeBytecode(df,&opt);
	sleep(3);
	
//	printf("first : 3\n");
	
}

FILE * log_int_aloha;
FILE * log_slot_aloha;

void INThandler(int sig)
{
    fclose(log_int_aloha);
    fclose(log_slot_aloha);
    printf("Close correctely");
    exit(0);
}

/**
 * name file by argument option
 * CTRL-C handle with file close
 */
void int_aloha_loop(struct debugfs_file * df, struct protocol_suite *suite, struct logic_options * current_options)
{
	int i, j, k;
	char iface_wlan[128];
	int_aloha_init(df, suite);

	//unsigned long average_point = 806;	//num slot for 620us with measurement time update of 0,5s.
	unsigned long average_point = 806;	
	unsigned long slot_num = 0;
	unsigned long slot = 0;
	
	unsigned long channel_busy_sum_error_check = 0;
	unsigned long channel_busy_sum_busy_time_check = 0;
	unsigned long channel_busy_sum_all = 0;
	
	unsigned long slot_successfull = 0;
	unsigned long slot_free = 0;
	
	
	
	#define CYCLE_UPDATE 5
	#define CYCLE_SAMPLE 5*3 //more of CYCLE_UPDATE
	int cycle = 0;
	int trace_station_traffic = 0;
	float pcol_all[CYCLE_SAMPLE];
	float pcol_error_check[CYCLE_SAMPLE];
	float pcol_busy_time_check = 0;
	float pcol_before = 0;
	float slot_successfull_rate_before = 0;
	float num_sta_before = 0;
	float  num_stations = 0;
	int count = 0;
	unsigned long tau = 32757;
        unsigned long param_14 = 0;
	double intpart = 0;
							
	//float bad_reception_norm = 0;
	//unsigned long bad_reception_sum = 0;
        //unsigned int channel_busy_seven = 0;
	//unsigned int save_busy[96/8]={0};
	
	time_t rawtime;
	struct tm * timeinfo;
	long int old_tv_sec=0;
	char buffer[80];
	signal(SIGINT, INThandler);
	
	if (strcmp(current_options->log_file_name,"")==0){
		current_options->log_file_name="file_log.csv";
	}
	log_int_aloha = fopen(current_options->log_file_name, "w+");
	log_slot_aloha = fopen("slot_log.csv", "w+");
	FILE *fp;	
	fp = popen("ifconfig | grep '192.168.3' | cut -d: -f2 | awk '{print $1}'", "r");
	//ifconfig | grep -e '192.168.3' | cut -d: -f2 | awk '{ print $1}'
	if (fp == NULL) {
	      printf("Failed to run command\n" );
	      exit;
	}
	fscanf(fp, "%s", iface_wlan);
	fclose(fp);
	
	unsigned int slot_count = 0x001F & shmRead16(df, B43_SHM_REGS, COUNT_SLOT);
	if(slot_count < 32)
	  slot = slot_count + 1;
	  
        //unsigned int prev_slot_count;
        //unsigned int seven_slots_prev = 0;	
	
	while (1) {

			usleep(7000);
			slot_count = 0x001F & shmRead16(df, B43_SHM_REGS, COUNT_SLOT);
			
			unsigned int packet_queued = shmRead32_int(df, B43_SHM_SHARED, PACKET_TO_TRANSMIT);
			unsigned int transmitted  = shmRead32_int(df, B43_SHM_SHARED, START_TRANSMISSION);
			unsigned int transmit_success = shmRead32_int(df, B43_SHM_SHARED, SUCCES_TRANSMISSION);
			unsigned int transmit_other =shmRead32_int(df, B43_SHM_SHARED, OTHER_TRANSMISSION);
			unsigned int bad_reception =shmRead32_int(df, B43_SHM_SHARED, BAD_RECEPTION);
			unsigned int busy_slot =shmRead32_int(df, B43_SHM_SHARED, BUSY_SLOT);
			
			unsigned int channel_busy_error_check = (packet_queued & transmitted & ~transmit_success ) | transmit_other | bad_reception ;
			unsigned int channel_busy_busy_time_check = (packet_queued & transmitted & ~transmit_success ) | transmit_other | ( busy_slot & ~transmit_success );
			unsigned int channel_busy_all = (packet_queued & transmitted & ~transmit_success ) | transmit_other | bad_reception | ( busy_slot & ~transmit_success );
			
			// Debugging.
			//printf("slot_count=%d\n", slot_count);
			//printf("%d, %08x, %08x, %08x, %08x, %08x, %08x\n",
			//       		slot_count, packet_queued, transmitted, transmit_success, transmit_other, bad_reception, busy_slot);	
                        
			//unsigned int slot = prev_slot_count;
			for (int j = 0; j < 32; ++j) {                               
                        
				channel_busy_sum_busy_time_check = channel_busy_sum_busy_time_check + ((channel_busy_busy_time_check >> slot) & 1);
				channel_busy_sum_all = channel_busy_sum_all + ((channel_busy_all >> slot) & 1);
				
				/*** good **/
				channel_busy_sum_error_check = channel_busy_sum_error_check + ((channel_busy_error_check >> slot) & 1);
				slot_successfull = slot_successfull + ((transmit_success >> slot) & 1);
				/*** good **/
								
				slot_num++;
				if ( (slot_num % average_point == 0) && slot_num > 1 ){
					
					/**** pcoll ***/
					pcol_all[cycle] = ((float)(channel_busy_sum_all) / average_point);
					pcol_error_check[cycle] = ((float)(channel_busy_sum_error_check) / average_point);
					pcol_busy_time_check = ((float)(channel_busy_sum_busy_time_check) / average_point);
						
					/**** log slot ***/
					slot_free = average_point - ( channel_busy_sum_error_check + slot_successfull);
					//printf("Slot %ld: slot_free = %ld, channel_busy_sum_error_check = %ld, slot_successfull = %ld\n", slot_num, slot_free, channel_busy_sum_error_check, slot_successfull);
					
					
					/* slot rate update */
					float slot_free_rate =  (float)(slot_free*100) / (float) average_point;
					float channel_busy_sum_error_check_rate =  (float)(channel_busy_sum_error_check*100) / (float) average_point;
					float slot_successfull_rate = (float)(slot_successfull*100) / (float) average_point;
					
				
					/* log operation */	      
					time(&rawtime);
        				timeinfo = localtime(&rawtime);
					
					/* log operation */	      
					strftime (buffer,80,"%G%m%d%H%M%S",timeinfo);
					//printf("%s\n", buffer);
					struct timeval tim;
             				gettimeofday(&tim, NULL);
             				double t1=tim.tv_sec+(tim.tv_usec/1000000.0);
            				//printf("%.6lf seconds elapsed\n", t1);	      
                                        //printf("Slot %ld: pcol = %f - num_sta= %f\n", slot_num, pcol_all, num_stations);
				        fprintf(log_int_aloha, "%s,%.6lf,%s,%f,%f,%f,%d,%f,%d\n", buffer, t1, iface_wlan, pcol_all[cycle], pcol_busy_time_check, pcol_error_check[cycle], tau, num_stations, count);
					//fprintf(log_int_aloha, "%s,%ld,%s,%f,%f,%f,%d,%f,%d\n", buffer, tim.tv_sec, iface_wlan, pcol_all[cycle], pcol_busy_time_check, pcol_error_check[cycle], tau, num_stations, count);
					//printf("Slot %ld: slot_free_rate = %f, channel_busy_sum_error_check_rate = %f, slot_successfull_rate = %f\n", slot_num, slot_free_rate, channel_busy_sum_error_check_rate, slot_successfull_rate );
					fprintf(log_slot_aloha, "%s,%.6lf,%s,%f,%f,%f\n", buffer, t1, iface_wlan, slot_free_rate, channel_busy_sum_error_check_rate, slot_successfull_rate );
					
                                        fflush(log_int_aloha);
                                        fflush(log_slot_aloha);
					
					cycle++;
					if (slot_successfull_rate < 0.4)
						  trace_station_traffic ++;
					
					if ( !( tim.tv_sec % CYCLE_UPDATE)  && (tim.tv_sec > old_tv_sec) ){	
						old_tv_sec = tim.tv_sec;
						float pcol_error_check_top = 0;
						if(num_stations<2){
						      //extract protocol persistent probability 
						      for(k=0; k<cycle; k++){
							if(pcol_error_check[k] > pcol_error_check_top)
							  pcol_error_check_top = pcol_error_check[k];
						      }
						}
						else{
						      #define AVERAGE_SAMPLE 4
						      for(k=(cycle - AVERAGE_SAMPLE); k<cycle; k++){
							  pcol_error_check_top = pcol_error_check_top + pcol_all[k];
						      }
						      pcol_error_check_top = (pcol_error_check_top/AVERAGE_SAMPLE);
						      if(tau <= 22000)
							  pcol_error_check_top = pcol_error_check_top - 0.05;
						}
						
						
						float prm_14 = (float)tau/65534;
						//stimate stations number
						if(pcol_error_check_top < 0.15)
						      num_stations = 1;
						else{
						      num_stations = 1 + (log10(1-pcol_error_check_top)/log10(1-prm_14));
						      if(tau == 58980)
							  num_stations = num_stations + 0.6;
						}
						
						
						if(num_stations > 4)
						  num_stations = 4;
						if(num_stations < 0)
						  num_stations = 0;
						  
						
						if ( (cycle-trace_station_traffic)<5 )
						  num_stations = num_stations - 1;
						
						cycle = 0;
						trace_station_traffic = 0;
						
	//					printf("num_sta=%f, num_before=%f, diff_2=%f\n ", num_stations, num_sta_before, diff_2);
	//					printf("abs_sta=%d\n",(int) abs_value_2);
	//					printf("pcol_all=%f, pcol_before=%f, diff= %f ", pcol_all, pcol_before, diff);
	//					printf("abs = %f\n\n\n", abs_value);
	//					pcol_before = pcol_error_check;
	//					slot_successfull_rate_before = slot_successfull_rate;
						      
							double var = modf (num_stations , &intpart);
							if(var >= 0.5){
							   intpart = intpart + 1;
							}
							
						      num_stations = (float)intpart;
						      if(num_stations==0)
							      tau = 58980;
						      else {
							      tau = 65534 / (int) num_stations;
							      if (tau > 58980){
								    tau = 58980;
							      }
							      if (tau < 10000){
								    tau = 10000;
							      }
						      }
						      //printf("num_sta=%f, intpart=%f, var=%f, tau = %ld\n", num_stations, intpart, var, tau);
						      //printf("num_sta= %d, pcoll= %f, prm_14= %f, tau=%f\n", num_stations, pcol_all, prm_14, tau);
						      //set opportunistically probability
						     
						     
						      //printf("PARAM_14 AGGIORNATO: **** %d ****\n\n", param_14);
					//	}
				//	}
						      shmWrite16(df, B43_SHM_SHARED, (0x11*2+PARAMETER_ADDR_BYTECODE_2), tau);
						      //shmWrite16(df, B43_SHM_SHARED, (0x11*2+PARAMETER_ADDR_BYTECODE_2), 58980);      
						      count = 0; 
					}
					else
					  count ++;
					
					
					/*reset slot conditions variables*/
					slot_free = 0;
					slot_successfull = 0;

					/*reset sum variables*/
					channel_busy_sum_error_check = 0;
					channel_busy_sum_busy_time_check = 0;
					channel_busy_sum_all = 0;
					
						      
					
                                }

			slot = (++slot) % (32);
			if (slot == (slot_count & 0x1F)) {
	//              	printf("Slot %ld: pcol = %f, channel_busy_sum = %ld\n", slot_num, pcol, channel_busy_sum);
				break;
			}

		}

		// This is where the active protocol will be updated once that is implemented

		//printf("Slot %ld: pcol = %ld, channel_busy_sum = %ld\n", slot_num, pcol, channel_busy_sum);
		//slot_num = 0;
		//for (int i = 0; i < suite->num_protocols; ++i) {
		//	printf("%s=%f ", suite->protocols[i].name, suite->weights[i]);
		//}
		
		//siccome (1-tau)^(N-1)=pcoll, se si misura la pcoll e si assume ch etutti usino la stessa tau di accesso di puo' trovare N e quindi regolare tau = 1/N;
		//quindi se osservo B slot, in cui ho colliso in C slot e ho trovato trasmissioni di altri in X slot;
		//pcoll = (C+X)/B;
		//printf("%d - %s\n",j, iface_wlan);
		//j++;
	}
	fclose(log_int_aloha);
	fclose(log_slot_aloha);
}

void init_options(struct logic_options * current_logic_options){
	current_logic_options->protocol_1_path="";
	current_logic_options->log_file_name="";
}

void int_aloha_usage(void)
{
	printf("%s",int_aloha_usageMenu);
}


void parseArgs(int argc, char **argv, struct logic_options * current_options)
{
	static int verbose_flag;
	int option_index = 0;
	
	static struct option long_option[] = {
	          {"tx-macaddress",		required_argument,	0,	'1' },
		  {"channel",			required_argument,	0,	'2' },
		  {"timeslot",			required_argument,	0,  	'3' },
		  {0,				0,			0,	 0  }
	};
	init_options(current_options);

	FILE * file;
	int c;
	int function_sesult;
	/*
	//autobytecode variable
	  unsigned char addr[6];
	    addr[0]=0xFF;
	    addr[1]=0xFF;
	    addr[2]=0xFF;
	    addr[3]=0xFF;
	    addr[4]=0xFF;
	    addr[5]=0xFF;
	  unsigned int timer[4];
	    timer[0]=0;
	    timer[1]=0;
	    timer[2]=0;
	    timer[3]=0;
	  int source_file=0;
	*/
	if ( argc == 1){
		int_aloha_usage();
		exit(0);
	}
	while((c = getopt_long(argc, argv, "1:l:w:h", long_option, &option_index )) != -1) {
	
		switch(c) {
		  
		  case '1':
			current_options->protocol_1_path =optarg; //atoi(optarg);
			break;

		  case 'l':
			current_options->log_file_name=optarg;
			break;
	
		  case 'h':
			int_aloha_usage();
			exit(0);
			break;

		  case 'w':
			current_options->slot_window=atoi(optarg);
			break;

		  default:
		       fprintf(stderr, "error check the help with option -h\n\n");
		       exit(1);
		       break;
		}
	} 
}


/*
 * run with:
 *  ./int-aloha -1 aloha-slot-probability-always.txt 
 */

int main(int argc, char *argv[])
{
	struct protocol_suite suite;
	struct logic_options current_options;
	//printf("%s\n\n",argv[0]);
	parseArgs(argc, argv, &current_options);

	init_protocol_suite(&suite, 1, 1);
	/*
	suite.protocols[0].emulator = aloha_emulate;
	struct aloha_param aloha_parameter0;
	aloha_parameter0.persistance = 0.25;
	suite.protocols[0].parameter = &aloha_parameter0;
	*/
	suite.protocols[0].name = "Aloha";
	suite.protocols[0].fsm_path = current_options.protocol_1_path;

	struct debugfs_file df;
	init_file(&df);
	int_aloha_loop(&df, &suite, &current_options);
}
