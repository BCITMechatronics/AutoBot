/*
 * Autobot_Encoder.c
 *
 *  Created on: Apr 6, 2024
 *      Author: haduy
 */
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
#include <Autobot_Encoder.h>
#include <Autobot_MotorControl.h>
//GLOBAL
volatile unsigned char encoderAPrevState = 0;
volatile unsigned char encoderBPrevState = 0;

volatile long int EncoderCount = 0;
volatile long int prevEncoderCount = 0;
volatile long int DeltaCount[256];
volatile long int velocity = 0;
volatile int indexCount=0;
volatile long int prevEncoderCountSpeed=0;
volatile long int Sample_Speed[500];
volatile unsigned char init_Count=2; // 0 ready for calibrate //1 is durring //2 is finish
volatile unsigned char finish_Calibrate=0; //0 not finish/ 1 finish
volatile long int Total_Of_Count=0;
uint16_t cpuTimer0IntCount;
uint16_t cpuTimer1IntCount;
uint16_t cpuTimer2IntCount;
//15      GPIO58      Encoder channel A
//14      GPIO59      Encoder channel B
//13      GPIO124     Encoder index channel M
void Calibrate() // 1 day / Dont fking touching this fuction
{
    GPIO_disableInterrupt(GPIO_INT_XINT4);
    GPIO_disableInterrupt(GPIO_INT_XINT5);
    init_Count=0;
    MotorDriver_setDirection(MOVE_UP);
    MotorDriver_setSpeed(100);
    unsigned char LScheckUp=1,LScheckDown=1;
    DEVICE_DELAY_US(100000);
    DEVICE_DELAY_US(100000);
//Not pull =1 when it hitt =0 for both UP and Down LS
    while(LScheckUp!=0)//LScheckUp==0 || LScheckDown==0LScheckUp==0 || LScheckDown==0
    {
        LScheckUp =GPIO_readPin(7);
    }
    MotorDriver_stop();
    if(init_Count==0)
    {

        EncoderCount=0; //start Measure
        MotorDriver_setDirection(MOVE_DOWN);
        MotorDriver_setSpeed(100);
        init_Count=1;
    }
    while(LScheckDown!=0)
    {
        LScheckDown =GPIO_readPin(6);
    }
    MotorDriver_stop();
    if(init_Count==1)
    {
        Total_Of_Count=abs(EncoderCount)+60000;
        EncoderCount=0;
        MotorDriver_setDirection(MOVE_UP);
        MotorDriver_setSpeed(50);
        finish_Calibrate=1;
        init_Count=2;
    }
    while(EncoderCount<=30000);
    MotorDriver_stop();

    EncoderCount=0;
    GPIO_enableInterrupt(GPIO_INT_XINT4);         // Enable XINT1
    GPIO_enableInterrupt(GPIO_INT_XINT5);         // Enable XINT2
}
void Autobot_Encoder_init()
{
    Device_init();
    Interrupt_initModule();
    Interrupt_initVectorTable();
    //
    // ISRs for each CPU Timer interrupt
    //
    Interrupt_register(INT_TIMER0, &cpuTimer0ISR);
    Interrupt_register(INT_TIMER1, &cpuTimer1ISR);
    Interrupt_register(INT_TIMER2, &cpuTimer2ISR);

    //
    // Initializes the Device Peripheral. For this example, only initialize the
    // Cpu Timers.
    //
    initCPUTimers();

    //
    // Configure CPU-Timer 0, 1, and 2 to interrupt every second:
    // 1 second Period (in uSeconds)
    //
    configCPUTimer(CPUTIMER0_BASE, DEVICE_SYSCLK_FREQ, 1000000);
    configCPUTimer(CPUTIMER1_BASE, DEVICE_SYSCLK_FREQ, 1000);
    configCPUTimer(CPUTIMER2_BASE, DEVICE_SYSCLK_FREQ, 1000000);

    //
    // To ensure precise timing, use write-only instructions to write to the
    // entire register. Therefore, if any of the configuration bits are changed
    // in configCPUTimer and initCPUTimers, the below settings must also
    // be updated.
    //
    CPUTimer_enableInterrupt(CPUTIMER0_BASE);
    CPUTimer_enableInterrupt(CPUTIMER1_BASE);
    CPUTimer_enableInterrupt(CPUTIMER2_BASE);

    //
    // To ensure precise timing, use write-only instructions to write to the
    // entire register. Therefore, if any of the configuration bits are changed
    // in configCPUTimer and initCPUTimers, the below settings must also
    // be updated.
    //
    CPUTimer_enableInterrupt(CPUTIMER0_BASE);
    CPUTimer_enableInterrupt(CPUTIMER1_BASE);
    CPUTimer_enableInterrupt(CPUTIMER2_BASE);

    //
    // Enables CPU int1, int13, and int14 which are connected to CPU-Timer 0,
    // CPU-Timer 1, and CPU-Timer 2 respectively.
    // Enable TINT0 in the PIE: Group 1 interrupt 7
    //
    Interrupt_enable(INT_TIMER0);
    Interrupt_enable(INT_TIMER1);
    Interrupt_enable(INT_TIMER2);

    //
    // Starts CPU-Timer 0, CPU-Timer 1, and CPU-Timer 2.
    //
    CPUTimer_startTimer(CPUTIMER0_BASE);
    CPUTimer_startTimer(CPUTIMER1_BASE);
    CPUTimer_startTimer(CPUTIMER2_BASE);

    ///////////ISR
    Interrupt_register(INT_XINT1, &xint1_isr);
    Interrupt_register(INT_XINT2, &xint2_isr);
    Interrupt_register(INT_XINT3, &xint3_isr);
    Interrupt_register(INT_XINT4, &xint4_isr);
    Interrupt_register(INT_XINT5, &xint5_isr);
    Interrupt_enable(INT_XINT1);
    Interrupt_enable(INT_XINT2);
    Interrupt_enable(INT_XINT3);
    Interrupt_enable(INT_XINT4);
    Interrupt_enable(INT_XINT5);


    // GPIO58 and GPIO59 are inputs
    //

    //GPIO_setQualificationMode(59, GPIO_QUAL_SYNC);
    GPIO_setPadConfig(58, GPIO_PIN_TYPE_STD);
    GPIO_setPinConfig(GPIO_58_GPIO58);
    GPIO_setPadConfig(59, GPIO_PIN_TYPE_STD);
    GPIO_setPinConfig(GPIO_59_GPIO59);
    GPIO_setPadConfig(124, GPIO_PIN_TYPE_STD);
    GPIO_setPinConfig(GPIO_124_GPIO124);
    GPIO_setDirectionMode(58,GPIO_DIR_MODE_IN);          // encoderAinput
    GPIO_setDirectionMode(59,GPIO_DIR_MODE_IN);          // encoderBinput
    GPIO_setDirectionMode(124,GPIO_DIR_MODE_IN);          // INDEX
    GPIO_setInterruptPin(58,GPIO_INT_XINT1);///encoderA
    GPIO_setInterruptPin(59,GPIO_INT_XINT2);//encoderB
    GPIO_setInterruptPin(124,GPIO_INT_XINT3);//INDEX
    GPIO_setInterruptType(GPIO_INT_XINT1,GPIO_INT_TYPE_RISING_EDGE );
    GPIO_setInterruptType(GPIO_INT_XINT2,GPIO_INT_TYPE_RISING_EDGE  );//GPIO_INT_TYPE_FALLING_EDGE
    GPIO_setInterruptType(GPIO_INT_XINT3,GPIO_INT_TYPE_RISING_EDGE  );
    // Enable XINT1,2,3,4
    GPIO_enableInterrupt(GPIO_INT_XINT1);         // Enable XINT1
    GPIO_enableInterrupt(GPIO_INT_XINT2);         // Enable XINT2
    GPIO_enableInterrupt(GPIO_INT_XINT3);         // Enable XINT3
    //////////////////////////FOR lIMIT SWITCH INT/////////////////////
    //////
    GPIO_setPadConfig(7, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO7   GPIO_PIN_TYPE_PULLUP LS_UP
    GPIO_setPinConfig(GPIO_7_GPIO7);               // GPIO7 = GPIO7 LS_UP
    GPIO_setDirectionMode(7, GPIO_DIR_MODE_IN);     // GPIO7 = input LS_UP
    GPIO_setPadConfig(6, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO6  GPIO_PIN_TYPE_STD LS_DOWN
    GPIO_setPinConfig(GPIO_6_GPIO6);                //LS_DOWN
    GPIO_setDirectionMode(6, GPIO_DIR_MODE_IN);     // GPIO6 = input LS_DOWN
    GPIO_setInterruptPin(6,GPIO_INT_XINT4);
    GPIO_setInterruptPin(7,GPIO_INT_XINT5);

    // Falling edge interrupt
    GPIO_setInterruptType(GPIO_INT_XINT4, GPIO_INT_TYPE_FALLING_EDGE);
    // // Falling edge interrupt
    GPIO_setInterruptType(GPIO_INT_XINT5, GPIO_INT_TYPE_FALLING_EDGE);
    //
    // Enable XINT1 and XINT2
    //
    GPIO_enableInterrupt(GPIO_INT_XINT4);         // Enable XINT1
    GPIO_enableInterrupt(GPIO_INT_XINT5);         // Enable XINT2
//    EINT;                                       // Enable Global Interrupts
}
//
// xint1_isr - External Interrupt 1 ISR
//
//interrupt void xint1_isr(void) //ENCODER_A
//{
//    unsigned char inputB = GPIO_readPin(59);
//    if(encoderAPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
//    {
//        // Check the state of ENCODER_B
////        unsigned char inputB = GPIO_readPin(59);
//        if (inputB==1)
//        {
//            EncoderCount++;
//        }
//        else if(inputB==0)
//        {
//            EncoderCount--;
//        }
//
//
//    }
//    else if(encoderAPrevState==1) // Falling edge (high-to-low) of ENCODER_A
//    {
//        // Check the state of ENCODER_B
////        unsigned char inputB = GPIO_readPin(59);
//        if (inputB==1)
//        {
//            EncoderCount--;
//        }
//        else if(inputB==0)
//        {
//            EncoderCount++;
//        }
//
//    }
//    if(encoderAPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
//    {
//        encoderAPrevState=1;// Toggle interrupt edge for ENCODER_A
//        GPIO_setInterruptType(GPIO_INT_XINT1, GPIO_INT_TYPE_FALLING_EDGE );// Toggle interrupt edge for ENCODER_A
//    }
//    else if (encoderAPrevState==1)
//    {
//        encoderAPrevState=0;// Toggle interrupt edge for ENCODER_A
//        GPIO_setInterruptType(GPIO_INT_XINT1, GPIO_INT_TYPE_RISING_EDGE );// Toggle interrupt edge for ENCODER_A
//    }
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);// Clear interrupt flag for ENCODER_A
//}
////
//// xint2_isr - External Interrupt 2 ISR
////
//interrupt void xint2_isr(void)  //ENCODER_B
//{
//    unsigned char inputA = GPIO_readPin(58);
//    if(encoderBPrevState==0)// Check for rising edge (low-to-high) of ENCODER_B
//    {
////        unsigned char inputA = GPIO_readPin(58);
//        if (inputA==1)
//        {
//            EncoderCount--;
//        }
//        else if(inputA==0)
//        {
//            EncoderCount++;
//        }
//
//
//    }
//    else if(encoderBPrevState==1)// Falling edge (high-to-low) of ENCODER_B
//    {
////        unsigned char inputA = GPIO_readPin(58);
//        if (inputA==1)
//        {
//            EncoderCount++;
//        }
//        else if(inputA==0)
//        {
//            EncoderCount--;
//        }
//
//
//    }
//    if(encoderBPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
//    {
//        encoderBPrevState=1;// Toggle interrupt edge for ENCODER_B
//        GPIO_setInterruptType(GPIO_INT_XINT2,GPIO_INT_TYPE_FALLING_EDGE );// Toggle interrupt edge for ENCODER_B
//    }
//    else if(encoderBPrevState==1)
//    {
//        encoderBPrevState=0;// Toggle interrupt edge for ENCODER_B
//        GPIO_setInterruptType(GPIO_INT_XINT2, GPIO_INT_TYPE_RISING_EDGE);// Toggle interrupt edge for ENCODER_B
//    }
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);// Clear interrupt flag for ENCODER_A
//}
//
//interrupt void xint3_isr(void)
//{
//    DeltaCount[i] = EncoderCount-prevEncoderCount;
//    i++;
//    prevEncoderCount = EncoderCount;
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag for ENCODER_A
//}
//
// initCPUTimers - This function initializes all three CPU timers
// to a known state.
//
void
initCPUTimers(void)
{
    //
    // Initialize timer period to maximum
    //
    CPUTimer_setPeriod(CPUTIMER0_BASE, 0xFFFFFFFF);
    CPUTimer_setPeriod(CPUTIMER1_BASE, 0xFFFFFFFF);
    CPUTimer_setPeriod(CPUTIMER2_BASE, 0xFFFFFFFF);

    //
    // Initialize pre-scale counter to divide by 1 (SYSCLKOUT)
    //
    CPUTimer_setPreScaler(CPUTIMER0_BASE, 0);
    CPUTimer_setPreScaler(CPUTIMER1_BASE, 0);
    CPUTimer_setPreScaler(CPUTIMER2_BASE, 0);

    //
    // Make sure timer is stopped
    //
    CPUTimer_stopTimer(CPUTIMER0_BASE);
    CPUTimer_stopTimer(CPUTIMER1_BASE);
    CPUTimer_stopTimer(CPUTIMER2_BASE);

    //
    // Reload all counter register with period value
    //
    CPUTimer_reloadTimerCounter(CPUTIMER0_BASE);
    CPUTimer_reloadTimerCounter(CPUTIMER1_BASE);
    CPUTimer_reloadTimerCounter(CPUTIMER2_BASE);

    //
    // Reset interrupt counter
    //
    cpuTimer0IntCount = 0;
    cpuTimer1IntCount = 0;
    cpuTimer2IntCount = 0;
}

