
//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include <Autobot_UART_SCIA.h>
#include <Autobot_UART_SCIB.h>
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
#include <math.h>
//#include <Autobot_Timer.h>
//unsigned char rxString[100];

#define UP 1
#define DOWN 2

// Globals
//
volatile uint32_t XINT1Count;
volatile uint32_t XINT2Count;
volatile uint32_t loopCount;
//Position Control

int calculatePWM(float feedback_value_count_per_sec);
void voidPositionControl(unsigned char PositionInPercent);
char succesful_Msg="Successfull!";
volatile uint32_t i;
volatile uint32_t Example_PassCount1;

unsigned char LSUP_Flag=0;
#define DEBOUNCE_DELAY 100 // Adjust debounce
void main(void)
{
    uint16_t receivedChar;
    uint32_t tempX1Count;
    uint32_t tempX2Count;
    char*msg;
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
    Autobot_SCIB_init();
    Autobot_SCIA_init();
    Autobot_ADC_init();
    Autobot_EPWM_init();
    Autobot_MotorDriver_int();
    Autobot_Encoder_init();

    MotorDriver_setDirection(MOVE_UP);

    DEVICE_DELAY_US(10000);
    Interrupt_disable(INT_TIMER0);
    Interrupt_disable(INT_TIMER1);
    Interrupt_disable(INT_TIMER2);
    EINT;  // Enable Global interrupt INTM
    ERTM;  // Enable Global realtime interrupt DBGM

    // Send starting message.
    //
//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//    msg = "Welcome To Autobot Tensile Tester!";
//    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,32);
//    msg = "Command:(/PWM,00/,/POS,00/,/MOVE,UP/,/MOVE,DOWN/,/STOP/,/LVDT/,/CALIBRATE/,/RESETENCODER/,/START/)";
//    SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,70);
    SCI_TxString(SCIA_BASE,msg);
    char stress[6]={1,2,3,4,5,6};
    char strain[6]={1,2,3,4,5,6};

    unsigned char test = -1;
    char CountString[20];
    while(1)
    {
//        if(LSUP_Flag)
//        {
//            switch(LSUP_Flag)
//            {
//            case UP:
//
//                sprintf(CountString,"LSUP:%d",XINT2Count);
//                SCI_TxString(SCIA_BASE,CountString);
//                LSUP_Flag=0;
//                break;
//            case DOWN:
//                sprintf(CountString,"LSDOWN:%d",XINT1Count);
//                SCI_TxString(SCIA_BASE,CountString);
//                LSUP_Flag=0;
//                break;
//            }
//
//        }

//        voidPositionControl(Desired_Position);
        test=SCI_RxString(SCIA_BASE,rxString);
        if(test==0)
        {
            SCI_TxString(SCIA_BASE,"succesful_Msg");
            Autobot_Commands(rxString);
        }
    }



}
//
// sciaRXFIFOISR - SCIA Receive FIFO ISR
//
__interrupt void sciaRXFIFOISR(void)
{
//    uint16_t i;
//    unsigned char test = -1;
//    test=SCI_RxString(SCIA_BASE,rxString);
//    if(test==0)
//    {
//        SCI_TxString(SCIA_BASE,"succesful_Msg");
//        Autobot_Commands(rxString);
//    }

//                receivedChar = SCI_readCharBlockingFIFO(SCIA_BASE); // Read received character
                receivedChar = SCI_readCharBlockingNonFIFO(SCIA_BASE);
                if (receivedChar == '\r')
                { // Check if received character is '\r'
                    rxString[rxIndex] = '\0'; // Add null terminator to make it a string
                    rxIndex = 0; // Reset index for next reception'
                    Autobot_Commands(rxString);
                    memset(rxString, 0, sizeof(rxString)); // Set all elements to 0 ('\0')
                }
                else if (rxIndex < BUFF_SZ - 1) // checking if the buffer is full or not
                { // Check if buffer has space
                    rxString[rxIndex++] = receivedChar; // Store received character
                }

    SCI_clearOverflowStatus(SCIA_BASE);

    SCI_clearInterruptStatus(SCIA_BASE, SCI_INT_RXFF);

    //
    // Issue PIE ack
    //
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP9);

    Example_PassCount1++;
}
__interrupt void
cpuTimer0ISR(void)
{

//    // Inside your main loop or wherever PWM control is needed

//    char outputString[50];
//    sprintf(outputString, "%lld,", EncoderCount);
//    SCI_TxString(SCIA_BASE,outputString);


    //ADC Result
    //
    // Convert, wait for completion, and store results
    //
    ADC_forceMultipleSOC(ADCA_BASE, (ADC_FORCE_SOC0 | ADC_FORCE_SOC1));

    //
    // Wait for ADCA to complete, then acknowledge flag
    //
    while(ADC_getInterruptStatus(ADCA_BASE, ADC_INT_NUMBER1) == false)
    {
    }
    ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER1);

    //
    // Store results
    //
    adcAResult0 = ADC_readResult(ADCARESULT_BASE, ADC_SOC_NUMBER0);
    adcAResult1 = ADC_readResult(ADCARESULT_BASE, ADC_SOC_NUMBER1);


    //
    // Software breakpoint. At this point, conversion results are stored in
    // adcAResult0, adcAResult1, adcDResult0, and adcDResult1.
    //
    // Hit run again to get updated conversions.
    //
