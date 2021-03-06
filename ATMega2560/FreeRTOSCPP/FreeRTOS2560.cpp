/*
*
freertos2560.c
*
*/
#include <avr/io.h>
#include <avr/wdt.h>

#include <FreeRTOS.h>
#include <task.h>
#include <semphr.h>

#include <stdio.h>
#include <stdlib.h>

#include "AltIMUv4.h"
#include "i2c.h"
#include "PulseWidth.h"

#define COUNT_IR 5
#define COUNT_US 3

SemaphoreHandle_t a_updated, m_updated, ba_updated, g_updated, ir_updated, us1_updated, us2_updated, us3_updated;
int32_t ba_p;
int16_t a_x, a_y, a_z, m_x, m_y, m_z, g_x, g_y, g_z;
uint16_t ir1_dist, ir2_dist, ir3_dist, ir4_dist, ir5_dist, ir_long_dist;
int32_t us1_dist, us2_dist, us3_dist;
uint32_t a_last_update, m_last_update, ba_last_update, g_last_update, ir1_last_update, ir2_last_update, ir3_last_update, ir4_last_update, ir5_last_update, ir_long_last_update, us1_last_update, us2_last_update, us3_last_update;
uint32_t ticks;

void twi_init();

void usart_send(char a);
char usart_recv();
void usart_init(unsigned long baud);

void debug_send(char a);
char debug_recv();
void debug_init(unsigned long baud);

void analog_init();
int16_t analog_read(int pin);
void delayus(uint16_t delta);

int32_t measure_pulse_us(volatile uint8_t *port, uint8_t pin, uint8_t state, uint32_t timeout);

enum deviceId
{
	ACCEL		= 0x10,	// 1
	COMPASS		= 0x20,	// 2
	GYRO		= 0x30, // 3
	BAROMETER	= 0x40,	// 4
	
	IR1			= 0x60,	// 6
	IR2			= 0x70,	// 7
	IR3			= 0x80,	// 8
	IR4			= 0x90,	// 9
	IR5			= 0xA0,	// 10
	
	US1			= 0xB0,	// 11
	US2			= 0xC0,	// 12
	US3			= 0xD0,	// 13
	US4			= 0xE0,	// 14
	
	IRLONG		= 0xF0	// 15
};

int freeRam() 
{
	extern int __heap_start, *__brkval;
	int v;
	return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}

inline void send_data(char id, uint16_t time, char *data, int size)
{
	int i;
	usart_send(id|((time>>8)&0x0F));
	usart_send(time&0xFF);
	for (i = 0; i < size; ++i)
	{
		usart_send(data[i]);
	}
}

//Tasks flash LEDs at Pins 12 and 13 at 1Hz and 2Hz respectively.
void usart_process(void *p)
{
	char data[6];
	while(1)
	{
		if (xSemaphoreTake(a_updated, 0) == pdTRUE)
		{
			data[0] = a_x>>8;
			data[1] = a_x;
			data[2] = a_y>>8;
			data[3] = a_y;
			data[4] = a_z>>8;
			data[5] = a_z;
			send_data(ACCEL, a_last_update, data, 6);
		}
		
		if (xSemaphoreTake(m_updated, 0) == pdTRUE)
		{
			data[0] = m_x>>8;
			data[1] = m_x;
			data[2] = m_y>>8;
			data[3] = m_y;
			data[4] = m_z>>8;
			data[5] = m_z;
			send_data(COMPASS, m_last_update, data, 6);
		}
		
		if (xSemaphoreTake(g_updated, 0) == pdTRUE)
		{
			data[0] = g_x>>8;
			data[1] = g_x;
			data[2] = g_y>>8;
			data[3] = g_y;
			data[4] = g_z>>8;
			data[5] = g_z;
			send_data(GYRO, g_last_update, data, 6);
		}
		
		if (xSemaphoreTake(ba_updated, 0) == pdTRUE)
		{
			data[0] = ba_p>>16;
			data[1] = ba_p>>8;
			data[2] = ba_p;
			send_data(BAROMETER, ba_last_update, data, 3);
		}
		
		if (xSemaphoreTake(ir_updated, 0) == pdTRUE)
		{
			data[0] = ir1_dist>>8;
			data[1] = ir1_dist;
			send_data(IR1, ir1_last_update, data, 2);
			data[0] = ir2_dist>>8;
			data[1] = ir2_dist;
			send_data(IR2, ir2_last_update, data, 2);
			data[0] = ir3_dist>>8;
			data[1] = ir3_dist;
			send_data(IR3, ir3_last_update, data, 2);
			data[0] = ir4_dist>>8;
			data[1] = ir4_dist;
			send_data(IR4, ir4_last_update, data, 2);
			data[0] = ir5_dist>>8;
			data[1] = ir5_dist;
			send_data(IR5, ir5_last_update, data, 2);
			data[0] = ir_long_dist>>8;
			data[1] = ir_long_dist;
			send_data(IRLONG, ir_long_last_update, data, 2);
		}
		
		if (xSemaphoreTake(us1_updated, 0) == pdTRUE)
		{
			data[0] = us1_dist>>8;
			data[1] = us1_dist;
			send_data(US1, us1_last_update, data, 2);
		}
		
		if (xSemaphoreTake(us2_updated, 0) == pdTRUE)
		{
			data[0] = us2_dist>>8;
			data[1] = us2_dist;
			send_data(US2, us2_last_update, data, 2);
		}
		
		if (xSemaphoreTake(us3_updated, 0) == pdTRUE)
		{
			data[0] = us3_dist>>8;
			data[1] = us3_dist;
			send_data(US3, us3_last_update, data, 2);
		}
	}
}

