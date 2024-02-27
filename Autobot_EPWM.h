/*
 * Autobot_EPWM.h
 *
 *  Created on: Feb 26, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_EPWM_H_
#define AUTOBOT_EPWM_H_
//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include <board.h>


extern volatile uint16_t compAVal;
extern volatile uint16_t compBVal;
//
// Globals
//
typedef struct
{
    uint32_t epwmModule;
    uint16_t epwmCompADirection;
    uint16_t epwmCompBDirection;
    uint16_t epwmTimerIntCount;
    uint16_t epwmMaxCompA;
    uint16_t epwmMinCompA;
    uint16_t epwmMaxCompB;
    uint16_t epwmMinCompB;
} epwmInfo;

extern epwmInfo epwm1Info;
extern epwmInfo epwm2Info;
extern epwmInfo epwm3Info;
// Defines
//
#define EPWM1_TIMER_TBPRD  2000  // Period register
#define EPWM1_MAX_CMPA     1950
#define EPWM1_MIN_CMPA     50 //50 before
#define EPWM1_MAX_CMPB     1950
#define EPWM1_MIN_CMPB       50

#define EPWM2_TIMER_TBPRD  2000  // Period register
#define EPWM2_MAX_CMPA     1950
#define EPWM2_MIN_CMPA       50
#define EPWM2_MAX_CMPB     1950
#define EPWM2_MIN_CMPB       50

#define EPWM3_TIMER_TBPRD  2000  // Period register
#define EPWM3_MAX_CMPA      950
#define EPWM3_MIN_CMPA       50
#define EPWM3_MAX_CMPB     1950
#define EPWM3_MIN_CMPB     1050

#define EPWM_CMP_UP           1
#define EPWM_CMP_DOWN         0
//
//  Function Prototypes
//
void Autobot_EPWM_init();
void initEPWM1(void);
void initEPWM2(void);
void initEPWM3(void);
__interrupt void epwm1ISR(void);
__interrupt void epwm2ISR(void);
__interrupt void epwm3ISR(void);
void updateCompare(epwmInfo*);

#endif /* AUTOBOT_EPWM_H_ */
