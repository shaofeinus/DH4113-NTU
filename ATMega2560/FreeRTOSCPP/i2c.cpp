#include <avr/io.h>

#define START				0x08
#define REPEATED_START		0x10
#define MT_SLA_ACK			0x18
#define MT_SLA_NACK			0x20
#define MT_DATA_ACK			0x28
#define MT_DATA_NACK		0x30
#define M_ARBLOST			0x38
#define MR_SLA_ACK			0x40
#define MR_SLA_NACK			0x48
#define MR_DATA_ACK			0x50
#define MR_DATA_NACK		0x58

void twi_set_frequency(uint32_t frequency)
{
	TWSR &= 0xFC;
	TWBR = ((F_CPU / frequency) - 16) / 2;
}

int twi_start()
{
	TWCR = (1<<TWINT)|(1<<TWSTA)|(1<<TWEN);
	while (!(TWCR & (1<<TWINT)));
	if ((TWSR&0xF8) != START)
		return -1;
	return 0;
}

int twi_stop()
{
	TWCR = (1<<TWINT)|(1<<TWEN)|(1<<TWSTO);
	return 0;
}

int twi_send_address(char address)
{
	TWDR = address;
	TWCR = (1<<TWINT)|(1<<TWEN);
	while (!(TWCR & (1<<TWINT)));
	return TWSR&0xF8;
	if ((TWSR&0xF8) != MT_SLA_ACK)
		return -1;
	return 0;
}

int twi_send_data(char data)
{
	TWDR = data;
	TWCR = (1<<TWINT)|(1<<TWEN);
	while (!(TWCR & (1<<TWINT)));
	if ((TWSR&0xF8) != MT_DATA_ACK)
		return -1;
	return 0;
}

int twi_read_data(char *data, char ack)
{
	if (ack)
	{
		TWCR = (1<<TWINT)|(1<<TWEN)|(1<<TWEA);
	}
	else
	{
		TWCR = (1<<TWINT)|(1<<TWEN);
	}
	while (!(TWCR & (1<<TWINT)));
	*data = TWDR;
	if ((TWSR&0xF8) != MR_DATA_ACK)
		return -1;
	return 0;
}