void twowire_process(void *p)
{
	twi_init();
	lsm303_init();
	lps25h_init();
	l3gd20h_init();
	//start watchdog
	//wdt_enable(WDTO_60MS);
	while(1)
	{
		//wdt_reset();
		lsm303_read_acc(&a_x, &a_y, &a_z);
		a_last_update = ticks;
		xSemaphoreGive(a_updated);
		
		lsm303_read_mag(&m_x, &m_y, &m_z);
		m_last_update = ticks;
		xSemaphoreGive(m_updated);
		
		l3gd20h_read(&g_x, &g_y, &g_z);
		g_last_update = ticks;
		xSemaphoreGive(g_updated);
		
		//vTaskDelay(5);
		if (ticks >= ba_last_update+80)
		{
			ba_p = lps25h_read();
			ba_last_update = ticks;
			xSemaphoreGive(ba_updated);	
		}
		
		vTaskDelay(20);
	}
}

void distir_process(void *p)
{
	analog_init();
	while(1)
	{
		ir1_dist = analog_read(0);
		ir1_last_update = ticks;
		ir2_dist = analog_read(1);
		ir2_last_update = ticks;
		ir3_dist = analog_read(2);
		ir3_last_update = ticks;
		ir4_dist = analog_read(3);
		ir4_last_update = ticks;
		ir5_dist = analog_read(4);
		ir5_last_update = ticks;
		ir_long_dist = analog_read(7);
		ir_long_last_update = ticks;
		xSemaphoreGive(ir_updated);
		vTaskDelay(100);
	}
}

