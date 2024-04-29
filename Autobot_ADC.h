/*
 * Autobot_ADC.h
 *
 *  Created on: Feb 25, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_ADC_H_
#define AUTOBOT_ADC_H_
// Included Files
//
#include "driverlib.h"
#include "device.h"

//
#define EX_ADC_RESOLUTION       12
// 12 for 12-bit conversion resolution, which supports (ADC_MODE_SINGLE_ENDED)
// Sample on single pin (VREFLO is the low reference)
// Or 16 for 16-bit conversion resolution, which supports (ADC_MODE_DIFFERENTIAL)
// Sample on pair of pins (difference between pins is converted, subject to
// common mode voltage requirements; see the device data manual)

// Function Prototypes
//
//
long map(long x, long in_min, long in_max, long out_min, long out_max);
void Autobot_ADC_init();
void initADCs(void);
void initADCSOCs(void);
extern int16_t adcAResult0;
extern int16_t adcAResult1;
//extern uint16_t adcAResult0;
//extern uint16_t adcAResult1;
extern uint16_t adcDResult0;
extern uint16_t adcDResult1;

#endif /* AUTOBOT_ADC_H_ */
