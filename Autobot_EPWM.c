/*
 * Autobot_EPWM.c
 *
 *  Created on: Feb 26, 2024
 *      Author: haduy
 */
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include <board.h>
#include <Autobot_EPWM.h>
volatile uint16_t compAVal;
volatile uint16_t compBVal;

epwmInfo epwm1Info;
epwmInfo epwm2Info;
epwmInfo epwm3Info;

void Autobot_EPWM_init()
{
    //pwm
        //
        // Initialize device clock and peripherals
        //
        Device_init();

        //
        // Disable pin locks and enable internal pull-ups.
        //
        Device_initGPIO();

        //
        // Initialize PIE and clear PIE registers. Disables CPU interrupts.
        //
        Interrupt_initModule();

        //
        // Initialize the PIE vector table with pointers to the shell Interrupt
        // Service Routines (ISR).
        //
        Interrupt_initVectorTable();

        //
        // For this case just init GPIO pins for ePWM1, ePWM2, ePWM3
        //
        Board_init();

        //
        // Interrupts that are used in this example are re-mapped to
        // ISR functions found within this file.
        //
        Interrupt_register(INT_EPWM1, &epwm1ISR);
        Interrupt_register(INT_EPWM2, &epwm2ISR);
        Interrupt_register(INT_EPWM3, &epwm3ISR);

        //
        // Disable sync(Freeze clock to PWM as well)
        //
        SysCtl_disablePeripheral(SYSCTL_PERIPH_CLK_TBCLKSYNC);

        initEPWM1();
        initEPWM2();
        initEPWM3();

        //
        // Enable sync and clock to PWM
        //
        SysCtl_enablePeripheral(SYSCTL_PERIPH_CLK_TBCLKSYNC);

        //
        // Enable interrupts required for this example
        //
        Interrupt_enable(INT_EPWM1);
        Interrupt_enable(INT_EPWM2);
        Interrupt_enable(INT_EPWM3);

        //
        // Enable global Interrupts and higher priority real-time debug events:
        //
        EINT;  // Enable Global interrupt INTM
        ERTM;  // Enable Global realtime interrupt DBGM
}
//
// epwm1ISR - EPWM1 ISR to update compare values
//
__interrupt void epwm1ISR(void)
{
    //
    // Update the CMPA and CMPB values
    //
//    updateCompare(&epwm1Info);

    //
    // Clear INT flag for this timer
    //
    EPWM_clearEventTriggerInterruptFlag(myEPWM1_BASE);

    //
    // Acknowledge this interrupt to receive more interrupts from group 3
    //
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP3);
}

//
// epwm2ISR - EPWM2 ISR to update compare values
//
__interrupt void epwm2ISR(void)
{
    //
    // Update the CMPA and CMPB values
    //
    updateCompare(&epwm2Info);

    //
    // Clear INT flag for this timer
    //
    EPWM_clearEventTriggerInterruptFlag(myEPWM2_BASE);

    //
    // Acknowledge this interrupt to receive more interrupts from group 3
    //
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP3);
}

