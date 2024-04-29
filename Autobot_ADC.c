/*
 * Autobot_ADC.c
 *
 *  Created on: Feb 25, 2024
 *      Author: haduy
 */

// Included Files
//
#include "driverlib.h"
#include "device.h"
#include <Autobot_ADC.h>

//// Globals
////
//uint16_t adcAResult0;
//uint16_t adcAResult1;
uint16_t adcDResult0;
uint16_t adcDResult1;
uint16_t resultsIndex;
uint16_t loopCounter;
int16_t adcAResult0;
int16_t adcAResult1;

void Autobot_ADC_init()
{
    // Initialize device clock and peripherals
     //
     Device_init();

     //
     // Disable pin locks and enable internal pullups.
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
      // Configure the ADC and power it up
      //
     //
     // Set ADCDLK divider to /4
     //
     ADC_setPrescaler(ADCA_BASE, ADC_CLK_DIV_4_0);
     ADC_setPrescaler(ADCD_BASE, ADC_CLK_DIV_4_0);

     //
     // Set resolution and signal mode (see #defines above) and load
     // corresponding trims.
     //
 #if(EX_ADC_RESOLUTION == 12)
     ADC_setMode(ADCA_BASE, ADC_RESOLUTION_12BIT, ADC_MODE_SINGLE_ENDED);
     ADC_setMode(ADCD_BASE, ADC_RESOLUTION_12BIT, ADC_MODE_SINGLE_ENDED);
 #elif(EX_ADC_RESOLUTION == 16)
     ADC_setMode(ADCA_BASE, ADC_RESOLUTION_16BIT, ADC_MODE_DIFFERENTIAL);
     ADC_setMode(ADCD_BASE, ADC_RESOLUTION_16BIT, ADC_MODE_DIFFERENTIAL);
 #endif

     //
     // Set pulse positions to late
     //
     ADC_setInterruptPulseMode(ADCA_BASE, ADC_PULSE_END_OF_CONV);
     ADC_setInterruptPulseMode(ADCD_BASE, ADC_PULSE_END_OF_CONV);

     //
     // Power up the ADCs and then delay for 1 ms
     //
     ADC_enableConverter(ADCA_BASE);
     ADC_enableConverter(ADCD_BASE);

     DEVICE_DELAY_US(1000);
     //
     // Configure SOCs of ADCA
     // - SOC0 will convert pin A0.
     // - SOC1 will convert pin A1.
     // - Both will be triggered by software only.
     // - For 12-bit resolution, a sampling window of 15 (75 ns at a 200MHz
     //   SYSCLK rate) will be used.  For 16-bit resolution, a sampling window
     //   of 64 (320 ns at a 200MHz SYSCLK rate) will be used.
     // - NOTE: A longer sampling window will be required if the ADC driving
     //   source is less than ideal (an ideal source would be a high bandwidth
     //   op-amp with a small series resistance). See TI application report
     //   SPRACT6 for guidance on ADC driver design.
     //

 #if(EX_ADC_RESOLUTION == 12)
     ADC_setupSOC(ADCA_BASE, ADC_SOC_NUMBER0, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN0, 15);
     ADC_setupSOC(ADCA_BASE, ADC_SOC_NUMBER1, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN1, 15);
 #elif(EX_ADC_RESOLUTION == 16)
     ADC_setupSOC(ADCA_BASE, ADC_SOC_NUMBER0, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN0, 64);
     ADC_setupSOC(ADCA_BASE, ADC_SOC_NUMBER1, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN1, 64);
 #endif

     //
     // Set SOC1 to set the interrupt 1 flag. Enable the interrupt and make
     // sure its flag is cleared.
     //
     ADC_setInterruptSource(ADCA_BASE, ADC_INT_NUMBER1, ADC_SOC_NUMBER1);
     ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER1);
     ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER1);

     //
     // Configure SOCs of ADCD
     // - SOC0 will convert pin D2.
     // - SOC1 will convert pin D3.
     // - Both will be triggered by software only.
     // - For 12-bit resolution, a sampling window of 15 (75 ns at a 200MHz
     //   SYSCLK rate) will be used.  For 16-bit resolution, a sampling window
     //   of 64 (320 ns at a 200MHz SYSCLK rate) will be used.
     // - NOTE: A longer sampling window will be required if the ADC driving
     //   source is less than ideal (an ideal source would be a high bandwidth
     //   op-amp with a small series resistance). See TI application report
     //   SPRACT6 for guidance on ADC driver design.
     //

 #if(EX_ADC_RESOLUTION == 12)
     ADC_setupSOC(ADCD_BASE, ADC_SOC_NUMBER0, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN2, 15);
     ADC_setupSOC(ADCD_BASE, ADC_SOC_NUMBER1, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN3, 15);
 #elif(EX_ADC_RESOLUTION == 16)
     ADC_setupSOC(ADCD_BASE, ADC_SOC_NUMBER0, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN2, 64);
     ADC_setupSOC(ADCD_BASE, ADC_SOC_NUMBER1, ADC_TRIGGER_SW_ONLY,
                  ADC_CH_ADCIN3, 64);
 #endif

     //
     // Set SOC1 to set the interrupt 1 flag. Enable the interrupt and make
     // sure its flag is cleared.
     //
     ADC_setInterruptSource(ADCD_BASE, ADC_INT_NUMBER1, ADC_SOC_NUMBER1);
     ADC_enableInterrupt(ADCD_BASE, ADC_INT_NUMBER1);
     ADC_clearInterruptStatus(ADCD_BASE, ADC_INT_NUMBER1);

}