void distultrasound_process(void *p)
{
	#define US0_TIMEOUT 20000
	#define US0_TIMEOUT_DELAY US0_TIMEOUT/10000*12
	// PA 1 ** 23 ** D23
	// PA 3 ** 25 ** D25
	// PA 5 ** 27 ** D27
	// PA 7 ** 29 ** D29
	// pin 2	PE 4	INT4
	// pin 3	PE 5	INT5
	// pin 18	PD 3	INT3
	// pin 19	PD 2	INT2
	SemaphoreHandle_t result_updated = xSemaphoreCreateBinary();
	
	DDRD &= ~(1<<PD2);
	DDRD &= ~(1<<PD3);
	DDRE &= ~(1<<PE4);
	DDRE &= ~(1<<PE5);
	
	DDRA |= (1<<PA1);
	DDRA |= (1<<PA3);
	DDRA |= (1<<PA5);
	DDRA |= (1<<PA7);
	pulse_init();
	while(1)
	{
		// pin 29 trig pin 19 echo
		PORTA &= ~(1<<PA7);
		delayus(2);
		PORTA |= (1<<PA7);
		delayus(10);
		PORTA &= ~(1<<PA7);
		xSemaphoreTake(result_updated, 0);
		pulse_read(19, result_updated, &us1_dist);
		if (xSemaphoreTake(result_updated, 20) == pdFALSE)
		{
			pulse_stop(19);
			us1_dist = 0;
		}
		us1_last_update = ticks;
		xSemaphoreGive(us1_updated);
		if (us1_dist == 0)
		{
			vTaskDelay(13);
		}
		else
		{
			vTaskDelay(33-(us1_dist>>10));
		}
			
		// pin 27 trig pin 18 echo
		PORTA &= ~(1<<PA5);
		delayus(2);
		PORTA |= (1<<PA5);
		delayus(10);
		PORTA &= ~(1<<PA5);
		xSemaphoreTake(result_updated, 0);
		pulse_read(18, result_updated, &us2_dist);
		if (xSemaphoreTake(result_updated, 20) == pdFALSE)
		{
			pulse_stop(18);
			us2_dist = 0;
		}
		us2_last_update = ticks;
		xSemaphoreGive(us2_updated);
		if (us2_dist == 0)
		{
			vTaskDelay(13);	
		}
		else
		{
			vTaskDelay(33-(us2_dist>>10));
		}
		
		// pin 25 trig pin 3 echo
		PORTA &= ~(1<<PA3);
		delayus(2);
		PORTA |= (1<<PA3);
		delayus(10);
		PORTA &= ~(1<<PA3);
		xSemaphoreTake(result_updated, 0);
		pulse_read(2, result_updated, &us3_dist);
		if (xSemaphoreTake(result_updated, 20) == pdFALSE)
		{
			pulse_stop(2);
			us3_dist = 0;
		}
		us3_last_update = ticks;
		xSemaphoreGive(us3_updated);
		if (us3_dist == 0)
		{
			vTaskDelay(13);
		}
		else
		{
			vTaskDelay(33-(us3_dist>>10));
		}
	}
}

extern "C" void vApplicationTickHook()
{
	++ticks;
}

uint32_t get_ticks()
{
	return ticks;
}

void vApplicationIdleHook()
{
	// Do nothing.
}

uint8_t mcusr_mirror __attribute__ ((section (".noinit")));

void get_mcusr(void) \
__attribute__((naked)) \
__attribute__((section(".init1")));
void get_mcusr(void)
{
	mcusr_mirror = MCUSR;
	MCUSR = 0;
	wdt_disable();
}

#define STACK_DEPTH 80 // tested 68 minimum

int main()
{
	TaskHandle_t t1, t2, t3, t4;
	ticks = 0;
	
	debug_init(115200);
	usart_init(115200);
	debug_send('S');
	debug_send(mcusr_mirror);
	debug_send('\r');
	debug_send('\n');
	
	a_updated = xSemaphoreCreateBinary();
	m_updated = xSemaphoreCreateBinary();
	g_updated = xSemaphoreCreateBinary();
	ba_updated = xSemaphoreCreateBinary();
	ir_updated = xSemaphoreCreateBinary();
	us1_updated = xSemaphoreCreateBinary();	
	us2_updated = xSemaphoreCreateBinary();	
	us3_updated = xSemaphoreCreateBinary();	
	
	// pin 49 PL 0
	// 5v to turn off accelerometer
	// gnd to turn on accelerometer
	DDRL &= ~(1<<PL0);
	
	//	Create tasks 
	xTaskCreate(usart_process, "usart", STACK_DEPTH, NULL, 1, &t1);
	if (!(PINL&(1<<PL0))) 
	{
		xTaskCreate(twowire_process, "twowire", STACK_DEPTH, NULL, 3, &t2);
	}
	xTaskCreate(distir_process, "distir", STACK_DEPTH, NULL, 2, &t3);
	xTaskCreate(distultrasound_process, "distus", STACK_DEPTH, NULL, 2, &t4);
	
	vTaskStartScheduler();
}

void twi_init()
{
	twi_set_frequency(400000L);
}