//
// epwm3ISR - EPWM3 ISR to update compare values
//
__interrupt void epwm3ISR(void)
{
    //
    // Update the CMPA and CMPB values
    //
    updateCompare(&epwm3Info);

    //
    // Clear INT flag for this timer
    //
    EPWM_clearEventTriggerInterruptFlag(myEPWM3_BASE);

    //
    // Acknowledge this interrupt to receive more interrupts from group 3
    //
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP3);
}
//
// initEPWM1 - Initialize EPWM1 values
//
void initEPWM1()
{
    //
    // Setup TBCLK
    //
    EPWM_setTimeBaseCounterMode(myEPWM1_BASE, EPWM_COUNTER_MODE_UP);
    EPWM_setTimeBasePeriod(myEPWM1_BASE, EPWM1_TIMER_TBPRD);
    EPWM_disablePhaseShiftLoad(myEPWM1_BASE);
    EPWM_setPhaseShift(myEPWM1_BASE, 0U);
    EPWM_setTimeBaseCounter(myEPWM1_BASE, 0U);

    //
    // Set ePWM clock pre-scaler
    //
    EPWM_setClockPrescaler(myEPWM1_BASE,
                           EPWM_CLOCK_DIVIDER_2,
                           EPWM_HSCLOCK_DIVIDER_2);

    //
    // Setup shadow register load on ZERO
    //
    EPWM_setCounterCompareShadowLoadMode(myEPWM1_BASE,
                                         EPWM_COUNTER_COMPARE_A,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);
    EPWM_setCounterCompareShadowLoadMode(myEPWM1_BASE,
                                         EPWM_COUNTER_COMPARE_B,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);

    //
    // Set Compare values
    //
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, //change ccr1 here
//                                EPWM1_MIN_CMPA);
    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A,
                               1000);
    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_B,
                                EPWM1_MIN_CMPB);

    //
    // Set actions for ePWM1A & ePWM1B
    //
    // Set PWM1A on Zero
    EPWM_setActionQualifierAction(myEPWM1_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_HIGH,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_ZERO);
    // Clear PWM1A on event A, up count
    EPWM_setActionQualifierAction(myEPWM1_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_LOW,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPA);
    // Set PWM1B on Zero
    EPWM_setActionQualifierAction(myEPWM1_BASE,
                                  EPWM_AQ_OUTPUT_B,
                                  EPWM_AQ_OUTPUT_HIGH,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_ZERO);
    // Clear PWM1B on event B, up count
    EPWM_setActionQualifierAction(myEPWM1_BASE,
                                  EPWM_AQ_OUTPUT_B,
                                  EPWM_AQ_OUTPUT_LOW,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPB);

    //
    // Interrupt where we will change the Compare Values
    //
    EPWM_setInterruptSource(myEPWM1_BASE, EPWM_INT_TBCTR_ZERO);
    EPWM_enableInterrupt(myEPWM1_BASE);
    EPWM_setInterruptEventCount(myEPWM1_BASE, 3U);

   //
   // Information this example uses to keep track
   // of the direction the CMPA/CMPB values are
   // moving, the min and max allowed values and
   // a pointer to the correct ePWM registers
   //

    // Start by increasing CMPA & CMPB
    epwm1Info.epwmCompADirection = EPWM_CMP_UP;
    epwm1Info.epwmCompBDirection = EPWM_CMP_UP;

    // Clear interrupt counter
    epwm1Info.epwmTimerIntCount = 0;

    // Set base as ePWM1
    epwm1Info.epwmModule = myEPWM1_BASE;

    // Setup min/max CMPA/CMP values
    epwm1Info.epwmMaxCompA = EPWM1_MAX_CMPA;
    epwm1Info.epwmMinCompA = EPWM1_MIN_CMPA;
    epwm1Info.epwmMaxCompB = EPWM1_MAX_CMPB;
    epwm1Info.epwmMinCompB = EPWM1_MIN_CMPB;
}

