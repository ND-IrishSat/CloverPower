// i2c_utils.h
#ifndef I2C_UTILS_H
#define I2C_UTILS_H

#include <stdio.h>

// External declaration of file descriptor
extern int i2c_fd;

// Function prototypes
int read_register_data(int reg_addr, int length, unsigned char *data);
void display_data();

#endif