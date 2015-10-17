/*
 * PulseWidth.cpp
 *
 * Created: 27/9/2015 03:58:53
 *  Author: Kaya
 */ 

#include <FreeRTOS.h>
#include <semphr.h>

#include <avr/interrupt.h>

extern uint32_t get_ticks();

SemaphoreHandle_t sema1, sema2, sema3, sema4;
int32_t *data_address1, *data_address2, *data_address3, *data_address4;
uint32_t start_time1, start_time2, start_time3, start_time4;
char stage1, stage2, stage3, stage4;

#define INT_CLEAR_PIN2() EIFR |= 1<<INTF4
#define INT_CLEAR_PIN3() EIFR |= 1<<INTF5
#define INT_CLEAR_PIN18() EIFR |= 1<<INTF3
#define INT_CLEAR_PIN19() EIFR |= 1<<INTF2

#define INT_ENABLE_PIN2() EIMSK |= (1 << INT4)
#define INT_ENABLE_PIN3() EIMSK |= (1 << INT5)
#define INT_ENABLE_PIN18() EIMSK |= (1 << INT3)
#define INT_ENABLE_PIN19() EIMSK |= (1 << INT2)

#define INT_DISABLE_PIN2() EIMSK &= ~(1 << INT4)
#define INT_DISABLE_PIN3() EIMSK &= ~(1 << INT5)
#define INT_DISABLE_PIN18() EIMSK &= ~(1 << INT3)
#define INT_DISABLE_PIN19() EIMSK &= ~(1 << INT2)

void pulse_init()
{
	//pin 2		PE 4	INT4
	//pin 3		PE 5	INT5
	//pin 18	PD 3	INT3
	//pin 19	PD 2	INT2
	//pin 20	PD 1	INT1 SDA
	//pin 21	PD 0	INT0 SCL
	//mode 00 low 01 change 10 falling 11 rising
	
	EICRA = (EICRA & ~((1 << ISC20) | (1 << ISC21))) | (0b01 << ISC20);
	
	EICRA = (EICRA & ~((1 << ISC30) | (1 << ISC31))) | (0b01 << ISC30);

	EICRB = (EICRB & ~((1 << ISC40) | (1 << ISC41))) | (0b01 << ISC40);

	EICRB = (EICRB & ~((1 << ISC50) | (1 << ISC51))) | (0b01 << ISC50);
}

void pulse_read(char pin, SemaphoreHandle_t semaphore, int32_t* address)
{
	char pin_state;
	
	switch (pin)
	{
		case 2:
			INT_DISABLE_PIN2();
			sema1 = semaphore;
			data_address1 = address;
			pin_state = PINE&(1<<PE4);
			if (pin_state)
			{
				stage1 = 0;
			}
			else
			{
				stage1 = 1;
			}
			INT_CLEAR_PIN2();
			INT_ENABLE_PIN2();
			break;
		case 3:
			INT_DISABLE_PIN3();
			sema2 = semaphore;
			data_address2 = address;
			pin_state = PINE&(1<<PE5);
			if (pin_state)
			{
				stage2 = 0;
			}
			else
			{
				stage2 = 1;
			}
			INT_CLEAR_PIN3();
			INT_ENABLE_PIN3();
			break;
		case 18:
			INT_DISABLE_PIN18();
			sema3 = semaphore;
			data_address3 = address;
			pin_state = PIND&(1<<PD3);
			if (pin_state)
			{
				stage3 = 0;
			}
			else
			{
				stage3 = 1;
			}
			INT_CLEAR_PIN18();
			INT_ENABLE_PIN18();
			break;
		case 19:
			INT_DISABLE_PIN19();
			sema4 = semaphore;
			data_address4 = address;
			pin_state = PIND&(1<<PD2);
			if (pin_state)
			{
				stage4 = 0;
			}
			else
			{
				stage4 = 1;
			}
			INT_CLEAR_PIN19();
			INT_ENABLE_PIN19();
			break;
		default:
			break;
	}
}

void pulse_stop(char pin)
{
	switch (pin)
	{
		case 2:
			INT_DISABLE_PIN2();
			break;
		case 3:
			INT_DISABLE_PIN3();
			break;
		case 18:
			INT_DISABLE_PIN18();
			break;
		case 19:
			INT_DISABLE_PIN19();
			break;
		default:
			break;
	}
	
}

//pin 19
ISR(INT2_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PIND&(1<<PD2);
	++stage4;
	if (stage4 == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage4 == 2 && pin_state)
	{
		start_time4 = time * 1000 + (TCNT1>>1);
	}
	else if (stage4 == 3 && !pin_state)
	{
		*(data_address4) = (time * 1000 + (TCNT1>>1)) - start_time4;
		xSemaphoreGiveFromISR(sema4, NULL);
		INT_DISABLE_PIN19();
	}
	else
	{
		*(data_address4) = 1;
		xSemaphoreGiveFromISR(sema4, NULL);
		INT_DISABLE_PIN19();
	}
}

//pin 18
ISR(INT3_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PIND&(1<<PD3);
	++stage3;
	if (stage3 == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage3 == 2 && pin_state)
	{
		start_time3 = time * 1000 + (TCNT1>>1);
	}
	else if (stage3 == 3 && !pin_state)
	{
		*(data_address3) = (time * 1000 + (TCNT1>>1)) - start_time3;
		xSemaphoreGiveFromISR(sema3, NULL);
		INT_DISABLE_PIN18();
	}
	else
	{
		*(data_address3) = 1;
		xSemaphoreGiveFromISR(sema3, NULL);
		INT_DISABLE_PIN18();
	}
}

//pin 2
ISR(INT4_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PINE&(1<<PE4);
	++stage1;
	if (stage1 == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage1 == 2 && pin_state)
	{
		start_time1 = time * 1000 + (TCNT1>>1);
	}
	else if (stage1 == 3 && !pin_state)
	{
		*(data_address1) = (time * 1000 + (TCNT1>>1)) - start_time1;
		xSemaphoreGiveFromISR(sema1, NULL);
		INT_DISABLE_PIN2();
	}
	else
	{
		*(data_address1) = 1;
		xSemaphoreGiveFromISR(sema1, NULL);
		INT_DISABLE_PIN2();
	}
}

//pin 3
ISR(INT5_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PINE&(1<<PE5);
	++stage2;
	if (stage2 == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage2 == 2 && pin_state)
	{
		start_time2 = time * 1000 + (TCNT1>>1);
	}
	else if (stage2 == 3 && !pin_state)
	{
		*(data_address2) = (time * 1000 + (TCNT1>>1)) - start_time2;
		xSemaphoreGiveFromISR(sema2, NULL);
		INT_DISABLE_PIN3();
	}
	else
	{
		*(data_address2) = 1;
		xSemaphoreGiveFromISR(sema2, NULL);
		INT_DISABLE_PIN3();
	}
}