void usart_init(unsigned long baud)
{
	//unsigned int ubrr = (F_CPU/4/baud-1)/2;
	unsigned int ubrr = F_CPU/8/baud - 1;
	
	UCSR3A = 1<<U2X3;
	/* Set baud rate */
	UBRR3H = (unsigned char)(ubrr>>8);
	UBRR3L = (unsigned char)ubrr;
	/* Enable receiver and transmitter */
	UCSR3B = (1<<RXEN3)|(1<<TXEN3);
	/* Set frame format: 8data, 1stop bit */
	UCSR3C = (3<<UCSZ30);//(1<<USBS3)| 2 stopbit
}

void usart_send(char a)
{
	debug_send(a);
	while ( !( UCSR3A & (1<<UDRE3)) );
	UDR3 = a;
}

char usart_recv()
{
	while ( !(UCSR3A & (1<<RXC3)) );
	return UDR3;
}

void analog_init()
{
	// ADC clock set to 1MHz
	//ADCSRA |= (1<<ADPS2);
	//ADCSRA &= ~(1<<ADPS1);
	//ADCSRA &= ~(1<<ADPS0);
	// ADC clock set to 125KHz
	ADCSRA |= (1<<ADPS2);
	ADCSRA |= (1<<ADPS1);
	ADCSRA |= (1<<ADPS0);
	ADCSRA |= (1<<ADEN);
	// first conversion takes the longest
	ADCSRA |= (1<<ADSC);
}

int16_t analog_read(int pin)
{
	uint8_t h, l;
	ADCSRB = (ADCSRB & ~(1 << MUX5)) | (((pin >> 3) & 0x01) << MUX5);
	ADMUX = (0x01 << 6) | (pin & 0x07);	
	
	ADCSRA |= (1<<ADSC);

	// ADSC is cleared when the conversion finishes
	while (ADCSRA&(1<<ADSC));

	l = ADCL;
	h = ADCH;

	// combine the two bytes
	return (h << 8) | l;
}


int32_t measure_pulse_us(volatile uint8_t *port, uint8_t pin, uint8_t state, uint32_t time_left)
{
	uint32_t initial, ending;
	uint8_t mask;
	mask = (1<<pin);
	state <<= pin;
	while (((*port)&mask) == state && time_left)
		time_left--;
	while (((*port)&mask) != state && time_left)
		time_left--;
	initial = (uint32_t)xTaskGetTickCount()*1000+(TCNT1>>1);
	//initial = (uint32_t)xTaskGetTickCount()*1000+(TCNT0*4);
	while (((*port)&mask) == state && time_left)
		time_left--;
	ending = (uint32_t)xTaskGetTickCount()*1000+(TCNT1>>1);
	//ending = (uint32_t)xTaskGetTickCount()*1000+(TCNT0*4);
	if (time_left) 
	{
		if (ending < initial)
			ending += 0x3E80000;
		return ending - initial;
	}
	return 0;
}

void delayus(unsigned int us)
{
	if (us <= 1) return; //  = 3 cycles, (4 when true)

	// the following loop takes 1/4 of a microsecond (4 cycles)
	// per iteration, so execute it four times for each microsecond of
	// delay requested.
	us <<= 2; // x4 us, = 4 cycles

	// account for the time taken in the preceeding commands.
	// we just burned 19 (21) cycles above, remove 5, (5*4=20)
	// us is at least 8 so we can substract 5
	us -= 5; // = 2 cycles,
	
	__asm__ __volatile__ (
	"1: sbiw %0,1" "\n\t" // 2 cycles
	"brne 1b" : "=w" (us) : "0" (us) // 2 cycles
	);
	//uint32_t final;
	//final = xTaskGetTickCount()*1000+TCNT0*4+delta;
	//while ((xTaskGetTickCount()*1000+TCNT0*4) < final);
}

void debug_init(unsigned long baud)
{
	//unsigned int ubrr = (F_CPU/4/baud-1)/2;
	unsigned int ubrr = F_CPU/8/baud - 1;
	
	UCSR0A = 1<<U2X0;
	/* Set baud rate */
	UBRR0H = (unsigned char)(ubrr>>8);
	UBRR0L = (unsigned char)ubrr;
	/* Enable receiver and transmitter */
	UCSR0B = (1<<RXEN0)|(1<<TXEN0);
	/* Set frame format: 8data, 1stop bit */
	UCSR0C = (3<<UCSZ00);//(1<<USBS0)| 2 stopbit
}

void debug_send(char a)
{
	while ( !( UCSR0A & (1<<UDRE0)) );
	UDR0 = a;
}

