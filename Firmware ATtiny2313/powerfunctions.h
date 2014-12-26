/*
 * Lego PowerFunctions definition
 *
 * powerfunctions.h
 *
 * Author:	Xander Maas, <xander@xjmaas.nl>
 * Created 23 sept 2014
 *
 * Copyright (c) 2014. All rights reserved.
 *
 * This header file is based on the PowerFunctions project for the Arduino
 * by Jurriaan
 * (https://github.com/jurriaan/Arduino-PowerFunctions/blob/master/PowerFunctions.h)
 *
 * This header file contains the 'public' definitions
 */

#ifndef PowerFunctions_h
#define PowerFunctions_h

#define COMBO_DIRECT_MODE 0x01
#define SINGLE_PIN_CONTINUOUS 0x2
#define SINGLE_PIN_TIMEOUT 0x3
#define SINGLE_OUTPUT 0x4
#define ESCAPE 0x4

#define IR_CYCLES(num) (uint16_t) ((1.0/38000.0) * 1000 * 1000 * num)

#define START_STOP          39
#define HIGH_PAUSE          21
#define LOW_PAUSE           10
#define HALF_PERIOD         0.5
#define MAX_MESSAGE_LENGTH  522 // 2 * 45 + 16 * 27

//PWM speed steps
#define PWM_FLT 0x0
#define PWM_FWD1 0x1
#define PWM_FWD2 0x2
#define PWM_FWD3 0x3
#define PWM_FWD4 0x4
#define PWM_FWD5 0x5
#define PWM_FWD6 0x6
#define PWM_FWD7 0x7
#define PWM_BRK 0x8
#define PWM_REV7 0x9
#define PWM_REV6 0xA
#define PWM_REV5 0xB
#define PWM_REV4 0xC
#define PWM_REV3 0xD
#define PWM_REV2 0xE
#define PWM_REV1 0xf

//speed
/*
#define RED_FLT 0x0
#define RED_FWD 0x1
#define RED_REV 0x2
#define RED_BRK 0x3
#define BLUE_FLT 0x0
#define BLUE_FWD 0x4
#define BLUE_REV 0x8
#define BLUE_BRK 0xC
*/

//output
#define RED 0x0
#define BLUE 0x1
#endif
