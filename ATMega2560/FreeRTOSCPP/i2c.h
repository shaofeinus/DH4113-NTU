/*
 * twi.h
 *
 * Created: 16/9/2015 11:07:18
 *  Author: Kaya
 */ 


#ifndef TWI_H_
#define TWI_H_

void twi_set_frequency(uint32_t frequency);
int twi_start();
int twi_stop();
int twi_send_address(char address);
int twi_send_data(char);
int twi_read_data(char *data, char ack);

#endif /* TWI_H_ */