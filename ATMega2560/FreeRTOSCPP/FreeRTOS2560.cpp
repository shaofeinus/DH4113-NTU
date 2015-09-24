/*
*
freertos2560.c
*
*/
#include <avr/io.h>
#include <FreeRTOS.h>
#include <task.h>
#include <semphr.h>
#include <stdio.h>
#include <stdlib.h>

#include "AltIMUv4.h"
#include "i2c.h"

SemaphoreHandle_t a_updated, m_updated, ir_updated, us_updated;
int16_t a_x, a_y, a_z, m_x, m_y, m_z;
uint16_t ir_dist, us_dist;
uint16_t a_last_update, m_last_update, ir_last_update, us_last_update;

//extern uint32_t countPulseASM(volatile uint8_t *port, uint8_t bit, uint8_t stateMask, unsigned long maxloops) __asm__("countPulseASM");

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

int16_t measure_pulse_us(volatile uint8_t *port, uint8_t pin, uint8_t state);

enum deviceId
{
	ACCEL		= 0x10,	// 1
	COMPASS		= 0x20,	// 2
	
	IR			= 0x80,	// 8
	US			= 0x90	// 9
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
	/*#define print_number(x) itoa(x, report, 10); \
							for (i = 0; report[i] != 0; ++i) \
								usart_send(report[i]);
	#define print_unumber(x)	utoa(x, report, 10); \
								for (i = 0; report[i] != 0; ++i) \
									usart_send(report[i]);
	
	char report[16];
	int i;*/
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
		
		if (xSemaphoreTake(ir_updated, 0) == pdTRUE)
		{
			data[0] = ir_dist>>8;
			data[1] = ir_dist;
			send_data(IR, ir_last_update, data, 2);
		}
		
		if (xSemaphoreTake(us_updated, 0) == pdTRUE)
		{
			data[0] = us_dist>>8;
			data[1] = us_dist;
			send_data(US, us_last_update, data, 2);
		}
		
		/*data = usart_recv();
		usart_send(data);*/
		/*if( xSemaphoreTake( xUpdated, 10 ) == pdTRUE )
		{
			usart_send('a');
			usart_send(':');
			usart_send(' ');
			print_number(a_x);
			usart_send(' ');
			print_number(a_y);
			usart_send(' ');
			print_number(a_z);
			usart_send(' ');
			usart_send('m');
			usart_send(':');
			usart_send(' ');
			print_number(m_x);
			usart_send(' ');
			print_number(m_y);
			usart_send(' ');
			print_number(m_z);
			usart_send(' ');
			usart_send('d');
			usart_send(':');
			usart_send(' ');
			print_unumber(ir_dist);
			usart_send(' ');
			print_unumber(us_dist);
			usart_send('\r');
			usart_send('\n');
			vTaskDelay(1000);
		}*/
	}
}

void twowire_process(void *p)
{
	twi_init();
	lsm303_init();
	while(1)
	{
		lsm303_read_acc(&a_x, &a_y, &a_z);
		a_last_update = xTaskGetTickCount();
		xSemaphoreGive( a_updated );
		lsm303_read_mag(&m_x, &m_y, &m_z);
		m_last_update = xTaskGetTickCount();
		xSemaphoreGive( m_updated );
		vTaskDelay(10);
	}
}

void distir_process(void *p)
{
	analog_init();
	while(1)
	{
		ir_dist = analog_read(0);
		ir_last_update = xTaskGetTickCount();
		xSemaphoreGive( ir_updated );
		vTaskDelay(100);
	}
}

void distultrasound_process(void *p)
{
	// PA 0 ** 22 ** D22 ECHO input 0
	// PA 1 ** 23 ** D23 TRIG output 1
	DDRA &= ~(1<<PA0);
	DDRA |= (1<<PA1);
	while(1)
	{
		PORTA &= ~(1<<PA1);
		delayus(2);
		PORTA |= (1<<PA1);
		delayus(10);
		PORTA &= ~(1<<PA1);
		us_dist = measure_pulse_us((volatile uint8_t *)&PINA, PA0, 1);
		us_last_update = xTaskGetTickCount();
		xSemaphoreGive( us_updated );
		vTaskDelay(100-(us_dist>>10));
	}
}


#define STACK_DEPTH 64

void vApplicationIdleHook()
{
	// Do nothing.
}

int main(void)
{
	usart_init(115200);
	usart_send('s');
	usart_send('\r');
	usart_send('\n');
	a_updated = xSemaphoreCreateBinary();
	m_updated = xSemaphoreCreateBinary();
	ir_updated = xSemaphoreCreateBinary();
	us_updated = xSemaphoreCreateBinary();
	
	TaskHandle_t t1, t2, t3, t4;
	//	Create tasks 
	xTaskCreate(usart_process, "usart", STACK_DEPTH, NULL, 1, &t1);
	xTaskCreate(twowire_process, "twowire", STACK_DEPTH, NULL, 2, &t2);
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
	ADCSRA = (1<<ADEN);
}

int16_t analog_read(int pin)
{
	uint8_t h, l;
	ADCSRB = (ADCSRB & ~(1 << MUX5)) | (((pin >> 3) & 0x01) << MUX5);
	ADMUX = (0x01 << 6) | (pin & 0x07);	
	ADCSRA |= (1<<ADSC);

	// ADSC is cleared when the conversion finishes
	while (ADCSRA&(1<<ADSC));

	l  = ADCL;
	h = ADCH;

	// combine the two bytes
	return (h << 8) | l;
}

uint32_t loops, initial, final;
uint8_t mask;

int16_t measure_pulse_us(volatile uint8_t *port, uint8_t pin, uint8_t state)
{
	/*uint8_t stateMask = (state ? 1<<pin : 0);

	// convert the timeout from microseconds to a number of times through
	// the initial loop; it takes approximately 16 clock cycles per iteration
	#define clockCyclesPerMicrosecond() ( F_CPU / 1000000L )
	#define clockCyclesToMicroseconds(a) ( (a) / clockCyclesPerMicrosecond() )
	#define microsecondsToClockCycles(a) ( (a) * clockCyclesPerMicrosecond() )
	unsigned long maxloops = microsecondsToClockCycles(0x7FFF)/16;

	unsigned long width = countPulseASM(port, 1<<pin, stateMask, maxloops);

	// prevent clockCyclesToMicroseconds to return bogus values if countPulseASM timed out
	if (width)
		return clockCyclesToMicroseconds(width * 16 + 16);*/
	mask = (1<<pin);
	state <<= pin;
	while (((*port)&mask) == state);
	while (((*port)&mask) != state);
	initial = xTaskGetTickCount()*1000+(TCNT1>>1);
	//initial = xTaskGetTickCount()*1000+(TCNT0*4);
	while (((*port)&mask) == state);
	final = xTaskGetTickCount()*1000+(TCNT1>>1);
	//final = xTaskGetTickCount()*1000+(TCNT0*4);
	return final - initial;
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