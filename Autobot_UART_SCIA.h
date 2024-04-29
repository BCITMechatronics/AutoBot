/*
 * Autobot_UART_SCI.h
 *
 *  Created on: Feb 25, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_UART_SCIA_H_
#define AUTOBOT_UART_SCIA_H_
#include "driverlib.h"
#include "device.h"
#define RX_BUFFER_SIZE 100 // Define the maximum size of the receive buffer
#define BUFF_SZ        100

extern volatile char rxBuffer[RX_BUFFER_SIZE];
extern volatile unsigned int rxIndex;
extern volatile char receivedChar;
extern volatile unsigned char rxString[BUFF_SZ];


void Autobot_SCIA_init();
//char SCI_TxString(uint32_t base,unsigned char *txString);
//char SCI_RxString(uint32_t base,char * rxString);

//void SCI_writeCharBlockingFIFO(uint32_t base, uint16_t data);
//uint16_t SCI_readCharBlockingFIFO(uint32_t base);
//void SCI_writeCharArray(uint32_t base, const uint16_t *const array, uint16_t length); ex:SCI_writeCharArray(SCIA_BASE, msg, 22);
//void SCI_readCharArray(uint32_t base, uint16_t *const array, uint16_t length); ex:SCI_readCharArray(SCIA_BASE, RxBuffer,10);
__interrupt void sciaTXFIFOISR(void);
__interrupt void sciaRXFIFOISR(void);

#endif /* AUTOBOT_UART_SCI_H_ */
