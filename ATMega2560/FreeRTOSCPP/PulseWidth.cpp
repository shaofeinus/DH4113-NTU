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

SemaphoreHandle_t sema[4];
int32_t* data_address[4];
uint32_t start_time[4];
char stage[4];

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
			sema[0] = semaphore;
			data_address[0] = address;
			pin_state = PINE&(1<<PE4);
			if (pin_state)
			{
				stage[0] = 0;
			}
			else
			{
				stage[0] = 1;
			}
			INT_CLEAR_PIN2();
			INT_ENABLE_PIN2();
			break;
		case 3:
			INT_DISABLE_PIN3();
			sema[1] = semaphore;
			data_address[1] = address;
			pin_state = PINE&(1<<PE5);
			if (pin_state)
			{
				stage[1] = 0;
			}
			else
			{
				stage[1] = 1;
			}
			INT_CLEAR_PIN3();
			INT_ENABLE_PIN3();
			break;
		case 18:
			INT_DISABLE_PIN18();
			sema[2] = semaphore;
			data_address[2] = address;
			pin_state = PIND&(1<<PD3);
			if (pin_state)
			{
				stage[2] = 0;
			}
			else
			{
				stage[2] = 1;
			}
			INT_CLEAR_PIN18();
			INT_ENABLE_PIN18();
			break;
		case 19:
			INT_DISABLE_PIN19();
			sema[3] = semaphore;
			data_address[3] = address;
			pin_state = PIND&(1<<PD2);
			if (pin_state)
			{
				stage[3] = 0;
			}
			else
			{
				stage[3] = 1;
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
	++stage[3];
	if (stage[3] == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage[3] == 2 && pin_state)
	{
		start_time[3] = time * 1000 + (TCNT1>>1);
	}
	else if (stage[3] == 3 && !pin_state)
	{
		*(data_address[3]) = (time * 1000 + (TCNT1>>1)) - start_time[3];
		xSemaphoreGiveFromISR(sema[3], NULL);
		INT_DISABLE_PIN19();
	}
	else
	{
		*(data_address[3]) = 0;
		xSemaphoreGiveFromISR(sema[3], NULL);
		INT_DISABLE_PIN19();
	}
}

//pin 18
ISR(INT3_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PIND&(1<<PD3);
	++stage[2];
	if (stage[2] == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage[2] == 2 && pin_state)
	{
		start_time[2] = time * 1000 + (TCNT1>>1);
	}
	else if (stage[2] == 3 && !pin_state)
	{
		*(data_address[2]) = (time * 1000 + (TCNT1>>1)) - start_time[2];
		xSemaphoreGiveFromISR(sema[2], NULL);
		INT_DISABLE_PIN18();
	}
	else
	{
		*(data_address[2]) = 0;
		xSemaphoreGiveFromISR(sema[2], NULL);
		INT_DISABLE_PIN18();
	}
}

//pin 2
ISR(INT4_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PINE&(1<<PE4);
	++stage[0];
	if (stage[0] == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage[0] == 2 && pin_state)
	{
		start_time[0] = time * 1000 + (TCNT1>>1);
	}
	else if (stage[0] == 3 && !pin_state)
	{
		*(data_address[0]) = (time * 1000 + (TCNT1>>1)) - start_time[0];
		xSemaphoreGiveFromISR(sema[0], NULL);
		INT_DISABLE_PIN2();
	}
	else
	{
		*(data_address[0]) = 0;
		xSemaphoreGiveFromISR(sema[0], NULL);
		INT_DISABLE_PIN2();
	}
}

//pin 3
ISR(INT5_vect)
{
	uint32_t time = get_ticks();
	char pin_state = PINE&(1<<PE5);
	++stage[1];
	if (stage[1] == 1 && !pin_state)
	{
		//Do nothing
	}
	else if (stage[1] == 2 && pin_state)
	{
		start_time[1] = time * 1000 + (TCNT1>>1);
	}
	else if (stage[1] == 3 && !pin_state)
	{
		*(data_address[1]) = (time * 1000 + (TCNT1>>1)) - start_time[1];
		xSemaphoreGiveFromISR(sema[1], NULL);
		INT_DISABLE_PIN3();
	}
	else
	{
		*(data_address[1]) = 0;
		xSemaphoreGiveFromISR(sema[1], NULL);
		INT_DISABLE_PIN3();
	}
}