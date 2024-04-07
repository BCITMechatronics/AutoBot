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
extern volatile long long int EncoderCount;
extern volatile long long int prevEncoderCount;
extern volatile long long int DeltaCount[256];
extern volatile long long int velocity;
extern volatile int indexCount;
extern volatile long long int prevEncoderCountSpeed;
extern volatile long long int Sample_Speed[500];
///Timer
// Function Prototypes
//
__interrupt void cpuTimer0ISR(void);
__interrupt void cpuTimer1ISR(void);
__interrupt void cpuTimer2ISR(void);
void initCPUTimers(void);
void configCPUTimer(uint32_t, float, float);
//
// Globals
//
extern uint16_t cpuTimer0IntCount;
extern uint16_t cpuTimer1IntCount;
extern uint16_t cpuTimer2IntCount;

void Autobot_Encoder_init();
#endif /* AUTOBOT_ENCODER_H_ */
