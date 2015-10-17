/*
 * AltIMUv4.cpp
 *
 * Created: 16/9/2015 13:11:48
 *  Author: Kaya
 */ 

#include <stdio.h>

#include "i2c.h"

namespace LSM303
{
	enum
	{
		ADDR              = 0x3A,
		ADDRW             = ADDR,
		ADDRR             = ADDR|0x01,
		
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
}

char lsm303_whoami()
{
	char a;
	twi_start();
	twi_send_address(LSM303::ADDRW); //write
	twi_send_data(LSM303::WHO_AM_I); //WHOAMI
	twi_start();
	twi_send_address(LSM303::ADDRR); //read
	twi_read_data(&a, 0);
	twi_stop();
	return a;
}

void lsm303_write(char reg, char data)
{
	twi_start();
	twi_send_address(LSM303::ADDRW); //write
	twi_send_data(reg);
	twi_send_data(data);
	twi_stop();
}

void lsm303_init()
{
	// 0x00 = 0b00000000
	// AFS = 0 (+/- 2 g full scale)
	lsm303_write(LSM303::CTRL2, 0x00);

	// 0x57 = 0b01010111
	// AODR = 0101 (50 Hz ODR); AZEN = AYEN = AXEN = 1 (all axes enabled)
	//lsm303_write(LSM303::CTRL1, 0x57);
	// 0x67 = 0b01100111
	// AODR = 0110 (100 Hz ODR); AZEN = AYEN = AXEN = 1 (all axes enabled)
	lsm303_write(LSM303::CTRL1, 0x67);

	// Magnetometer

	// 0x64 = 0b01100100
	// M_RES = 11 (high resolution mode); M_ODR = 001 (6.25 Hz ODR)
	//lsm303_write(LSM303::CTRL5, 0x64);
	// 0x74 = 0b01110100
	// M_RES = 11 (high resolution mode); M_ODR = 101 (100 Hz ODR)
	lsm303_write(LSM303::CTRL5, 0x74);

	// 0x20 = 0b00100000
	// MFS = 01 (+/- 4 gauss full scale)
	//lsm303_write(LSM303::CTRL6, 0x20);
	// 0x00 = 0b00000000
	// MFS = 00 (+/- 2 gauss full scale)
	lsm303_write(LSM303::CTRL6, 0x00);

	// 0x00 = 0b00000000
	// MLP = 0 (low power mode off); MD = 00 (continuous-conversion mode)
	lsm303_write(LSM303::CTRL7, 0x00);
}

void lsm303_read_acc(int16_t *x, int16_t *y, int16_t *z)
{
	char xl, xh, yl, yh, zl, zh;
	twi_start();
	twi_send_address(LSM303::ADDRW);
	twi_send_data(LSM303::OUT_X_L_A|(1<<7));
	twi_start();
	twi_send_address(LSM303::ADDRR); //read
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
	twi_send_address(LSM303::ADDRW);
	twi_send_data(LSM303::D_OUT_X_L_M|(1<<7));
	twi_start();
	twi_send_address(LSM303::ADDRR); //read
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

namespace L3GD20H
{
	enum
	{
		ADDR                    = 0xD6,
		ADDRW                   = ADDR,
		ADDRR                   = ADDR|0x01,
		
		WHO_AM_I       = 0x0F,

		CTRL1          = 0x20, // D20H
		CTRL2          = 0x21, // D20H
		CTRL3          = 0x22, // D20H
		CTRL4          = 0x23, // D20H
		CTRL5          = 0x24, // D20H
		REFERENCE      = 0x25,
		OUT_TEMP       = 0x26,
		STATUS         = 0x27, // D20H
		
		OUT_X_L        = 0x28,
		OUT_X_H        = 0x29,
		OUT_Y_L        = 0x2A,
		OUT_Y_H        = 0x2B,
		OUT_Z_L        = 0x2C,
		OUT_Z_H        = 0x2D,

		FIFO_CTRL      = 0x2E, // D20H
		FIFO_SRC       = 0x2F, // D20H
		
		IG_CFG         = 0x30, // D20H
		IG_SRC         = 0x31, // D20H
		IG_THS_XH      = 0x32, // D20H
		IG_THS_XL      = 0x33, // D20H
		IG_THS_YH      = 0x34, // D20H
		IG_THS_YL      = 0x35, // D20H
		IG_THS_ZH      = 0x36, // D20H
		IG_THS_ZL      = 0x37, // D20H
		IG_DURATION    = 0x38, // D20H
		
		LOW_ODR        = 0x39  // D20H
	};
}

void l3gd20h_write(char reg, char data)
{
	twi_start();
	twi_send_address(L3GD20H::ADDRW); //write
	twi_send_data(reg);
	twi_send_data(data);
	twi_stop();
}

void l3gd20h_init()
{
	// 0x00 = 0b00000000
	// Low_ODR = 0 (low speed ODR disabled)
	l3gd20h_write(L3GD20H::LOW_ODR, 0x00);
	
	// 0x00 = 0b00000000
	// FS = 00 (+/- 250 dps full scale)
	l3gd20h_write(L3GD20H::CTRL4, 0x00);
	
	// 0x6F = 0b01101111
	// DR = 01 (200 Hz ODR); BW = 10 (50 Hz bandwidth); PD = 1 (normal mode); Zen = Yen = Xen = 1 (all axes enabled)
	l3gd20h_write(L3GD20H::CTRL1, 0x6F);
}

void l3gd20h_read(int16_t *x, int16_t *y, int16_t *z)
{
	char xl, xh, yl, yh, zl, zh;
	twi_start();
	twi_send_address(L3GD20H::ADDRW);
	twi_send_data(L3GD20H::OUT_X_L|(1<<7));
	twi_start();
	twi_send_address(L3GD20H::ADDRR); //read
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

namespace LPS25H
{
	enum
	{
		ADDR                    = 0xBA,
		ADDRW                   = ADDR,
		ADDRR                   = ADDR|0x01,
		
		REF_P_XL                = 0x08,
		REF_P_L                 = 0x09,
		REF_P_H                 = 0x0A,
		
		WHO_AM_I                = 0x0F,
		
		RES_CONF                = 0x10,
		
		CTRL_REG1               = 0x20,
		CTRL_REG2               = 0x21,
		CTRL_REG3               = 0x22,
		CTRL_REG4               = 0x23, // 25H
		
		INT_CFG                 = 0x24,
		INT_SOURCE              = 0x25,
		
		STATUS_REG              = 0x27,
		
		PRESS_OUT_XL            = 0x28,
		PRESS_OUT_L             = 0x29,
		PRESS_OUT_H             = 0x2A,

		TEMP_OUT_L              = 0x2B,
		TEMP_OUT_H              = 0x2C,
		
		FIFO_CTRL               = 0x2E, // 25H
		FIFO_STATUS             = 0x2F, // 25H
		
		THS_P_L                 = 0x30,
		THS_P_H                 = 0x31,
		
		RPDS_L                  = 0x39, // 25H
		RPDS_H                  = 0x3A  // 25H
	};
}

void lps25h_init()
{
	// 0xB0 = 0b10110000
	// PD = 1 (active mode);  ODR = 011 (12.5 Hz pressure & temperature output data rate)
	twi_start();
	twi_send_address(LPS25H::ADDRW); //write
	twi_send_data(LPS25H::CTRL_REG1);
	twi_send_data(0xB0);
	twi_stop();
}

int32_t lps25h_read() 
{
	char xl, l, h;
	twi_start();
	twi_send_address(LPS25H::ADDRW);
	twi_send_data(LPS25H::PRESS_OUT_XL|(1<<7));
	twi_start();
	twi_send_address(LPS25H::ADDRR); //read
	twi_read_data(&xl, 1);
	twi_read_data(&l, 1);
	twi_read_data(&h, 0);
	twi_stop();
	return ((int32_t)h << 16) | ((int32_t)l << 8) | xl;
}