/*
 * AltIMUv4.cpp
 *
 * Created: 16/9/2015 13:11:48
 *  Author: Kaya
 */ 

#include <stdio.h>

#include "i2c.h"

#define ADDR 0x3A
#define ADDRW ADDR
#define ADDRR ADDR|0x01

enum regAddr
{
	TEMP_OUT_L        = 0x05, // D
	TEMP_OUT_H        = 0x06, // D

	STATUS_M          = 0x07, // D

	INT_CTRL_M        = 0x12, // D
	INT_SRC_M         = 0x13, // D
	INT_THS_L_M       = 0x14, // D
	INT_THS_H_M       = 0x15, // D

	OFFSET_X_L_M      = 0x16, // D
	OFFSET_X_H_M      = 0x17, // D
	OFFSET_Y_L_M      = 0x18, // D
	OFFSET_Y_H_M      = 0x19, // D
	OFFSET_Z_L_M      = 0x1A, // D
	OFFSET_Z_H_M      = 0x1B, // D
	REFERENCE_X       = 0x1C, // D
	REFERENCE_Y       = 0x1D, // D
	REFERENCE_Z       = 0x1E, // D

	CTRL0             = 0x1F, // D
	CTRL1             = 0x20, // D
	CTRL2             = 0x21, // D
	CTRL3             = 0x22, // D
	CTRL4             = 0x23, // D
	CTRL5             = 0x24, // D
	CTRL6             = 0x25, // D
	CTRL7             = 0x26, // D
	STATUS_A          = 0x27, // D

	OUT_X_L_A         = 0x28,
	OUT_X_H_A         = 0x29,
	OUT_Y_L_A         = 0x2A,
	OUT_Y_H_A         = 0x2B,
	OUT_Z_L_A         = 0x2C,
	OUT_Z_H_A         = 0x2D,

	FIFO_CTRL         = 0x2E, // D
	FIFO_SRC          = 0x2F, // D

	IG_CFG1           = 0x30, // D
	IG_SRC1           = 0x31, // D
	IG_THS1           = 0x32, // D
	IG_DUR1           = 0x33, // D
	IG_CFG2           = 0x34, // D
	IG_SRC2           = 0x35, // D
	IG_THS2           = 0x36, // D
	IG_DUR2           = 0x37, // D

	CLICK_CFG         = 0x38, // D
	CLICK_SRC         = 0x39, // D
	CLICK_THS         = 0x3A, // D
	TIME_LIMIT        = 0x3B, // D
	TIME_LATENCY      = 0x3C, // D
	TIME_WINDOW       = 0x3D, // D

	Act_THS           = 0x3E, // D
	Act_DUR           = 0x3F, // D

	WHO_AM_I          = 0x0F, // D

	D_OUT_X_L_M       = 0x08,
	D_OUT_X_H_M       = 0x09,
	D_OUT_Y_L_M       = 0x0A,
	D_OUT_Y_H_M       = 0x0B,
	D_OUT_Z_L_M       = 0x0C,
	D_OUT_Z_H_M       = 0x0D
};

char LSM303_whoami()
{
	char a;
	twi_start();
	twi_send_address(ADDRW); //write
	twi_send_data(WHO_AM_I); //WHOAMI
	twi_start();
	twi_send_address(ADDRR); //read
	twi_read_data(&a, 0);
	twi_stop();
	return a;
}

void LSM303_write(char reg, char data)
{
	twi_start();
	twi_send_address(ADDR); //write
	twi_send_data(reg);
	twi_send_data(data);
	twi_stop();
}

void lsm303_init()
{
	// 0x00 = 0b00000000
	// AFS = 0 (+/- 2 g full scale)
	LSM303_write(CTRL2, 0x00);

	// 0x57 = 0b01010111
	// AODR = 0101 (50 Hz ODR); AZEN = AYEN = AXEN = 1 (all axes enabled)
	LSM303_write(CTRL1, 0x57);

	// Magnetometer

	// 0x64 = 0b01100100
	// M_RES = 11 (high resolution mode); M_ODR = 001 (6.25 Hz ODR)
	LSM303_write(CTRL5, 0x64);

	// 0x20 = 0b00100000
	// MFS = 01 (+/- 4 gauss full scale)
	LSM303_write(CTRL6, 0x20);

	// 0x00 = 0b00000000
	// MLP = 0 (low power mode off); MD = 00 (continuous-conversion mode)
	LSM303_write(CTRL7, 0x00);
}

void lsm303_read_acc(int16_t *x, int16_t *y, int16_t *z)
{
	char xl, xh, yl, yh, zl, zh;
	twi_start();
	twi_send_address(ADDRW);
	twi_send_data(OUT_X_L_A|(1<<7));
	twi_start();
	twi_send_address(ADDRR); //read
	twi_read_data(&xl, 1);
	twi_read_data(&xh, 1);
	twi_read_data(&yl, 1);
	twi_read_data(&yh, 1);
	twi_read_data(&zl, 1);
	twi_read_data(&zh, 0);
	twi_stop();
	*x = (int16_t)(xh << 8 | xl);
	*y = (int16_t)(yh << 8 | yl);
	*z = (int16_t)(zh << 8 | zl);
}

void lsm303_read_mag(int16_t *x, int16_t *y, int16_t *z)
{
	char xl, xh, yl, yh, zl, zh;
	twi_start();
	twi_send_address(ADDRW);
	twi_send_data(D_OUT_X_L_M|(1<<7));
	twi_start();
	twi_send_address(ADDRR); //read
	twi_read_data(&xl, 1);
	twi_read_data(&xh, 1);
	twi_read_data(&yl, 1);
	twi_read_data(&yh, 1);
	twi_read_data(&zl, 1);
	twi_read_data(&zh, 0);
	twi_stop();
	*x = (int16_t)(xh << 8 | xl);
	*y = (int16_t)(yh << 8 | yl);
	*z = (int16_t)(zh << 8 | zl);
}