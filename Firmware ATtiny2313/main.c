/*
 * Lego PowerFunctions I2C Slave
 *
 * main.c
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
 *      30 Jan 2015	Added a checksum recalculation to task1() as we also have
 *      			to toggle a bit in nibble1 of the pfCommand
 *      31 Jan 2015	Found aout that Combo PWM uses the Escape bit and moves the
 *      			address bit to bit 0 of nibble 1. We don't want to toggle
 *      			this bit when using Combo PWM
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include "usiTwiSlave.h"
#include "main.h"
#include "powerfunctions.h"

/*
 * A task gets dispatched every tick_flag tick
 */
void task_dispatch(void) {
	// Scan the task bits for an active task and execute it
	unsigned char task;

	// Take care of the task timers. If the value == 0, skip it
	// else decrement it. If it decrements to zero (0), activate the task
	// associated with it
	task = 0 ;
	while ( task < NUM_TASKS ) {
		if ( task_timers[task] ) {
			// Decrement the timer
			task_timers[task]--;
			if ( task_timers[task] == 0 ) {
				// If == 0, activate the task bit
				task_set(task);
			}
		}
		task++;
	}

	// Start with the most significant task
	task = 0;

	while ( task < NUM_TASKS ) {
		if ( (task_bits & pgm_read_byte(&bit_mask[task])) ) {
			// If active task has been found ...
			break;
		}
		// Otherwise try the next task
		task++;
	}
	switch ( task ) {
         case 0:
			task0();
			break;
		case 1:
			task1();
			break;
        // No tasks were active!!
		default:
			break;
	}
}

/*
 * Enable a task for execution
 */
void task_set(unsigned char task) {
	// Sets a task bit
	task_bits |= pgm_read_byte(&bit_mask[task]);
}

/*
 * Disables a task
 */
void task_reset(unsigned char task) {
	// Resets a task bit
	task_bits &= (~pgm_read_byte(&bit_mask[task]));
}

/*
 * The tasks
 */
// This task will test the PFREG0 register and act accordingly if both values
// have been received (both bits PFLB and PFHB are set)
void task0(void) {
	// We want to run this task every 100ms (== 10Hz)
	task_timers[0] = 10;
    
	// Check if th PFWORD flasg is set (both bytes have been received)
	if ( (PFREG0 & ((1 << PFLB) | (1 << PFHB))) ) {
        pfCommand = ((uint16_t)highByte << 8) | lowByte;
        
		// Make sure the PFREG0 register is updated, so we know a new
		// command has been received
		PFREG0 |= (1 << PFCMD0);

		// Before we return, reset the PFREG0 bits and the I2C registers
		PFREG0 &= ~(1 << PFLB);
		PFREG0 &= ~(1 << PFHB);
        highByte = 0x00;
        lowByte = 0x00;
	}
	// When the task has finished, reset the task
	task_reset(0);
}

// This task will be used to process the received command
// It will run every 100mSec
void task1(void) {
    task_timers[1] = 10;
    
#ifdef DEBUG
    PORTD |= (1 << PD6);
#endif
    
    if ( (PFREG0 & (1 << PFCMD0)) ) {
        converted_byte(highByte, lowByte);
        // if a (complete) PF command has been received (2 bytes)
        // process it
        for ( uint8_t i = 0; i < 6; i++ ) {
			// We have to toggle the Toggle bit, but this also implies a
			// recalculation of nibble 4 (checksum)
			uint8_t nib1 = pfCommand >> 12 & 0xf;
			uint8_t nib2 = pfCommand >> 8 & 0xf;
			uint8_t nib3 = pfCommand >> 4 & 0xf;
			
			// We only want to toggle this bit when bit 3 is NOT set
			// Which means, we are using PWM Combo mode
			if ((nib1 & ~(1 << 2))) {
				// Toggle the bit (MSB in nibble)
				nib1 = nib1 ^ 8;
			}
			uint8_t nib4 = 0xf ^ nib1 ^ nib2 ^ nib3;
			// Constuct our new command
			pfCommand = nib1 << 12 | nib2 << 8 | nib3 << 4 | nib4;
            // Send the command 6 times!
            pause(i);

            process_command(pfCommand);
        }
    }

#ifdef DEBUG
    PORTD &= ~(1 << PD6);
#endif
    
    // Reset the bits in the PFREG0 register
    PFREG0 &= ~(1 << PFCMD0);
    PFREG0 &= ~(1 << PFHB);
    PFREG0 &= ~(1 << PFLB);
    /*
#ifdef DEBUG
    // Clear the two test LEDS
    PORTD &= ~(1 << I2C_RCVD_LOW);
    PORTD &= ~(1 << I2C_RCVD_HGH);
#endif
     */
    
	// When the task has finished, reset the task
	task_reset(1);
}

/*
 * Call this routine to initialize all peripherals
 */
