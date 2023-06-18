/* 
 *
 *  PRU Debug Program
 *  (c) Copyright 2011 by Arctica Technologies
 *  Written by Steven Anderson
 *
 */

#include <stdio.h>

#include "prudbg.h"

void printhelp()
{
	printf("Command help\n\n");

	printf("    Note: A brief version of help is available with the command HB\n\n");

	printf("    - Commands are case insensitive\n");
	printf("    - Address and numeric values can be dec (ex 12), hex (ex 0xC), or octal\n");
	printf("      (ex 014)\n");
	printf("    - Memory addresses can be wa=32-bit word address, ba=byte address.  Suffix\n");
	printf("      of i=instruction or d=data memory\n");
	printf("    - Return without a command will rerun a previous D, DD, or DI command while\n");
	printf("      displaying the next block\n");
	printf("    - Return without a command will rerun a previous SS\n\n");

	printf("    Note 1: Addresses, whether absolute, relative, or offsets, are all indexed\n");
	printf("            by 32 bit words, and not bytes. This means that addresses, lengths,\n");
	printf("            and offets taken from the Texas Instruments documentation need\n");
	printf("            to by divided by 4 (shifted right 2 bits) when used in all memory\n");
	printf("            commands below\n\n");

	printf("    Note 2: Vertical bars designate command aliases: e.g. 'BR | B' signifies\n");
	printf("            either BR or B as the command\n\n");

	printf("    BR | B [breakpoint_number [address]]\n");
	printf("    View or set an instruction breakpoint\n");
	printf("       -'b' by itself will display current breakpoints\n");
	printf("       - breakpoint_number is the breakpoint reference and ranges from 0 to %u\n", MAX_BREAKPOINTS - 1);
	printf("       - address is the instruction word address at which the processor should\n");
	printf("         stop (instruction is not executed)\n");
	printf("       - if no address is provided, then the breakpoint is cleared\n\n");

	printf("    D memory_location [length]\n");
	printf("    Global PRUSS memory map data dump (indexed by 32 bit words, not bytes)\n\n");

	printf("    DD memory_location [length]\n");
	printf("    Global memory map data dump starting at current PRU's local data RAM\n");
	printf("    (indexed by 32 bit words, not bytes)\n\n");

	printf("    DI memory_location [length]\n");
	printf("    Dump instruction memory for current PRU (indexed by 32 bit words, not bytes)\n\n");

	printf("    DIS | II  memory_location [length]\n");
	printf("    Disassemble instruction memory of current PRU (indexed by 32 bit words, not bytes)\n\n");

	printf("    DISIP | I  [inst_cnt_prior [inst_cnt_after]]\n");
	printf("    Disassemble instruction memory of current PRU around the instruction pointer(IP).\n");
	printf("    inst_cnt_prior is number of instructions to display preceding the IP.\n");
	printf("    inst_cnt_after is number of instructions to display after the IP.\n\n");

	printf("    G\n");
	printf("    Start processor execution of instructions (at current IP)\n\n");

	printf("    GSS | GS\n");
	printf("    Start processor execution using automatic single stepping - this allows\n");
	printf("    running a program with breakpoints\n\n");

	printf("    HALT | H\n");
	printf("    Halt the processor\n\n");

	printf("    L memory_location file_name\n");
	printf("    Load program file into instruction memory at 32-bit word address provided\n");
	printf("    (offset from beginning of instruction memory)\n\n");

	printf("    PRU | P pru_number\n");
	printf("    Set the active PRU where pru_number ranges from 0 to %u\n", NUM_OF_PRU - 1);
	printf("    Some debugger commands do action on active PRU (such as halt and reset)\n\n");

	printf("    Q\n");
	printf("    Quit the debugger and return to shell prompt.\n\n");

	printf("    R\n");
	printf("    Display the current PRU registers.\n\n");

	printf("    RESET | T\n");
	printf("    Reset the current PRU\n\n");

	printf("    SS | S \n");
	printf("    Single step the current instruction.\n\n");

	printf("    WA [watch_num [address [value]]]\n");
	printf("    Clear or set a watch point\n");
	printf("      format 1:  wa - print watch point list\n");
	printf("      format 2:  wa watch_num - clear watch point watch_num\n");
	printf("      format 3:  wa watch_num address - set a watch point (watch_num) so any\n");
	printf("                 change at that word address in data memory will be printed\n");
	printf("                 during program execution with gss command\n");
	printf("      format 4:  wa watch_num address value - set a watch point (watch_num)\n");
	printf("                 so that the program (run with gss) will be halted when the\n");
	printf("                 memory location equals the value\n");
	printf("      NOTE: for watchpoints to work, you must use gss command to run the\n");
	printf("            program\n\n");

	printf("    WR memory_location value1 [value2 [value3 ...]]\n");
	printf("    Write 32-bit values starting at a PRUSS memory location in its\n");
	printf("    global memory map. Memory_location is a 32-bit word index, not\n");
	printf("    a byte index\n\n");

	printf("    WRD memory_location value1 [value2 [value3 ...]]\n");
	printf("    Write 32-bit values in the current PRU's data memory\n");
	printf("    Memory_location is a 32-bit word index, not a byte index, starting\n");
	printf("    at the beginning of the current PRU's data memory.\n\n");

	printf("    WRI memory_location value1 [value2 [value3 ...]]\n");
	printf("    Write 32-bit values in the current PRU's instruction memory\n");
	printf("    Memory_location is a 32-bit word index, not a byte index, starting\n");
	printf("    at the beginning of the current PRU's instruction memory.\n\n");

	printf("\n");
}

