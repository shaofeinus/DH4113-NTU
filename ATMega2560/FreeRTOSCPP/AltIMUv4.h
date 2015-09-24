/*
 * AltIMUv4.h
 *
 * Created: 16/9/2015 13:13:23
 *  Author: Kaya
 */ 


#ifndef ALTIMUV4_H_
#define ALTIMUV4_H_


void lsm303_init();
void lsm303_read_acc(int16_t *x, int16_t *y, int16_t *z);
void lsm303_read_mag(int16_t *x, int16_t *y, int16_t *z);


#endif /* ALTIMUV4_H_ */