void init_devices(void) {
	// Stop all errant interrupts until we have setup the MCU
	cli();

#ifdef DEBUG
    /*
	DDRD |= (1 << I2C_RCVD_LOW);
	PORTD &= ~(1 << I2C_RCVD_LOW);
	DDRD |= (1 <<  I2C_RCVD_HGH);
	PORTD &= ~(1 << I2C_RCVD_HGH);
    */
    
    // Also for debug purposes
    DDRB |= (1 << PB0) | (1 << PB1);
    DDRD |= (1 << PD4) | (1 << PD6);
    
    // Turn them off initially
    PORTB &= ~(1 << PB0);
    PORTB &= ~(1 << PB1);
    PORTD &= ~(1 << PD4);
    PORTD &= ~(1 << PD6);
#endif

	// Initialize TIMER0
	timer0_init();
    
    // Initialize TIMER1
    timer1_init();
    
    // Re-enable all interrupts
	sei();

    init_serial();
    
	// Set up our I2C interface/bus
	setupI2C();
}

/* 
 * Initialize our serial port
 */
void init_serial(void) {
    UBRRL = 25;             /* 19200 baud */
    
    UCSRB = (1 << RXEN) | (1 << TXEN);
    UCSRC = (1 << UCSZ1) | (1 << UCSZ0);
}

void converted_byte(char byte1, char byte2) {
    
    unsigned char buf[] = { byte1, byte2};
    
    char str[20];
    
    unsigned char *pin = buf;
    const char *hex = "0123456789ABCDEF";
    char *pout = str;
    int i = 0;
    for ( i = 0; i < sizeof(buf)-1; i++) {
        *pout++ = hex[(*pin>>4)&0xf];
        *pout++ = hex[(*pin++)&0xf];
    }
    *pout++ = hex[(*pin>>4)&0xf];
    *pout++ = hex[(*pin++)&0xf];
    //    *pout = 0x00; // Null-terminator
    
    converted =  str;
}


void usart_putchar(char data) {
    // Wait for empty transmit buffer
    while ( !(UCSRA & (_BV(UDRE))) );
    // Start transmission
    UDR = data;
}

/*
 * Send string over serial
 */
void send_string(char *msg) {
    while ( *msg ) {
        usart_putchar( *msg);
        msg++;
    }
}

/* 
 * Initialize TIMER0 - The timer we use for the tasks
 * WGM:				CTC
 * Pre-Scale:		1024
 * Desired value:	10 mSec
 * Actual value:	9.8 mSec
 */
void timer0_init(void) {
	// Stop
	TCCR0B = 0x00;

	// Set the count
	TCNT0 = 0x00;

	// Set CTC Mode
	TCCR0A |= (1 << WGM01);

    // Use Compare Interrupt Register A for TIMER0
    TIMSK |= (1 << OCIE0A);
    
	// Set the count value
    OCR0A = OCR0A_VALUE;

	// Start TIMER0 by setting the pre-scale
	TCCR0B |= (1 << CS00);
	TCCR0B |= (1 << CS02);
}

/* Initialize TIMER1 - The timer we want to use to create the 76kHz
 * carrier later on. First we want to test it with 2 Hz carrier.
 * The actual blink rate will be half... 1 cycle will be used to 
 * turn the LED on, the other will be used to turn the LED off
 *
 * 1Hz blink, 2Hz carrier
 * WGM:             CTC
 * Pre-Scale:       64
 * Desired value:   500 mSec
 * Actual value:    499.992 mSec (rounding issue?)
 * Desired counter: 62499
 * actual counter:  62499 == 0xf423
 *
 * 38kHz blink, 76kHz carrier
 * WGM:             CTC
 * Pre-Scale:       1
 * Desired value:   13.157 uSec
 * Actual value:    13.000 uSec
 * Desired counter: 104.3
 * Actual counter:  104 == 0x68
 */
void timer1_init(void) {
    // Mode:            CTC     WGM[13:10]  = 0100
    // Prescale:        1       CS[12:10]   = 001
    // Compare Match:   toggle  COM1A[1:0]  = 01

    // First stop the timer
    TCCR1B = 0x00;
    
    // Use Compare Interrupt Register A from TIMER1
    TIMSK |= (1 << OCIE1A);
    
    // Set OCR1A to our calculated value
    OCR1A = (uint16_t) OCR1A_VALUE;
    
    // Set the mode
    TCCR1B |= (1 << WGM12);
    
    // Set the compare match toggle on OC1A
    TCCR1A |= (1 << COM1A0);
    
    // Start the timer by setting the prescale value
    TCCR1B |= (1 << CS10);
}

/*
 * The interrupt handler(s)
 */
ISR (TIMER0_COMPA_vect) {
	// TIMER0 has overflowed
	tick_flag = 1;
}

