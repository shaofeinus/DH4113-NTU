/*
 * PulseWidth.h
 *
 * Created: 27/9/2015 04:12:03
 *  Author: Kaya
 */ 


#ifndef PULSEWIDTH_H_
#define PULSEWIDTH_H_


void pulse_init();

void pulse_read(char pin, SemaphoreHandle_t semaphore, int32_t* address);

void pulse_stop(char pin);


#endif /* PULSEWIDTH_H_ */