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


// Function Prototypes
//
//
long map(long x, long in_min, long in_max, long out_min, long out_max);
void Autobot_ADC_init();
void configureADC(uint32_t adcBase);
void setupADCContinuous(uint32_t adcBase, uint32_t channel);

#define RESULTS_BUFFER_SIZE     256 //buffer for storing conversion results
                                //(size must be multiple of 16)
#define EX_ADC_RESOLUTION       12
// Globals

extern uint16_t adcAResults[RESULTS_BUFFER_SIZE];
extern uint16_t resultsIndex;
extern uint16_t loopCounter;

#endif /* AUTOBOT_ADC_H_ */