ISR (TIMER1_COMPA_vect) {
    // empty by design
#ifdef DEBUG
    PORTD ^= (1 << PD4);
#endif
    cycles_count++;
}

/*
 * This sets up the I2C bus
 */
void setupI2C(void) {
	usiTwiSlaveInit(i2cAddress(),
			i2cReadFromRegister,
			i2cWriteToRegister);
}

/*
 * Determine the slave address we are listening on
 */
uint8_t i2cAddress(void) {
	// We use two pins to 'create' the address we are listening on
	// Set the two address pins as inputs
	DDRD &= ~(1 << ADDR_PIN0);
	DDRD &= ~(1 << ADDR_PIN1);

	// Disable the internal Pull-Up resistors
	PORTD &= ~(1 << ADDR_PIN0);
	PORTD &= ~(1 << ADDR_PIN1);

	// The base address is 0x40
	uint8_t address = 0x40;

	// The bit mask is 00001100b == 12 == 0x0c
	uint8_t subAddress = ~PIND & 0x0c;

	// Right shift the subAddress 2 bits
	subAddress = (subAddress >> 2);

	// Store our channel (which is the subAddress + 1)
	channel = subAddress + 1;

	// Store our address
	address = address + subAddress;

	return address;
}

uint8_t i2cReadFromRegister(uint8_t reg) {
	switch (reg) {
		case 0:
			//Return the major version number
			return MAJOR_VERSION;
			break;
		case 1:
			// Return minor version number
			return MINOR_VERSION;
			break;
		case 2:
			// Return revision number
			return REVISION;
			break;
		case 3:
			// Return release
			return RELEASE;
			break;
		case 10:
			// Return byte #1 of the board identification
			return 'P';
			break;
		case 11:
			// Return byte #2 of the board identification
			return 'F';
			break;
		case 12:
			// Return byte #3 of the board identification
			return 'X';
			break;
		case 13:
			// Return byte #4 of the board identification
			return 'M';
			break;
		default:
			// Seems the master queried an unsupported register
			// return 0xff
			return 0xff;
	}
}

void i2cWriteToRegister(uint8_t reg, uint8_t value) {
	switch (reg) {
		case 30:
			// we received a value for the lowByte
			if ( lowByte != value ) {
				// If the value has changed, store this
                lowByte = value;
			}
			// Either way, a new value has been received, so set the PFLB 
			// register
			PFREG0 |= (1 << PFLB);
            //PORTD ^= (1 << I2C_RCVD_LOW);
			break;
		case 31:
			if ( highByte != value ) {
				highByte = value;
			}
			// Either way, a new value has been received, so set the PFHB
			// register
			PFREG0 |= (1 << PFHB);
            //PORTD ^= (1 << I2C_RCVD_HGH);
			break;
        default:
            break;
	}
}

/*
 * Functions we need for PowerFunctions
 */
/*
 * Command Processing
 */
void process_command(uint16_t command) {
    
    start_stop_bit();
    
    for ( uint8_t i = 0; i < 16; i++ ) {
        if ( (0x8000 & (command << i)) != 0 ) {
            send_bit(PAUSE_HIGH);
            //send_string("1");
        } else {
            send_bit(PAUSE_LOW);
            //send_string("0");
        }
    }
    //send_string("\n\r");
    start_stop_bit();
}

void send_bit(uint8_t pause) {
    cycles_count = 0;
    
    // Set PB3 as output, enabling OC1A
    DDRB |= (1 << PB3);
    
    // First send the HIGH MARK
    while ( cycles_count < MARK ) {
        __asm __volatile ("nop");
    }
    
    // Clear PB3 as output, disabling PB3
    DDRB &= ~(1 << PB3);
    
    // Reset the cycles_count & send_command flag
    cycles_count = 0;
    
    // Send nothing, just count the cycles
    while ( cycles_count < pause ) {
        __asm __volatile ("nop");
    }
}

void pause(uint8_t count) {
    uint8_t pause = 0;
    switch ( count ) {
        case 0:
            pause = 4 - channel;
            break;
        case 1:
        case 2:
            pause = 5;
        default:
            pause = 5 + (2 * channel);
            break;
    }
    cycles_count = 0;
    // uint16_t cycles_wait = pause * MAX_MSG_LNGTH;
    // In a lot of other implementations I find references to 77 µs as
    // multiplication factor, which means about 3 cycles (2.9) (!!)
    uint16_t cycles_wait = pause * 3;
    while ( cycles_count < cycles_wait) {
        __asm __volatile ("nop");
    }
    
}

void start_stop_bit(void) {
    send_bit(PAUSE_STARTSTOP);
}

/*
 * Main program loop
 */
int main(void) {
	init_devices();
    
	// Start the needed tasks(s)
    task_set(0);
    task_set(1);

    // Main loop
	while (1) {
		if ( tick_flag) {
			tick_flag = 0;
			task_dispatch();
		}
	}
	return 0;
}