void configureADC(uint32_t adcBase)
{
    //
    // Set ADCDLK divider to /4
    //
    ADC_setPrescaler(adcBase, ADC_CLK_DIV_4_0);

    //
    // Set resolution and signal mode (see #defines above) and load
    // corresponding trims.
    //
//#if(EX_ADC_RESOLUTION == 12)
//    ADC_setMode(adcBase, ADC_RESOLUTION_12BIT, ADC_MODE_SINGLE_ENDED);
//#elif(EX_ADC_RESOLUTION == 16)
//    ADC_setMode(adcBase, ADC_RESOLUTION_16BIT, ADC_MODE_DIFFERENTIAL);//FIX
//#endif
#if(EX_ADC_RESOLUTION == 12)
    ADC_setMode(adcBase, ADC_RESOLUTION_12BIT, ADC_MODE_SINGLE_ENDED);
#elif(EX_ADC_RESOLUTION == 16)
    ADC_setMode(adcBase, ADC_RESOLUTION_16BIT, ADC_MODE_DIFFERENTIAL);
#endif

    //
    // Set pulse positions to late
    //
    ADC_setInterruptPulseMode(adcBase, ADC_PULSE_END_OF_CONV);

    //
    // Power up the ADCs and then delay for 1 ms
    //
    ADC_enableConverter(adcBase);

    //
    // Delay for 1ms to allow ADC time to power up
    //
    DEVICE_DELAY_US(1000);
}

//
// setupADCContinuous - setup the ADC to continuously convert on one channel
//
void setupADCContinuous(uint32_t adcBase, uint32_t channel)
{
    uint16_t acqps;

    //
    // Determine acquisition window (in SYSCLKS) based on resolution
    //
    if(EX_ADC_RESOLUTION == 12)
    {
        acqps = 30; // 150ns
    }
    else //resolution is 16-bit
    {
        acqps = 64; // 320ns
    }
    //
    // - NOTE: A longer sampling window will be required if the ADC driving
    //   source is less than ideal (an ideal source would be a high bandwidth
    //   op-amp with a small series resistance). See TI application report
    //   SPRACT6 for guidance on ADC driver design.
    // - NOTE: A slightly longer S+H window is used with 12-bit resolution to
    //   ensure the data collection loop can keep up with the ADC
    //

    //
    // Configure SOCs channel no. & acquisition window.
    //
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER0, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER1, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER2, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER3, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER4, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER5, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER6, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER7, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER8, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER9, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER10, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER11, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER12, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER13, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER14, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);
    ADC_setupSOC(adcBase, ADC_SOC_NUMBER15, ADC_TRIGGER_SW_ONLY,
                 (ADC_Channel)channel, acqps);

    //
    // Setup interrupt trigger for SOCs. ADCINT2 will trigger first 8 SOCs.
    // ADCINT1 will trigger next 8 SOCs
    //

    //
    // ADCINT2 trigger for SOC0-SOC7
    //
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER0,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER1,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER2,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER3,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER4,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER5,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER6,
                               ADC_INT_SOC_TRIGGER_ADCINT2);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER7,
                               ADC_INT_SOC_TRIGGER_ADCINT2);

    //
    // ADCINT1 trigger for SOC8-SOC15
    //
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER8,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER9,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER10,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER11,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER12,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER13,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER14,
                               ADC_INT_SOC_TRIGGER_ADCINT1);
    ADC_setInterruptSOCTrigger(adcBase, ADC_SOC_NUMBER15,
                               ADC_INT_SOC_TRIGGER_ADCINT1);

    //
    // Disable Interrupt flags
    //
    ADC_disableInterrupt(adcBase, ADC_INT_NUMBER1);
    ADC_disableInterrupt(adcBase, ADC_INT_NUMBER2);
    ADC_disableInterrupt(adcBase, ADC_INT_NUMBER3);
    ADC_disableInterrupt(adcBase, ADC_INT_NUMBER4);

    //
    // Enable continuous mode
    //
    ADC_enableContinuousMode(adcBase, ADC_INT_NUMBER1);
    ADC_enableContinuousMode(adcBase, ADC_INT_NUMBER2);
    ADC_enableContinuousMode(adcBase, ADC_INT_NUMBER3);
    ADC_enableContinuousMode(adcBase, ADC_INT_NUMBER4);

    //
    // Configure interrupt triggers
    //
    ADC_setInterruptSource(adcBase, ADC_INT_NUMBER1, ADC_SOC_NUMBER6);
    ADC_setInterruptSource(adcBase, ADC_INT_NUMBER2, ADC_SOC_NUMBER14);
    ADC_setInterruptSource(adcBase, ADC_INT_NUMBER3, ADC_SOC_NUMBER7);
    ADC_setInterruptSource(adcBase, ADC_INT_NUMBER4, ADC_SOC_NUMBER15);
}

//
// End of file
//