char debug_recv()
{
	while ( !(UCSR0A & (1<<RXC0)) );
	return UDR0;
}



/*
const uint8_t PROGMEM digital_pin_to_port_PGM[] = {
	// PORTLIST
	// -------------------------------------------
	PE	, // PE 0 ** 0 ** USART0_RX
	PE	, // PE 1 ** 1 ** USART0_TX
	PE	, // PE 4 ** 2 ** PWM2
	PE	, // PE 5 ** 3 ** PWM3
	PG	, // PG 5 ** 4 ** PWM4
	PE	, // PE 3 ** 5 ** PWM5
	PH	, // PH 3 ** 6 ** PWM6
	PH	, // PH 4 ** 7 ** PWM7
	PH	, // PH 5 ** 8 ** PWM8
	PH	, // PH 6 ** 9 ** PWM9
	PB	, // PB 4 ** 10 ** PWM10
	PB	, // PB 5 ** 11 ** PWM11
	PB	, // PB 6 ** 12 ** PWM12
	PB	, // PB 7 ** 13 ** PWM13
	PJ	, // PJ 1 ** 14 ** USART3_TX
	PJ	, // PJ 0 ** 15 ** USART3_RX
	PH	, // PH 1 ** 16 ** USART2_TX
	PH	, // PH 0 ** 17 ** USART2_RX
	PD	, // PD 3 ** 18 ** USART1_TX
	PD	, // PD 2 ** 19 ** USART1_RX
	PD	, // PD 1 ** 20 ** I2C_SDA  
	PD	, // PD 0 ** 21 ** I2C_SCL
	PA	, // PA 0 ** 22 ** D22
	PA	, // PA 1 ** 23 ** D23
	PA	, // PA 2 ** 24 ** D24
	PA	, // PA 3 ** 25 ** D25
	PA	, // PA 4 ** 26 ** D26
	PA	, // PA 5 ** 27 ** D27
	PA	, // PA 6 ** 28 ** D28
	PA	, // PA 7 ** 29 ** D29
	PC	, // PC 7 ** 30 ** D30
	PC	, // PC 6 ** 31 ** D31
	PC	, // PC 5 ** 32 ** D32
	PC	, // PC 4 ** 33 ** D33
	PC	, // PC 3 ** 34 ** D34 
	PC	, // PC 2 ** 35 ** D35
	PC	, // PC 1 ** 36 ** D36
	PC	, // PC 0 ** 37 ** D37
	PD	, // PD 7 ** 38 ** D38
	PG	, // PG 2 ** 39 ** D39
	PG	, // PG 1 ** 40 ** D40
	PG	, // PG 0 ** 41 ** D41
	PL	, // PL 7 ** 42 ** D42
	PL	, // PL 6 ** 43 ** D43
	PL	, // PL 5 ** 44 ** D44
	PL	, // PL 4 ** 45 ** D45
	PL	, // PL 3 ** 46 ** D46
	PL	, // PL 2 ** 47 ** D47
	PL	, // PL 1 ** 48 ** D48
	PL	, // PL 0 ** 49 ** D49
	PB	, // PB 3 ** 50 ** SPI_MISO
	PB	, // PB 2 ** 51 ** SPI_MOSI
	PB	, // PB 1 ** 52 ** SPI_SCK
	PB	, // PB 0 ** 53 ** SPI_SS
	PF	, // PF 0 ** 54 ** A0
	PF	, // PF 1 ** 55 ** A1
	PF	, // PF 2 ** 56 ** A2
	PF	, // PF 3 ** 57 ** A3
	PF	, // PF 4 ** 58 ** A4
	PF	, // PF 5 ** 59 ** A5
	PF	, // PF 6 ** 60 ** A6
	PF	, // PF 7 ** 61 ** A7
	PK	, // PK 0 ** 62 ** A8
	PK	, // PK 1 ** 63 ** A9
	PK	, // PK 2 ** 64 ** A10
	PK	, // PK 3 ** 65 ** A11
	PK	, // PK 4 ** 66 ** A12
	PK	, // PK 5 ** 67 ** A13
	PK	, // PK 6 ** 68 ** A14
	PK	, // PK 7 ** 69 ** A15
};
*/