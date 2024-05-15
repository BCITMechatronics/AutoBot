/*************************************************************************************************
 * UART_SCI.c
 * - C implementation or source file for MSP430 UCSI UART A1
 *
 *  Author: Ace
 *  Created on: March 1, 2017
 *  Date: Feburary 30, 2024
 **************************************************************************************************/


#include <Autobot_UART_SCIB.h>
#include "driverlib.h"
#include "device.h"

//
// Defines
//
// Define AUTOBAUD to use the autobaud lock feature
//#define AUTOBAUD



/************************************************************************************
* Function: SCIAInit

************************************************************************************/
void Autobot_SCIB_init()
{
//    //
//    // Configure PLL, disable WD, enable peripheral clocks.
//    //
    Device_init();

    //
    // Disable pin locks and enable internal pullups.
    //
    Device_initGPIO();

//    //
//    // Configuration for the SCI Rx pin.
    //
//    GPIO_setMasterCore(DEVICE_GPIO_PIN_SCIRXDA, GPIO_CORE_CPU1);
//    GPIO_setPinConfig(DEVICE_GPIO_CFG_SCIRXDA);
//    GPIO_setDirectionMode(DEVICE_GPIO_PIN_SCIRXDA, GPIO_DIR_MODE_IN);
//    GPIO_setPadConfig(DEVICE_GPIO_PIN_SCIRXDA, GPIO_PIN_TYPE_STD);
//    GPIO_setQualificationMode(DEVICE_GPIO_PIN_SCIRXDA, GPIO_QUAL_ASYNC);
//    //
//    // Configuration for the SCI Tx pin.
//    //
//    GPIO_setMasterCore(DEVICE_GPIO_PIN_SCITXDA, GPIO_CORE_CPU1);
//    GPIO_setPinConfig(DEVICE_GPIO_CFG_SCITXDA);
//    GPIO_setDirectionMode(DEVICE_GPIO_PIN_SCITXDA, GPIO_DIR_MODE_OUT);
//    GPIO_setPadConfig(DEVICE_GPIO_PIN_SCITXDA, GPIO_PIN_TYPE_STD);
//    GPIO_setQualificationMode(DEVICE_GPIO_PIN_SCITXDA, GPIO_QUAL_ASYNC);


    //
    // SCI for USB-to-UART adapter on FTDI chip
    //
//    #define DEVICE_GPIO_PIN_SCIRXDA     43U             // GPIO number for SCI RX
//    #define DEVICE_GPIO_PIN_SCITXDA     42U             // GPIO number for SCI TX
//    #define DEVICE_GPIO_CFG_SCIRXDA     GPIO_43_SCIRXDA // "pinConfig" for SCI RX
//    #define DEVICE_GPIO_CFG_SCITXDA     GPIO_42_SCITXDA // "pinConfig" for SCI TX
//    #else
//    #define DEVICE_GPIO_PIN_SCIRXDA     28U             // GPIO number for SCI RX
//    #define DEVICE_GPIO_PIN_SCITXDA     29U             // GPIO number for SCI TX
//    #define DEVICE_GPIO_CFG_SCIRXDA     GPIO_28_SCIRXDA // "pinConfig" for SCI RX
//    #define DEVICE_GPIO_CFG_SCITXDA     GPIO_29_SCITXDA // "pinConfig" for SCI TX
    //
    // Configuration for the SCI Rx pin.
    //
//    GPIO_setMasterCore(28U, GPIO_CORE_CPU1);
//    GPIO_setPinConfig(GPIO_28_SCIRXDA);
//    GPIO_setDirectionMode(28U, GPIO_DIR_MODE_IN);
//    GPIO_setPadConfig(28U, GPIO_PIN_TYPE_STD);
//    GPIO_setQualificationMode(28U, GPIO_QUAL_ASYNC);
//
//
//    //
//    // Configuration for the SCI Tx pin.
//    //
//    GPIO_setMasterCore(29U, GPIO_CORE_CPU1);
//    GPIO_setPinConfig(GPIO_29_SCITXDA);
//    GPIO_setDirectionMode(29U, GPIO_DIR_MODE_OUT);
//    GPIO_setPadConfig(29U, GPIO_PIN_TYPE_STD);
//    GPIO_setQualificationMode(29U, GPIO_QUAL_ASYNC);
        // Configuration for the SCI Rx pin.
        //
        GPIO_setMasterCore(19U, GPIO_CORE_CPU1);
        GPIO_setPinConfig(GPIO_19_SCIRXDB);
        GPIO_setDirectionMode(19U, GPIO_DIR_MODE_IN);
        GPIO_setPadConfig(19U, GPIO_PIN_TYPE_STD);
        GPIO_setQualificationMode(19U, GPIO_QUAL_ASYNC);


        //
        // Configuration for the SCI Tx pin.
        //
        GPIO_setMasterCore(18U , GPIO_CORE_CPU1);
        GPIO_setPinConfig(GPIO_18_SCITXDB);
        GPIO_setDirectionMode(18U , GPIO_DIR_MODE_OUT);
        GPIO_setPadConfig(18U, GPIO_PIN_TYPE_STD);
        GPIO_setQualificationMode(18U , GPIO_QUAL_ASYNC);


    // Initialize interrupt controller and vector table.
    //
//    Interrupt_initModule();
//    Interrupt_initVectorTable();

    //
    // Initialize SCIA and its FIFO.
    //
    SCI_performSoftwareReset(SCIB_BASE); //SCIA_BASE

    //
    // Configure SCIA for echoback.
    //
    SCI_setConfig(SCIB_BASE, DEVICE_LSPCLK_FREQ,19200, (SCI_CONFIG_WLEN_8 |
                                                        SCI_CONFIG_STOP_ONE |
                                                        SCI_CONFIG_PAR_NONE));
    SCI_resetChannels(SCIB_BASE);
    SCI_resetRxFIFO(SCIB_BASE);
    SCI_resetTxFIFO(SCIB_BASE);
    SCI_clearInterruptStatus(SCIB_BASE, SCI_INT_TXFF | SCI_INT_RXFF);
    SCI_enableFIFO(SCIB_BASE);
    SCI_enableModule(SCIB_BASE);
    SCI_performSoftwareReset(SCIB_BASE);

#ifdef AUTOBAUD
    //
    // Perform an autobaud lock.
    // SCI expects an 'a' or 'A' to lock the baud rate.
    //
    SCI_lockAutobaud(SCIB_BASE);
#endif
}