//
// configCPUTimer - This function initializes the selected timer to the
// period specified by the "freq" and "period" parameters. The "freq" is
// entered as Hz and the period in uSeconds. The timer is held in the stopped
// state after configuration.
//
void
configCPUTimer(uint32_t cpuTimer, float freq, float period)
{
    uint32_t temp;

    //
    // Initialize timer period:
    //
    temp = (uint32_t)(freq / 1000000 * period);
    CPUTimer_setPeriod(cpuTimer, temp);

    //
    // Set pre-scale counter to divide by 1 (SYSCLKOUT):
    //
    CPUTimer_setPreScaler(cpuTimer, 0);

    //
    // Initializes timer control register. The timer is stopped, reloaded,
    // free run disabled, and interrupt enabled.
    // Additionally, the free and soft bits are set
    //
    CPUTimer_stopTimer(cpuTimer);
    CPUTimer_reloadTimerCounter(cpuTimer);
    CPUTimer_setEmulationMode(cpuTimer,
                              CPUTIMER_EMULATIONMODE_STOPAFTERNEXTDECREMENT);
    CPUTimer_enableInterrupt(cpuTimer);

    //
    // Resets interrupt counters for the three cpuTimers
    //
    if (cpuTimer == CPUTIMER0_BASE)
    {
        cpuTimer0IntCount = 0;
    }
    else if(cpuTimer == CPUTIMER1_BASE)
    {
        cpuTimer1IntCount = 0;
    }
    else if(cpuTimer == CPUTIMER2_BASE)
    {
        cpuTimer2IntCount = 0;
    }
}

//
// cpuTimer0ISR - Counter for CpuTimer0
//
//__interrupt void
//cpuTimer0ISR(void)
//{
//    cpuTimer0IntCount++;
//
//    //
//    // Acknowledge this interrupt to receive more interrupts from group 1
//    //
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
//}

//
// cpuTimer1ISR - Counter for CpuTimer1
//
//__interrupt void
//cpuTimer1ISR(void)
//{
////    //
////    // The CPU acknowledges the interrupt.
////    //
////    cpuTimer1IntCount++;
//}
//
////
//// cpuTimer2ISR - Counter for CpuTimer2
////
__interrupt void
cpuTimer2ISR(void)
{
//    //
//    // The CPU acknowledges the interrupt.
//    //
//    cpuTimer2IntCount++;
}
