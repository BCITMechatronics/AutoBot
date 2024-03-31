/*
 * Autobot_MotorControl.h
 *
 *  Created on: Mar 1, 2024
 *      Author: haduy
 */

#ifndef AUTOBOT_MOTORCONTROL_H_
#define AUTOBOT_MOTORCONTROL_H_
#include "driverlib.h"
#include "device.h"
#include <board.h>
#include <Autobot_EPWM.h>
#include "stdint.h"


// Định nghĩa các hằng số

#define MOTOR_PWM_MAX_VALUE 2000-1  // Giá trị tối đa của PWM (tùy thuộc vào độ phân giải của PWM)
#define MOTOR_PWM_MIN_VALUE 0     // Giá trị tối thiểu của PWM
#define MOVE_UP 1
#define MOVE_DOWN 0
#define IN_1 22
#define IN_2 21
#define PWM_DUTY_CYCLES 40
void Autobot_MotorDriver_int();

void MotorDriver_setDirection(unsigned char Direction);

// Hàm điều khiển tốc độ động cơ
void MotorDriver_setSpeed(unsigned char SpeedInPercent);

// Hàm dừng động cơ
void MotorDriver_stop();
#endif /* AUTOBOT_MOTORCONTROL_H_ */