//    ESTOP0;

//
//          Interrupt_enable(INT_TIMER0);
//          Interrupt_enable(INT_TIMER1);
//          Interrupt_enable(INT_TIMER2);
//
    Sample_Strain[cpuTimer0IntCount]= EncoderCount;
    Sample_Stress[cpuTimer0IntCount]= adcAResult0;///Later will be ADC value FROM LVDT adcAResult0-adcAResult1
    cpuTimer0IntCount++;
    if(EncoderCount<0||EncoderCount>Total_Of_Count)
    {
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
        MotorDriver_stop();
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
    }
      Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);

}
// xint1_isr - External Interrupt 1 ISR
__interrupt void
cpuTimer1ISR(void)
{

    Sample_Speed[cpuTimer0IntCount] = EncoderCount-prevEncoderCountSpeed; //count/milisecond
    feedback_value_count_per_sec = EncoderCount-prevEncoderCountSpeed;
    int pwm = calculatePWM(feedback_value_count_per_sec);
    MotorDriver_setSpeed(pwm);
    if(EncoderCount<0||EncoderCount>Total_Of_Count)
    {
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
        MotorDriver_stop();
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
    }
//

//        if(cpuTimer1IntCount==0)
//        {
//    //                MotorDriver_setDirection(MOVE_DOWN);
//                    MotorDriver_setDirection(MOVE_UP);
//
//    //                DEVICE_DELAY_US(10000);
//                    EncoderCount=0;
//                    prevEncoderCountSpeed=0;
//            MotorDriver_setSpeed(100); //10 15 25 50 75 100
//
//        }
//        Sample_Speed[cpuTimer1IntCount] = EncoderCount;
        //speed caculation in 1 ms [COUNT/MILISECOND]
//        Sample_Speed[cpuTimer0IntCount] = EncoderCount-prevEncoderCountSpeed; //count/milisecond

//        feedback_value_count_per_sec = EncoderCount-prevEncoderCountSpeed;
//        int pwm = calculatePWM(feedback_value_count_per_sec);
//        MotorDriver_setSpeed(pwm);
//        if(cpuTimer1IntCount==200)
//        {
//            MotorDriver_setSpeed(0);
//            SCI_TxString(SCIA_BASE,"[");
//             int m=0;
//             char outputString[50];
//             for(m=0;m<200;m++)
//             {
//                 sprintf(outputString, "%lld,", Sample_Speed[m]);
//                 SCI_TxString(SCIA_BASE,outputString);
//             }
//
//             SCI_TxString(SCIA_BASE,"]");
//             cpuTimer1IntCount=600;
//        }
        cpuTimer1IntCount++;
        prevEncoderCountSpeed = EncoderCount;
//        //
//    //    // Acknowledge this interrupt to receive more interrupts from group 1
//        //
//
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
//    cpuTimer1IntCount++;
}
__interrupt void
cpuTimer2ISR(void)
{
    if(EncoderCount<0||EncoderCount>Total_Of_Count)
    {
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
        MotorDriver_stop();
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
    }

    SCI_TxString(SCIA_BASE,"A");
    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Stress[cpuTimer2IntCount])&0xFF));
    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Stress[cpuTimer2IntCount]>>8)&0xFF));
    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Stress[cpuTimer2IntCount]>>16)&0xFF));


    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Strain[cpuTimer2IntCount])&0xFF));
    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Strain[cpuTimer2IntCount]>>8)&0xFF));
    SCI_writeCharBlockingFIFO(SCIA_BASE,((Sample_Strain[cpuTimer2IntCount]>>16)&0xFF));


    cpuTimer2IntCount++;
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP1);
}