/************************************************************************************
* Function: SCITxString
* - writes a C string of characters, one char at a time by calling
*   SCITxString. Stops when it encounters  the NULL character in the string
*   does NOT transmit the NULL character
* return: number of characters transmitted

************************************************************************************/
char SCI_TxString(uint32_t base,unsigned char *txString)
{
    char i=0;
    // Loop until the null terminator is encountered
    while (*txString != '\0')
    {
        // Send the current character over SCI
        SCI_writeCharBlockingNonFIFO(base, *txString);

        // Move to the next character in the string
        txString++;
        i++;//numofcharacter is transmitted
    }
    return i;

}




/*
 * Function: SCIRxString(uint32_t base,char * rxString)
 * Gets a string from SCI. Copy from the receive buffer until a return character is sent then return the string.
 *
 * Inputs: [char *] string pointer,uint32_t base
 * Returns: char 0 Successful, char -1 Fail
 */
char SCI_RxString(uint32_t base,char * rxString)
{

    uint16_t index = 0; // Index variable to store data into rxString

    // Loop to receive data from SCI port until encountering the '\r' character
    while (1)
    {
        // Read a character from the SCI port
        char receivedChar = SCI_readCharBlockingFIFO(base);

        // Check if the newly read character is '\r' (end-of-line character)
        if (receivedChar == '\r')
        {
            // End-of-line character received, end data reception
            rxString[index] = '\0'; // Append null terminator '\0' to the end of rxString array
            break;
        }

        // Store the received character in rxString at index position
        rxString[index] = receivedChar;

        // Move to the next position in the rxString array
        index++;

        // Check if exceeding the size of the rxString array
        if (index >= RX_BUFFER_SIZE)
        {
            // Receive buffer is full, handle this case here
            return-1;
        }
    }
    return 0;
}

/************************************************************************************
 * * Function: void SCI_writeCharBlockingFIFO(uint32_t base, uint16_t data);
Waits to send a character from the specified port when the FIFO enhancement is enabled.
Sends the character
data to the transmit buffer for the specified port. If there is no space available in the transmit FIFO, this function waits until there is space available before returning. data is a uint16_t but only 8 bits are written to the SCI port. SCI only transmits 8 bit characters.
Parameters
base: is the base address of the SCI port.
data: is the character to be transmitted.
Return
None.
************************************************************************************/
//void SCI_writeCharBlockingFIFO(uint32_t base, uint16_t data);


/************************************************************************************
 * * Function: uint16_t SCI_readCharBlockingFIFO(uint32_t base);
Waits for a character from the specified port when the FIFO enhancement is enabled.
Gets a character from the receive FIFO for the specified port. If there are no characters available,
this function waits until a character is received before returning. Returns immediately in case of Error.
Parameters
base: is the base address of the SCI port.
Return
Returns the character read from the specified port as uint16_t or 0x0 in case of Error. The application must use SCI_getRxStatus() API to check if some error occurred before consuming the data
************************************************************************************/
//uint16_t SCI_readCharBlockingFIFO(uint32_t base);

/************************************************************************************
 * Function:void SCI_writeCharArray(uint32_t base, const uint16_t *const array, uint16_t length);
//Waits to send an array of characters from the specified port.
//Sends the number of characters specified by
//length, starting at the address array, out of the transmit buffer for the specified port. If there is no space available in the transmit buffer, or the transmit FIFO if it is enabled, this function waits until there is space available and length number of characters are transmitted before returning. array is a pointer to uint16_ts but only the least significant 8 bits are written to the SCI port. SCI only transmits 8 bit characters.
//Parameters
//base: is the base address of the SCI port.
//array: is the address of the array of characters to be transmitted. It is pointer to the array of characters to be transmitted.
//length: is the length of the array, or number of characters in the array to be transmitted.
//Return
//None.
************************************************************************************/
//void SCI_writeCharArray(uint32_t base, const uint16_t *const array, uint16_t length);


/************************************************************************************
  * Function:void SCI_readCharArray(uint32_t base, uint16_t *const array, uint16_t length);
//Waits to receive an array of characters from the specified port.
//
//Receives an array of characters from the receive buffer for the specified port, and stores them as an array of characters starting at address
//
//array. This function waits until the length number of characters are received before returning.
//Parameters
//base: is the base address of the SCI port.
//
//array: is the address of the array of characters to be received. It is a pointer to the array of characters to be received.
//
//length: is the length of the array, or number of characters in the array to be received.
//
//Return
//None.
************************************************************************************/
//void SCI_readCharArray(uint32_t base, uint16_t *const array, uint16_t length);


//checking Error
//uint16_t rxStatus = 0U;
//rxStatus = SCI_getRxStatus(SCIA_BASE);
//if((rxStatus & SCI_RXSTATUS_ERROR) != 0)
//{
//    //
//    //If Execution stops here there is some error
//    //Analyze SCI_getRxStatus() API return value
//    //
//    ESTOP0;
//}




