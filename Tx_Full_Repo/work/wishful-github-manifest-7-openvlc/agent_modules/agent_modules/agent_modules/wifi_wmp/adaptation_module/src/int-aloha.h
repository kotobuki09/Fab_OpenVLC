#ifndef INT_ALOHA_H
#define INT_ALOHA_H

#include "libb43.h"


#define int_aloha_usageMenu "\
--------------------------------------------\n\
WMP intelligent aloha V 2.49 - 2015\n\
--------------------------------------------\n\
Usage: int_aloha [OPTIONS]\n\
\t -h \t\t\t\t Print this help text\n\
\t -1 <#> \t\t\t choose protocol path #\n\
\t -l <#> \t\t\t choose name file log \n"


struct meta_slot {
	int slot_num;
	/* 1 represents that there was a packet waiting to be transmitted,
	0 represents that there was no packet waiting to be transmitted. */
	char packet_queued : 1;
	/* 1 represents that the running protocol transmitted a frame,
	0 represents that no frame was transmitted. */
	char transmitted : 1;
	/* 1 represents that the channel was used by another node, 0
	represents channel was not used by another node. */
	char channel_busy : 1;
};

typedef double (*protocol_emulator)(void *param, int slot_num, struct meta_slot previous_slot);

struct protocol {
	/* Unique identifier. */
	int id;
	/* Readable name, such as "TDMA (slot 1)". */
	char *name;
	/* Path to the compiled (.txt) FSM implementation. */
	char *fsm_path;
	/* Protocol emulator for determining decisions of protocol locally. */
	protocol_emulator emulator;
	/* Parameter for protocol emulator. */
	void *parameter;
};

struct protocol_suite {
	/* Total number of protocols. */
	int num_protocols;
	/* Index of best protocol. Initially null. */
	int best_protocol;
	/* Index of protocol in slot 1. Null if no protocol in slot 1. */
	int slot1_protocol;
	/* Index of protocol in slot 2. Null if no protocol in slot 2. */
	int slot2_protocol;
	/* Which slot is active. 0 indicates neither are active. */
	int active_slot;
	/* Array of all protocols. */
	struct protocol *protocols;
	/* Array of weights corresponding to protocols. */
	double *weights;
	/* Factor used in computing weights. */
	double eta;
	/* Slot information for last to be emulated. */
	struct meta_slot last_slot;
};

struct logic_options{
	char * protocol_1_path;
	char * log_file_name;
	char * slot_window;
};

void init_protocol_suite(struct protocol_suite *suite, int num_protocols, double eta);
void update_weights(struct protocol_suite *suite, struct meta_slot slot);
void int_aloha_init(struct debugfs_file * df, struct protocol_suite *suite);
void int_aloha_loop(struct debugfs_file * df, struct protocol_suite *suite, struct logic_options * current_options);
void init_options(struct logic_options * current_logic_options);
void int_aloha_usage(void);
void parseArgs(int argc, char **argv, struct logic_options * current_options);

#endif // INT_ALOHA_H
