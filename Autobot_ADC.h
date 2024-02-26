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
void ADC_init();
void configureADC(uint32_t adcBase);
void setupADCContinuous(uint32_t adcBase, uint32_t channel);

#define RESULTS_BUFFER_SIZE     256 //buffer for storing conversion results
                                //(size must be multiple of 16)
#define EX_ADC_RESOLUTION       16

#endif /* AUTOBOT_ADC_H_ */
