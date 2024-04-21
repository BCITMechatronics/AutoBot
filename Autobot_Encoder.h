/*
 * Autobot_Encoder.h
 *
 *  Created on: Apr 6, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_ENCODER_H_
#define AUTOBOT_ENCODER_H_
#include "driverlib.h"
#include "device.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <stdbool.h>
#include <float.h>
#include <limits.h>
#include <stdint.h>
// Defines
//GPIO19 A      PIN3
//GPIO18 B      PIN4
//GPIO67 Index  PIN5
//
// Function Prototypes
//
interrupt void xint1_isr(void);
interrupt void xint2_isr(void);
interrupt void xint3_isr(void);
interrupt void xint4_isr(void);
interrupt void xint5_isr(void);
//Global
extern volatile unsigned char encoderAPrevState;
extern volatile unsigned char encoderBPrevState;
extern volatile long int EncoderCount;
extern volatile long int prevEncoderCount;
extern volatile long int DeltaCount[256];
extern volatile long int velocity;
extern volatile int indexCount;
extern volatile long int prevEncoderCountSpeed;
extern volatile long int Sample_Speed[500];
extern volatile unsigned char init_Count; // 0 ready for calibrate //1 is durring //2 is finish
extern volatile unsigned char finish_Calibrate; //0 not finish/ 1 finish
extern volatile long int Total_Of_Count;
///Timer
// Function Prototypes
//
__interrupt void cpuTimer0ISR(void);
__interrupt void cpuTimer1ISR(void);
__interrupt void cpuTimer2ISR(void);
void initCPUTimers(void);
void configCPUTimer(uint32_t, float, float);
void Calibrate();
//
// Globals
//
extern uint16_t cpuTimer0IntCount;
extern uint16_t cpuTimer1IntCount;
extern uint16_t cpuTimer2IntCount;

void Autobot_Encoder_init();
#endif /* AUTOBOT_ENCODER_H_ */
