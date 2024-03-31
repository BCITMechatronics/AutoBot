/*
 * Autobot_Timer.h
 *
 *  Created on: Feb 28, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_TIMER_H_
#define AUTOBOT_TIMER_H_
#include "driverlib.h"
#include "device.h"
//
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

#endif /* AUTOBOT_TIMER_H_ */
