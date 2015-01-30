/*
 * Lego PowerFunctions I2C Slave
 *
 * main.h
 *
 * Author:	Xander Maas, <xander@xjmaas.nl>
 * Created:	17 oct 2014
 *
 * Copyright (c) 2014, Xander Maas
 * Copyright (c) 2010, Russel Bull (Multi-tasking code)
 *
 * License:
 *      This program is free software; you can redistribute it and/or modify it
 *      under the terms of the GNU General Public License as published by the
 *      Free Software Foundation; either version 2 of the License, or (at your
 *      option) any later version.
 *
 *      This program is distributed in the hope that it will be useful, but
 *      WITHOUT ANY WARRANTY; without even the implied warranty of
 *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *      GNU General Public License for more details.
 *
 * Warranties:
 *      NONE, USE AT OWN RISK
 *
 * Note(s):
 *      This file is based on code from avrfreaks.net
 *      Thread => [TUT][C]Multi-tasking tutorial part 1
 *      (http://www.avrfreaks.net/forum/tutc-multi-tasking-tutorial-part-1)
 *      The code on which the multi-tasking os based is copyrighted, but free
 *      for any use.
 *
 * Change history:
 *      date        Description
 *      26 Dec 2014 First public release.
 */

/*
 * COMPILE OPTIONS
 */
#ifndef F_CPU
#define F_CPU 8000000UL
#endif

/*
 * Forward function declarations
 */

// Initialization functions
void init_device(void);
void timer0_init(void);
void timer1_init(void);

// Multi-tasking functions
void task_reset(unsigned char task);
void task_set(unsigned char task);
void task_dispatch(void);

// I2C functions
void setupI2C(void);
uint8_t i2cAddress(void);
uint8_t i2cReadFromRegister(uint8_t reg);
void i2cWriteToRegister(uint8_t reg, uint8_t value);

// PowerFunctions functions
void process_command(uint16_t command);
void send_bit(uint8_t pause);
void pause(uint8_t count);
void start_stop_bit(void);

// The tasks we want to perform
void task0(void);
void task1(void);

// Debugging using Serial
void init_serial(void);
void send_string(char *msg);
void converted_byte(char byte1, char byte2);

/*
 * Multi-tasking
 */

// TIMER0 settings/calculations for Multi-tasking
#define T0_PRESCALER    1024
#define T0_F_OUT        100     /* 100 Hz == 10 ms per tick */
#define OCR0A_VALUE     ((((F_CPU / 2) / T0_PRESCALER) / T0_F_OUT) -1)
#define OCR0A_DEBUG     PB2

// Define the number of tasks
#define NUM_TASKS 2

// lsb is high priority task
unsigned char task_bits = 0;

// If non-zero, a tick has elapsed
// Used by TIMER0
volatile char tick_flag = 0;

// Init the timers to 0 on startup
unsigned int task_timers[NUM_TASKS] = {0, 0};

// Value -> bitmask translate table
static const unsigned PROGMEM char bit_mask[] = {1, 2, 4, 16, 32, 64, 128};

/* 
 * Input/Output
 */

#ifdef DEBUG
// DEBUGGING I2C PINS (LED OUTPUTS)
#define I2C_RCVD_LOW	PD0
#define I2C_RCVD_HGH	PD1
#endif

/*
 * I2C
 */

// Version
#define MAJOR_VERSION 	0
#define MINOR_VERSION 	1	
#define REVISION 		0
#define RELEASE 		'R'	//	A == 0x41 == Alpha
							//	B == 0x42 == Bravo
							//	R == 0x52 == Release Candidate
							//	G == 0x47 == Gold Master

// Address pins
#define ADDR_PIN0		PD2
#define ADDR_PIN1		PD3

/*
 * LEGO powerFunctions
 */

// TIMER0 Settings for LEGO Powerfunctions
#define T1_PRESCALER    1
#define T1_F_OUT        38000   /* 38 kHz           */
#define OCR1A_VALUE     ((((F_CPU / 2) / T1_PRESCALER) / T1_F_OUT) -1)

// We count here in half cycles ;)
#define MARK            12      // 6 Cycles
#define PAUSE_STARTSTOP 2 * START_STOP
#define PAUSE_HIGH      2 * HIGH_PAUSE
#define PAUSE_LOW       2 * LOW_PAUSE
#define MAX_MSG_LNGTH   2 * MAX_MESSAGE_LENGTH

// Flags to determine the state of the through I2C received command
volatile uint8_t PFREG0 = 0x00;
#define PFLB			0		// Is set when the low byte has been received
#define PFHB			1		// Is set when the high byte has been received
#define PFCMD0			2		// Is set when a complete command has been
                                // received

volatile uint8_t send_command = 0;
volatile uint16_t cycles_count = 0;

volatile uint8_t calc_pause = 0;

// The place to store our high and low byte(s) of the command
// we want to send to our PF enabled device
volatile uint8_t lowByte;
volatile uint8_t highByte;

// Channel value has already been corrected in the code
// e.g. an address of 0 if channel 1
static volatile uint8_t channel;
volatile uint16_t pfCommand;


// Debugging
char *converted;
