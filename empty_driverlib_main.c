

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
#include <stdint.h>
#include <Autobot_MotorControl.h>
#include <Autobot_Command.h>
#include <Autobot_Encoder.h>

//#include <Autobot_Timer.h>
unsigned char rxString[100];


// Globals
//
volatile uint32_t XINT1Count;
volatile uint32_t XINT2Count;
volatile uint32_t loopCount;



volatile uint32_t i;
void main(void)
{
    uint16_t receivedChar;
    unsigned char *msg;
    unsigned char pwm_Control;
    uint32_t tempX1Count;
    uint32_t tempX2Count;
    Device_init();

    //
    // Configures the GPIO pin as a push-pull output
    //
    Device_initGPIO();
//
    // Initializes PIE and clears PIE registers. Disables CPU interrupts.
    //
    Interrupt_initModule();

    //
    // Initializes the PIE vector table with pointers to the shell Interrupt
    // Service Routines (ISR).
    //
    Interrupt_initVectorTable();
    Board_init();

    Autobot_SCI_AInit();
//    Autobot_ADC_init();
    Autobot_EPWM_init();
    Autobot_MotorDriver_int();


    Autobot_Encoder_init();


    EINT;  // Enable Global interrupt INTM
    ERTM;  // Enable Global realtime interrupt DBGM

//    MotorDriver_setSpeed(40);
    MotorDriver_setDirection(MOVE_UP);
//    MotorDriver_setDirection(MOVE_DOWN);
//    MotorDriver_setSpeed(50);
//    MotorDriver_stop();
    // Send starting message.
    //
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//    msg = "Welcome To Autobot Tensile Tester!";
//    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,32);
//    msg = "Command:(/speed,00/,/MOVE,UP/,/MOVE,DOWN/,/STOP/,/LVDT/,/EncoderSpeed/,/EncoderPosition/)";
////    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,70);
//    SCI_TxString(SCIA_BASE,msg);
//    char stress[6]={1,2,3,4,5,6};
//    char strain[6]={1,2,3,4,5,6};
//    char Message[16] = {'A', stress[1], strain[1], stress[2], strain[2], stress[3], strain[3], stress[4], strain[4], stress[5], strain[5], 'E', 'N', 'D'};
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

}
__interrupt void
cpuTimer0ISR(void)
{
    if(cpuTimer0IntCount==0)
    {
        //        MotorDriver_setDirection(MOVE_DOWN);
                MotorDriver_setDirection(MOVE_UP);
                EncoderCount=0;
                prevEncoderCountSpeed=0;
        MotorDriver_setSpeed(100); //10 15 25 50 75 100

    }

    //speed caculation in 1 ms [COUNT/MILISECOND]
    Sample_Speed[cpuTimer0IntCount] = EncoderCount-prevEncoderCountSpeed; //count/milisecond
    if(cpuTimer0IntCount==500)
    {
        char StringHead[10]="[";
        SCI_TxString(SCIA_BASE,StringHead);

         int m=0;
         MotorDriver_setSpeed(0);

         for(m=0;m<500;m++)
         {
             char outputString[50];
             sprintf(outputString, "%lld,", Sample_Speed[m]);
             SCI_TxString(SCIA_BASE,outputString);
//             SCI_writeCharArray(SCIA_BASE, outputString,2);
         }


         char StringTail[10]="]";
         SCI_TxString(SCIA_BASE,StringTail);
         cpuTimer0IntCount=600;
//        SCI_writeCharArray(SCIA_BASE, outputString,500);
//        SCI_TxString(SCIA_BASE,outputString);
    }
    cpuTimer0IntCount++;
    prevEncoderCountSpeed = EncoderCount;
    //
    // Acknowledge this interrupt to receive more interrupts from group 1
    //
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
}
// xint1_isr - External Interrupt 1 ISR

