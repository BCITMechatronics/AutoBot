/*
 * Autobot_Command.c
 *
 *  Created on: Mar 8, 2024
 *      Author: haduy
 */

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
#include <Autobot_Encoder.h>
#include <Autobot_MotorControl.h>
#include <Autobot_Command.h>

const char *seps = ", \t\n";
msg = "Command:(/START/,/PWM,00/,/MOVE,UP/,/MOVE,DOWN/,/STOP/,/LVDT/,/POS,00/)";
void Autobot_Commands(char* command)
{
    char* token = NULL, * nextTok = NULL;              // for tokenizing the line string

    //Break String
    token = strtok(command, seps);             // break first time to check command name
    if (token == NULL)
    {
        return -1; //  Nothing To Read
    }
    if (strcmp(token, "PWM") == 0)
    {
        unsigned char SpeedInPercent=0;
        //Break 2nd to get string
        token = strtok(NULL,seps);//break second time to get state
        if (token == NULL)
        {
            return -1; // Invalid
        }
        SpeedInPercent =atoi(token);
        MotorDriver_setSpeed(SpeedInPercent);
    }
    else if (strcmp(token, "START") == 0)
    {
        MotorDriver_setDirection(MOVE_UP);
        setpoint_count_per_sec=440;
        cpuTimer2IntCount=0;

        Interrupt_enable(INT_TIMER2);
        Interrupt_enable(INT_TIMER1);
        Interrupt_enable(INT_TIMER0);


    }
    else if (strcmp(token, "RESETENCODER") == 0)
    {
        EncoderCount=0;
    }
    else if (strcmp(token, "STOP") == 0)
    {
        Interrupt_disable(INT_TIMER0);
        Interrupt_disable(INT_TIMER1);
        Interrupt_disable(INT_TIMER2);
        MotorDriver_stop();
//        SCI_TxString(SCIA_BASE,"B");
    }
    // Check if the command is to get vector data from PixyCam
    else if (strcmp(token, "MOVE") == 0)
    {
        //Break 2nd to get continuous
        token = strtok(NULL,seps);//break second time to get state
        if (token == NULL)
        {
            return -1; // Invalid
        }
        if (strcmp(token, "UP") == 0)
        {
            MotorDriver_setDirection(MOVE_UP);
        }
        else if (strcmp(token, "DOWN") == 0)
        {
            MotorDriver_setDirection(MOVE_DOWN);
        }
    }
    else if (strcmp(token, "LVDT") == 0)
    {
        get_LVDT();
    }
    else if (strcmp(token, "CALIBRATE") == 0)
    {

        Calibrate();
        DEVICE_DELAY_US(1000000);
        SCI_TxString(SCIA_BASE,"E");
//        SCI_writeCharBlockingFIFO(SCIA_BASE,0x45);
        SCI_writeCharBlockingFIFO(SCIA_BASE,((Total_Of_Count)&0xFF));
        SCI_writeCharBlockingFIFO(SCIA_BASE,((Total_Of_Count>>8)&0xFF));
        SCI_writeCharBlockingFIFO(SCIA_BASE,((Total_Of_Count>>16)&0xFF));




    }
    else if (strcmp(token, "POS") == 0)
    {
        //Break 2nd to get string
        token = strtok(NULL,seps);//break second time to get state
        if (token == NULL)
        {
            return -1; // Invalid
        }
        Desired_Position =atoi(token);

        while(1)
        {
            voidPositionControl(Desired_Position);
            long long int Desired_EncoderCount=(Desired_Position*Total_Of_Count)/100;
             if ((EncoderCount>(Desired_EncoderCount-1000))&(EncoderCount<(Desired_EncoderCount+1000)))
             {

                 Interrupt_disable(INT_TIMER0);
                 MotorDriver_stop();
                 break;
             }
        }

    }
    else if (strcmp(token, "LS") == 0)
    {
//        GPIO_setPadConfig(7, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34   GPIO_PIN_TYPE_PULLUP
//        GPIO_setPinConfig(GPIO_7_GPIO7);               // GPIO34 = GPIO34
//        GPIO_setDirectionMode(7, GPIO_DIR_MODE_IN);     // GPIO34 = input
//        GPIO_setPadConfig(6, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34  GPIO_PIN_TYPE_STD
//        GPIO_setPinConfig(GPIO_6_GPIO6);               // GPIO34 = GPIO34
//        GPIO_setDirectionMode(6, GPIO_DIR_MODE_IN);     // GPIO34 = input
        //INTPUT PULLDOWN
        unsigned char LScheckUp=-1,LScheckDown=-1;
//Not pull =1 when it hitt =0 for both UP and Down LS
        unsigned char *msg;
        while(1)//LScheckUp==0 || LScheckDown==0LScheckUp==0 || LScheckDown==0
        {

            LScheckUp =GPIO_readPin(7);
            LScheckDown =GPIO_readPin(6);
            if(LScheckUp==0)
            {
                  msg = "Limit Swith UP it hitted!";
                  SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,25);
                  MotorDriver_stop();
                  MotorDriver_setDirection(MOVE_DOWN);
            }
            if(LScheckDown==0)
            {
                  msg = "Limit Swith Down it hitted!";
                  SCI_writeCharArray(SCIA_BASE, (uint16_t*)msg,25);
                  MotorDriver_stop();
                  MotorDriver_setDirection(MOVE_UP);
            }
        }
    }
    else
    {
        // Error message for unknown command
        return -1;
    }
}
void get_LVDT()
{
//
//        unsigned char ADCvalue[50];
//        unsigned char countADC=0;
//        while(countADC < RESULTS_BUFFER_SIZE)
//        {
//            sprintf(ADCvalue, "LVDT Val %u: %u",countADC, adcAResults[countADC]);
//            countADC++;
//            SCI_TxString(SCIA_BASE,ADCvalue);
//        }

}