// Function to calculate PWM duty cycle using PI control
int calculatePWM(float feedback_value_count_per_sec)
{
    // Calculate error
    float error = setpoint_count_per_sec - feedback_value_count_per_sec;

    // Integral term calculation
    integral_term += error;

    // Proportional and integral control terms
    float proportional_term = Kp * error;
    float integral_control = Ki * integral_term;

    // Calculate PWM duty cycle
    float pwm = proportional_term + integral_control;

    // Update previous error
    previous_error = error;
    if (pwm > 100.0)
    {
        pwm = 100.0;
    }
    else if (pwm < 0.0)
    {
        pwm = 0;

    }

    return pwm;

}
void voidPositionControl(unsigned char PositionInPercent)
{
    // Convert position in percent to target count
    float target_count = (float)PositionInPercent / 100.0 * Total_Of_Count;//Total_Of_Count

    // Feedback mechanism to get current count (assuming it's stored in a global variable)
    float current_count = EncoderCount;

    // Calculate error
    float error = (float)target_count - (float)current_count;

    // Integral term calculation
    integral_term_Position += error;

    // Derivative term calculation
    float derivative_term = error - previous_error_Position;

    // Calculate control output
    float control_output = Kp_Position * error+Ki_Position * integral_term_Position+ Kd_Position * derivative_term;;//
    // Ensure PWM duty cycle is within bounds
    float pwm_duty_cycle=0;
    if (pwm_duty_cycle > 100)
    {
        pwm_duty_cycle = 100;
    } else if (pwm_duty_cycle < 0)
    {
        MotorDriver_setDirection(MOVE_DOWN);
       pwm_duty_cycle = 20;
    }
    pwm_duty_cycle = control_output;

    if (error > 0)
    {
        MotorDriver_setDirection(MOVE_UP);
    } else
    {
        MotorDriver_setDirection(MOVE_DOWN);
    }
    // Convert control output to PWM duty cycle


    // Apply PWM duty cycle to control the actuator
    MotorDriver_setSpeed(pwm_duty_cycle);

    // Update previous error
    previous_error_Position = error;
    // Set direction based on the error


}


interrupt void xint1_isr(void) //ENCODER_A
{
    unsigned char inputB = GPIO_readPin(59);
    if(encoderAPrevState==0)// Check for rising edge (low-to-high) of ENCODER_A
    {
        // Check the state of ENCODER_B
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
    unsigned char inputA = GPIO_readPin(58);
    if(encoderBPrevState==0)// Check for rising edge (low-to-high) of ENCODER_B
    {
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
//JUMP DOWN 2TIME AND JUM UP 1 TIME
interrupt void xint4_isr(void)////LIMIT SWITCH DOWN HIT AND STOP TO PROTECT SYSTEM
{
    Interrupt_disable(INT_TIMER0);
    Interrupt_disable(INT_TIMER1);
    Interrupt_disable(INT_TIMER2);
    MotorDriver_stop();


//    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//    XINT1Count++;
////
////    GPIO_setInterruptType(GPIO_INT_XINT4, GPIO_INT_TYPE_FALLING_EDGE);
////    SCI_TxString(SCIA_BASE,"D");
//    LSUP_Flag=2;
//    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag
    // Check debounce timer
//    if (GPIO_getData(GPIO_INT_XINT4) == 0 && (EPWM_getCounterValue(myEPWM1_BASE) != 0))
//    {
//        if (Timer_getPeriod(TIMER0_BASE) - Timer_getValue(TIMER0_BASE) > DEBOUNCE_DELAY)
//        {
//            MotorDriver_stop();
//            EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
//            XINT1Count++;
//        }
//    }
//    debounceTimer = Timer_getPeriod(TIMER0_BASE) - Timer_getValue(TIMER0_BASE);
//    Timer_setCount(TIMER0_BASE, 0); // Reset timer
//    GPIO_clearInterruptFlag(GPIO_INT_XINT4); // Clear interrupt flag
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12); // Clear interrupt flag
}

//
// xint2_isr - External Interrupt 2 ISR
//
interrupt void xint5_isr(void)////LIMIT SWITCH UP HIT AND STOP TO PROTECT SYSTEM
{
    Interrupt_disable(INT_TIMER0);
    Interrupt_disable(INT_TIMER1);
    Interrupt_disable(INT_TIMER2);

    MotorDriver_stop();
    EPWM_setCounterCompareValue(myEPWM1_BASE, EPWM_COUNTER_COMPARE_A, 0);
    XINT2Count++;
    LSUP_Flag=1;
//    GPIO_setInterruptType(GPIO_INT_XINT5, GPIO_INT_TYPE_FALLING_EDGE);
//    SCI_TxString(SCIA_BASE,"U");
    Interrupt_clearACKGroup(INTERRUPT_ACK_GROUP12);// Clear interrupt flag
}
//
// End of File
//