interrupt void xint1_isr(void) //ENCODER_A
{
    unsigned char inputB = GPIO_readPin(18);
    if(encoderAPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
    {
        // Check the state of ENCODER_B
//        unsigned char inputB = GPIO_readPin(18);
        if (inputB==1)
        {
            EncoderCount++;
        }
        else if(inputB==0)
        {
            EncoderCount--;
        }


    }
    else if(encoderAPrevState==1) // Falling edge (high-to-low) of ENCODER_A
    {
        // Check the state of ENCODER_B
//        unsigned char inputB = GPIO_readPin(18);
        if (inputB==1)
        {
            EncoderCount--;
        }
        else if(inputB==0)
        {
            EncoderCount++;
        }

    }
    if(encoderAPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
    {
        encoderAPrevState=1;// Toggle interrupt edge for ENCODER_A
        GPIO_setInterruptType(GPIO_INT_XINT1, GPIO_INT_TYPE_FALLING_EDGE );// Toggle interrupt edge for ENCODER_A
    }
    else if (encoderAPrevState==1)
    {
        encoderAPrevState=0;// Toggle interrupt edge for ENCODER_A
        GPIO_setInterruptType(GPIO_INT_XINT1, GPIO_INT_TYPE_RISING_EDGE );// Toggle interrupt edge for ENCODER_A
    }
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);// Clear interrupt flag for ENCODER_A
}
//
// xint2_isr - External Interrupt 2 ISR
//
interrupt void xint2_isr(void)  //ENCODER_B
{
    unsigned char inputA = GPIO_readPin(19);
    if(encoderBPrevState==0)// Check for rising edge (low-to-high) of ENCODER_B
    {
//        unsigned char inputA = GPIO_readPin(19);
        if (inputA==1)
        {
            EncoderCount--;
        }
        else if(inputA==0)
        {
            EncoderCount++;
        }


    }
    else if(encoderBPrevState==1)// Falling edge (high-to-low) of ENCODER_B
    {
//        unsigned char inputA = GPIO_readPin(19);
        if (inputA==1)
        {
            EncoderCount++;
        }
        else if(inputA==0)
        {
            EncoderCount--;
        }


    }
    if(encoderBPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
    {
        encoderBPrevState=1;// Toggle interrupt edge for ENCODER_B
        GPIO_setInterruptType(GPIO_INT_XINT2,GPIO_INT_TYPE_FALLING_EDGE );// Toggle interrupt edge for ENCODER_B
    }
    else if(encoderBPrevState==1)
    {
        encoderBPrevState=0;// Toggle interrupt edge for ENCODER_B
        GPIO_setInterruptType(GPIO_INT_XINT2, GPIO_INT_TYPE_RISING_EDGE);// Toggle interrupt edge for ENCODER_B
    }
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);// Clear interrupt flag for ENCODER_A
}

interrupt void xint3_isr(void)
{
//    DeltaCount[indexCount] = EncoderCount-prevEncoderCount;
//    indexCount++;
//    prevEncoderCount = EncoderCount;
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag for ENCODER_A
}
interrupt void xint4_isr(void)
{
//    MotorDriver_stop();
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//    MotorDriver_setDirection(MOVE_UP);
//    XINT1Count++;
//
////    //
////    // Acknowledge this interrupt to get more from group 1
////    //
////    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
//    GPIO_setInterruptType(GPIO_INT_XINT4, GPIO_INT_TYPE_FALLING_EDGE);
//
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag for ENCODER_A

}

//
// xint2_isr - External Interrupt 2 ISR
//
interrupt void xint5_isr(void)
{
//    MotorDriver_stop();
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//    MotorDriver_setDirection(MOVE_DOWN);
//    XINT2Count++;
//
//    //
//    // Acknowledge this interrupt to get more from group 1
//    //
////    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
//    // // Falling edge interrupt
//    GPIO_setInterruptType(GPIO_INT_XINT5, GPIO_INT_TYPE_FALLING_EDGE);
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag for ENCODER_A
}
//
// End of File
//





