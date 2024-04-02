/*
 * Autobot_Command.c
 *
 *  Created on: Mar 8, 2024
 *      Author: haduy
 */

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
#include <Autobot_Command.h>

const char *seps = ", \t\n";
msg = "Command:(/speed,00/,/MOVE,UP/,/MOVE,DOWN/,/STOP/,/LVDT/,/EncoderSpeed/,/EncoderPosition/)";
void Autobot_Commands(char* command)
{
    char* token = NULL, * nextTok = NULL;              // for tokenizing the line string

    //Break String
    token = strtok(command, seps);             // break first time to check command name
    if (token == NULL)
    {
        return -1; //  Nothing To Read
    }
    if (strcmp(token, "speed") == 0)
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

    else if (strcmp(token, "STOP") == 0)
    {
        MotorDriver_stop();
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
    else if (strcmp(token, "EncoderSpeed") == 0)
    {

    }
    else if (strcmp(token, "LS") == 0)
    {
        GPIO_setPadConfig(7, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34   GPIO_PIN_TYPE_PULLUP
        GPIO_setPinConfig(GPIO_7_GPIO7);               // GPIO34 = GPIO34
        GPIO_setDirectionMode(7, GPIO_DIR_MODE_IN);     // GPIO34 = input
        GPIO_setPadConfig(6, GPIO_PIN_TYPE_PULLUP);     // Enable pullup on GPIO34  GPIO_PIN_TYPE_STD
        GPIO_setPinConfig(GPIO_6_GPIO6);               // GPIO34 = GPIO34
        GPIO_setDirectionMode(6, GPIO_DIR_MODE_IN);     // GPIO34 = input
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
    // Enable ADC interrupts
    //
    ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER1);
    ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER2);
    ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER3);
    ADC_enableInterrupt(ADCA_BASE, ADC_INT_NUMBER4);

    //
    // Clear all interrupts flags(INT1-4)
    //
    HWREGH(ADCA_BASE + ADC_O_INTFLGCLR) = 0x000F;

    //
    // Initialize results index
    //
    resultsIndex = 0;

    //
    // Software force start SOC0 to SOC7
    //
    HWREGH(ADCA_BASE + ADC_O_SOCFRC1) = 0x00FF;

    //
    // Keep taking samples until the results buffer is full
    //
    while(resultsIndex < RESULTS_BUFFER_SIZE)
    {
        //
        // Wait for first set of 8 conversions to complete
        //
        while(false == ADC_getInterruptStatus(ADCA_BASE, ADC_INT_NUMBER3));

        //
        // Clear the interrupt flag
        //
        ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER3);

        //
        // Save results for first 8 conversions
        //
        // Note that during this time, the second 8 conversions have
        // already been triggered by EOC6->ADCIN1 and will be actively
        // converting while first 8 results are being saved
        //
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER0);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER1);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER2);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER3);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER4);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER5);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER6);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER7);
        //
        // Wait for the second set of 8 conversions to complete
        //
        while(false == ADC_getInterruptStatus(ADCA_BASE, ADC_INT_NUMBER4));

        //
        // Clear the interrupt flag
        //
        ADC_clearInterruptStatus(ADCA_BASE, ADC_INT_NUMBER4);
        //
        // Save results for second 8 conversions
        //
        // Note that during this time, the first 8 conversions have
        // already been triggered by EOC14->ADCIN2 and will be actively
        // converting while second 8 results are being saved
        //
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER8);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER9);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER10);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER11);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER12);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER13);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER14);
        adcAResults[resultsIndex++] = ADC_readResult(ADCARESULT_BASE,
                                                     ADC_SOC_NUMBER15);

    }

    //
    // Disable all ADCINT flags to stop sampling
    //
    ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER1);
    ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER2);
    ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER3);
    ADC_disableInterrupt(ADCA_BASE, ADC_INT_NUMBER4);


//     At this point, adcAResults[] contains a sequence of conversions
//     from the selected channel

        unsigned char ADCvalue[50];
        unsigned char countADC=0;
        while(countADC < RESULTS_BUFFER_SIZE)
        {
            sprintf(ADCvalue, "LVDT Val %u: %u",countADC, adcAResults[countADC]);
            countADC++;
            SCI_TxString(SCIA_BASE,ADCvalue);
        }

}
