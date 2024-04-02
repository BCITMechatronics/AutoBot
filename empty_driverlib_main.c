

#define RX_BUFFER_SIZE 100

char rxBuffer[RX_BUFFER_SIZE];

//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include <Autobot_UART_SCI.h>
#include <Autobot_ADC.h>
#include <board.h>
#include <Autobot_EPWM.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <stdbool.h>
#include <float.h>
#include <limits.h>
#include <Autobot_Timer.h>
#include <Autobot_MotorControl.h>
//#include "IQmathLib.h"
#include <Autobot_Command.h>
//#include <Autobot_EQEP.h>
unsigned char RxBuffer[100];
unsigned char rxString[100];
void main(void)
{
    uint16_t receivedChar;
    unsigned char *msg;
    unsigned char pwm_Control;

//
    Autobot_SCI_AInit();
    Autobot_ADC_init();
    Autobot_EPWM_init();
    Autobot_MotorDriver_int();

    GPIO_setPadConfig(7, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34   GPIO_PIN_TYPE_PULLUP
    GPIO_setPinConfig(GPIO_7_GPIO7);               // GPIO34 = GPIO34
    GPIO_setDirectionMode(7, GPIO_DIR_MODE_IN);     // GPIO34 = input
    GPIO_setPadConfig(6, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34  GPIO_PIN_TYPE_STD
    GPIO_setPinConfig(GPIO_6_GPIO6);               // GPIO34 = GPIO34
    GPIO_setDirectionMode(6, GPIO_DIR_MODE_IN);     // GPIO34 = input
//    unsigned char ADCvalue[50];

//    int  ADCResult=4096;
////
//    sprintf(ADCvalue, "Adc Value is %d", ADCResult);
//    SCI_TxString(SCIA_BASE,ADCvalue);
//    sprintf(ADCvalue, "Adc Value is %d", 4096);
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A,
//                                1000);

    //
    // Enable global Interrupts and higher priority real-time debug events:
    //
    EINT;  // Enable Global interrupt INTM
    ERTM;  // Enable Global realtime interrupt DBGM

    MotorDriver_setSpeed(40);
    MotorDriver_setDirection(MOVE_UP);
//    MotorDriver_setDirection(MOVE_DOWN);
//    MotorDriver_setSpeed(50);
//    MotorDriver_stop();
    // Send starting message.
    //
    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
    msg = "Welcome To Autobot Tensile Tester!";
    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,32);
    msg = "Command:(/speed,00/,/MOVE,UP/,/MOVE,DOWN/,/STOP/,/LVDT/,/EncoderSpeed/,/EncoderPosition/)";
    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,70);
    char stress[6]={1,2,3,4,5,6};
    char strain[6]={1,2,3,4,5,6};
    char Message[16] = {'A', stress[1], strain[1], stress[2], strain[2], stress[3], strain[3], stress[4], strain[4], stress[5], strain[5], 'E', 'N', 'D'};
    unsigned char test =-1;
    while(1)
    {

        test=SCI_RxString(SCIA_BASE,rxString);
        if(test==0)
        {
            Autobot_Commands(rxString);
        }

    }
//   while(1)
//   {
//       SCI_writeCharArray(SCIB_BASE, Message, 16);
//       DEVICE_DELAY_US(100000);
//   }
//
//    for(;;)
//    {
//        msg = "\r\nEnter a character: \0";
//        SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg, 22);
//
//        //
//        // Read a character from the FIFO.
//        //
//        receivedChar = SCI_readCharBlockingFIFO(SCIA_BASE);
//
////        rxStatus = SCI_getRxStatus(SCIA_BASE);
////        if((rxStatus & SCI_RXSTATUS_ERROR) != 0)
////        {
////            //
////            //If Execution stops here there is some error
////            //Analyze SCI_getRxStatus() API return value
////            //
////            ESTOP0;
////        }
//
//        //
//        // Echo back the character.
//        //
//        msg = "  You sent: \0";
//        SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg, 13);
//        SCI_writeCharBlockingFIFO(SCIA_BASE, receivedChar);
//
//        //
//        // Increment the loop count variable.
//        //
//        loopCounter++;
//    }

//     Take conversions indefinitely in loop

//    do
//    {
//        //
//        // Enable ADC interrupts
//        //
//        ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER1);
//        ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER2);
//        ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER3);
//        ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER4);
//
//        //
//        // Clear all interrupts flags(INT1-4)
//        //
//        HWREGH(ADCA_BASE + ADC_O_INTFLGCLR) = 0x000F;
//
//        //
//        // Initialize results index
//        //
//        resultsIndex = 0;
//
//        //
//        // Software force start SOC0 to SOC7
//        //
//        HWREGH(ADCA_BASE + ADC_O_SOCFRC1) = 0x00FF;
//
//        //
//        // Keep taking samples until the results buffer is full
//        //
//        while(resultsIndex < RESULTS_BUFFER_SIZE)
//        {
//            //
//            // Wait for first set of 8 conversions to complete
//            //
//            while(false == ADC_getInterruptStatus(ADCA_BASE, ADC_INT_NUMBER3));
//
//            //
//            // Clear the interrupt flag
//            //
//            ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER3);
//
//            //
//            // Save results for first 8 conversions
//            //
//            // Note that during this time, the second 8 conversions have
//            // already been triggered by EOC6->ADCIN1 and will be actively
//            // converting while first 8 results are being saved
//            //
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER0);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER1);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER2);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER3);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER4);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER5);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER6);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER7);
//
//            //
//            // Wait for the second set of 8 conversions to complete
//            //
//            while(false == ADC_getInterruptStatus(ADCA_BASE, ADC_INT_NUMBER4));
//
//            //
//            // Clear the interrupt flag
//            //
//            ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER4);
//
//            //
//            // Save results for second 8 conversions
//            //
//            // Note that during this time, the first 8 conversions have
//            // already been triggered by EOC14->ADCIN2 and will be actively
//            // converting while second 8 results are being saved
//            //
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER8);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER9);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER10);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER11);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER12);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER13);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER14);
//            adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
//                                                         ADC_SOC_NUMBER15);
//
//
//
//
//        }
//
//        //
//        // Disable all ADCINT flags to stop sampling
//        //
//        ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER1);
//        ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER2);
//        ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER3);
//        ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER4);
//
//        //
//        // At this point, adcAResults[] contains a sequence of conversions
//        // from the selected channel
//        //
//
//
//        //
//        // Software breakpoint, hit run again to get updated conversions
//        //
//        asm("   ESTOP0");
//    }
//    while(1); // Loop forever
}

//
// End of File
//








