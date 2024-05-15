/*
 * Autobot_MotorControl.c
 *
 *  Created on: Mar 1, 2024
 *      Author: haduy
 */
#include "driverlib.h"
#include "device.h"
#include <board.h>
#include <Autobot_EPWM.h>
#include <Autobot_MotorControl.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <Autobot_Encoder.h>

void Autobot_MotorDriver_int()
{

    GPIO_setPadConfig(IN_1, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO22
    GPIO_writePin(IN_1, 1);                            // Load output latch
    GPIO_setPinConfig(GPIO_22_GPIO22);                // GPIO22 = GPIO22
    GPIO_setDirectionMode(IN_1, GPIO_DIR_MODE_OUT);    // GPIO22 = output
    GPIO_writePin(IN_1, 0);                            // Load output latch
//    /////////////////// need comment
//
//    GPIO_setPadConfig(7, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34   GPIO_PIN_TYPE_PULLUP
//    GPIO_setPinConfig(GPIO_7_GPIO7);               // GPIO34 = GPIO34
//    GPIO_setDirectionMode(7, GPIO_DIR_MODE_IN);     // GPIO34 = input
//    GPIO_setPadConfig(6, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34  GPIO_PIN_TYPE_STD
//    GPIO_setPinConfig(GPIO_6_GPIO6);               // GPIO34 = GPIO34
//    GPIO_setDirectionMode(6, GPIO_DIR_MODE_IN);     // GPIO34 = input



}

void MotorDriver_setSpeed(unsigned char SpeedInPercent)
{

    if (SpeedInPercent <= 0)
        SpeedInPercent= 0;
    else if (SpeedInPercent > 100)
        SpeedInPercent= 100;


    //                                EPWM1_MIN_CMPA);
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A,
//                                    1000.5);
//    unsigned char SpeedInCCR=0;
//    SpeedInCCR= ((SpeedInPercent*2000)/100);
    //check CMPA register inEpwm1Regs for make sure CCR1 value
    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, SpeedInPercent*20); //carefull with SpeedInPercent*20 its only good with CCR0=2000 SpeedInPercent*CCR0/100
}
void MotorDriver_setDirection(unsigned char Direction)
{
    if(Direction == MOVE_UP)
    {
        GPIO_writePin(IN_1, 1);                            // Load output latch
        DirectionStatus =  MOVE_UP;
    }
    else if(Direction == MOVE_DOWN)
    {
        GPIO_writePin(IN_1, 0);                            // Load output latch
        DirectionStatus =  MOVE_DOWN;
    }
}

void MotorDriver_stop()
{

    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
}