void printhelpbrief()
{
	printf("Command help\n\n");
	printf("    Note: A vertical bar signifies an optional command alias\n\n");
	printf("    BR | B [breakpoint_number [address]] - View or set an instruction breakpoint\n");
	printf("    D memory_location [length] - Global PRUSS memory map data dump (indexed by 32 bit words, not bytes)\n");
	printf("    DD memory_location [length] - Current PRU's data RAM dump (indexed by 32 bit words, not bytes)\n");
	printf("    DI memory_location [length] - Current PRU's instruction RAM dump (indexed by 32 bit words, not bytes)\n");
	printf("    DIS | II [memory_location [length]] - Disassemble instruction memory (32-bit word offset from beginning of PRU instruction memory)\n");
	printf("    DISIP | I [inst_cnt_prior [inst_cnt_after]] - Disassemble instruction memory around instruction pointer\n");
	printf("    G - Start processor execution of instructions (at current IP)\n");
	printf("    GSS | GS - Start processor execution using automatic single stepping - this allows running a program with breakpoints\n");
	printf("    HALT | H - Halt the processor\n");
	printf("    L memory_location file_name - Load program file into instruction memory\n");
	printf("    PRU | P pru_number - Set the active PRU where pru_number ranges from 0 to %u\n", NUM_OF_PRU - 1);
	printf("    Q - Quit the debugger and return to shell prompt.\n");
	printf("    R - Display the current PRU registers.\n");
	printf("    RESET | T - Reset the current PRU\n");
	printf("    SS | S - Single step the current instruction.\n");
	printf("    WA [watch_num [address [value]]] - Clear or set a watch point\n");
	printf("    WR memory_location value1 [value2 [value3 ...]] - Write 32-bit values to PRUSS Global Memory (indexed by 32 bit words, not bytes)\n");
	printf("    WRD memory_location value1 [value2 [value3 ...]] - Write 32-bit values to current PRU's data memory (indexed by 32 bit words, not bytes)\n");
	printf("    WRI memory_location value1 [value2 [value3 ...]] - Write 32-bit values to current PRU's instruction memory (indexed by 32 bit words, not bytes)\n");

	printf("\n");
}