//
// initEPWM2 - Initialize EPWM2 values
//
void initEPWM2()
{
    //
    // Setup TBCLK
    //
    EPWM_setTimeBaseCounterMode(myEPWM2_BASE, EPWM_COUNTER_MODE_UP);
    EPWM_setTimeBasePeriod(myEPWM2_BASE, EPWM2_TIMER_TBPRD);
    EPWM_disablePhaseShiftLoad(myEPWM2_BASE);
    EPWM_setPhaseShift(myEPWM2_BASE, 0U);
    EPWM_setTimeBaseCounter(myEPWM2_BASE, 0U);

    //
    // Set ePWM clock pre-scaler
    //
    EPWM_setClockPrescaler(myEPWM2_BASE,
                           EPWM_CLOCK_DIVIDER_2,
                           EPWM_HSCLOCK_DIVIDER_2);

    //
    // Setup shadow register load on ZERO
    //
    EPWM_setCounterCompareShadowLoadMode(myEPWM2_BASE,
                                         EPWM_COUNTER_COMPARE_A,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);
    EPWM_setCounterCompareShadowLoadMode(myEPWM2_BASE,
                                         EPWM_COUNTER_COMPARE_B,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);

    //
    // Set Compare values
    //
    EPWM_setCounterCompareValue(myEPWM2_BASE, EPWM_COUNTER_COMPARE_A,
                                EPWM2_MIN_CMPA);
    EPWM_setCounterCompareValue(myEPWM2_BASE, EPWM_COUNTER_COMPARE_B,
                                EPWM2_MAX_CMPB);

    //
    // Set actions for ePWM1A & ePWM1B
    //
    // Clear PWM2A on period and set on event A, up-count
    EPWM_setActionQualifierAction(myEPWM2_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_LOW,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_PERIOD);
    EPWM_setActionQualifierAction(myEPWM2_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_HIGH,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPA);

    // Clear PWM2B on Period & set on event B, up-count
    EPWM_setActionQualifierAction(myEPWM2_BASE,
                                  EPWM_AQ_OUTPUT_B,
                                  EPWM_AQ_OUTPUT_LOW,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_PERIOD);
    EPWM_setActionQualifierAction(myEPWM2_BASE,
                                  EPWM_AQ_OUTPUT_B,
                                  EPWM_AQ_OUTPUT_HIGH,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPB);

    //
    // Interrupt where we will change the Compare Values
    //
    EPWM_setInterruptSource(myEPWM2_BASE, EPWM_INT_TBCTR_ZERO);
    EPWM_enableInterrupt(myEPWM2_BASE);
    EPWM_setInterruptEventCount(myEPWM2_BASE, 3U);

    //
    // Information this example uses to keep track
    // of the direction the CMPA/CMPB values are
    // moving, the min and max allowed values and
    // a pointer to the correct ePWM registers
    //

    // Start by increasing CMPA & decreasing CMPB
    epwm2Info.epwmCompADirection = EPWM_CMP_UP;
    epwm2Info.epwmCompBDirection = EPWM_CMP_DOWN;

    // Clear interrupt counter
    epwm2Info.epwmTimerIntCount = 0;

    // Set base as ePWM2
    epwm2Info.epwmModule = myEPWM2_BASE;

    // Setup min/max CMPA/CMP values
    epwm2Info.epwmMaxCompA = EPWM2_MAX_CMPA;
    epwm2Info.epwmMinCompA = EPWM2_MIN_CMPA;
    epwm2Info.epwmMaxCompB = EPWM2_MAX_CMPB;
    epwm2Info.epwmMinCompB = EPWM2_MIN_CMPB;
}
//
// initEPWM3 - Initialize EPWM3 values
//
void initEPWM3(void)
{
    //
    // Setup TBCLK
    //
    EPWM_setTimeBaseCounterMode(myEPWM3_BASE, EPWM_COUNTER_MODE_UP);
    EPWM_setTimeBasePeriod(myEPWM3_BASE, EPWM3_TIMER_TBPRD);
    EPWM_disablePhaseShiftLoad(myEPWM3_BASE);
    EPWM_setPhaseShift(myEPWM3_BASE, 0U);
    EPWM_setTimeBaseCounter(myEPWM3_BASE, 0U);

    //
    // Set ePWM clock pre-scaler
    //
    EPWM_setClockPrescaler(myEPWM3_BASE,
                           EPWM_CLOCK_DIVIDER_1,
                           EPWM_HSCLOCK_DIVIDER_1);

    //
    // Setup shadow register load on ZERO
    //
    EPWM_setCounterCompareShadowLoadMode(myEPWM3_BASE,
                                         EPWM_COUNTER_COMPARE_A,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);
    EPWM_setCounterCompareShadowLoadMode(myEPWM3_BASE,
                                         EPWM_COUNTER_COMPARE_B,
                                         EPWM_COMP_LOAD_ON_CNTR_ZERO);

    //
    // Set Compare values
    //
    EPWM_setCounterCompareValue(myEPWM3_BASE, EPWM_COUNTER_COMPARE_A,
                                EPWM3_MIN_CMPA);
    EPWM_setCounterCompareValue(myEPWM3_BASE, EPWM_COUNTER_COMPARE_B,
                                EPWM3_MAX_CMPB);

    //
    // Set actions for ePWM1A & ePWM1B
    //
    // Set PWM3A on event B, up-count & clear on event B, up-count
    EPWM_setActionQualifierAction(myEPWM3_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_HIGH,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPA);
    EPWM_setActionQualifierAction(myEPWM3_BASE,
                                  EPWM_AQ_OUTPUT_A,
                                  EPWM_AQ_OUTPUT_LOW,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_UP_CMPB);

    // Toggle EPWM3B on counter = zero
    EPWM_setActionQualifierAction(myEPWM3_BASE,
                                  EPWM_AQ_OUTPUT_B,
                                  EPWM_AQ_OUTPUT_TOGGLE,
                                  EPWM_AQ_OUTPUT_ON_TIMEBASE_ZERO);

    //
    // Interrupt where we will change the Compare Values
    //
    EPWM_setInterruptSource(myEPWM3_BASE, EPWM_INT_TBCTR_ZERO);
    EPWM_enableInterrupt(myEPWM3_BASE);
    EPWM_setInterruptEventCount(myEPWM3_BASE, 3U);

   //
   // Information this example uses to keep track
   // of the direction the CMPA/CMPB values are
   // moving, the min and max allowed values and
   // a pointer to the correct ePWM registers
   //

    // Start by increasing CMPA & decreasing CMPB
    epwm3Info.epwmCompADirection = EPWM_CMP_UP;
    epwm3Info.epwmCompBDirection = EPWM_CMP_UP;

    // Start the count at 0
    epwm3Info.epwmTimerIntCount = 0;

    // Set base as ePWM1
    epwm3Info.epwmModule = myEPWM3_BASE;

    // Setup min/max CMPA/CMP values
    epwm3Info.epwmMaxCompA = EPWM3_MAX_CMPA;
    epwm3Info.epwmMinCompA = EPWM3_MIN_CMPA;
    epwm3Info.epwmMaxCompB = EPWM3_MAX_CMPB;
    epwm3Info.epwmMinCompB = EPWM3_MIN_CMPB;
}
//
// updateCompare - Update the compare values for the specified EPWM
//
void updateCompare(epwmInfo *epwm_info)
{
   //
   // Every 10'th interrupt, change the CMPA/CMPB values
   //
   if(epwm_info->epwmTimerIntCount == 10)
   {
       epwm_info->epwmTimerIntCount = 0;
       compAVal = EPWM_getCounterCompareValue(epwm_info->epwmModule,
                                              EPWM_COUNTER_COMPARE_A);
       compBVal = EPWM_getCounterCompareValue(epwm_info->epwmModule,
                                              EPWM_COUNTER_COMPARE_B);

       //
       // If we were increasing CMPA, check to see if
       // we reached the max value.  If not, increase CMPA
       // else, change directions and decrease CMPA
       //
       if(epwm_info->epwmCompADirection == EPWM_CMP_UP)
       {
           if(compAVal < epwm_info->epwmMaxCompA)
           {
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_A, ++compAVal);
           }
           else
           {
               epwm_info->epwmCompADirection = EPWM_CMP_DOWN;
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_A, --compAVal);
           }
       }

       //
       // If we were decreasing CMPA, check to see if
       // we reached the min value.  If not, decrease CMPA
       // else, change directions and increase CMPA
       //
       else
       {
           if(compAVal == epwm_info->epwmMinCompA)
           {
               epwm_info->epwmCompADirection = EPWM_CMP_UP;
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_A, ++compAVal);

           }
           else
           {
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_A, --compAVal);
           }
       }

       //
       // If we were increasing CMPB, check to see if
       // we reached the max value.  If not, increase CMPB
       // else, change directions and decrease CMPB
       //
       if(epwm_info->epwmCompBDirection == EPWM_CMP_UP)
       {
           if(compBVal < epwm_info->epwmMaxCompB)
           {
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_B, ++compBVal);
           }
           else
           {
               epwm_info->epwmCompBDirection = EPWM_CMP_DOWN;
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_B, --compBVal);

           }
       }

       //
       // If we were decreasing CMPB, check to see if
       // we reached the min value.  If not, decrease CMPB
       // else, change directions and increase CMPB
       //
       else
       {
           if(compBVal == epwm_info->epwmMinCompB)
           {
               epwm_info->epwmCompBDirection = EPWM_CMP_UP;
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_B, ++compBVal);
           }
           else
           {
               EPWM_setCounterCompareValue(epwm_info->epwmModule,
                                           EPWM_COUNTER_COMPARE_B, --compBVal);
           }
       }
   }

   //
   // Increment interrupt count if < 10
   //
   else
   {
      epwm_info->epwmTimerIntCount++;
   }
   return;
}
