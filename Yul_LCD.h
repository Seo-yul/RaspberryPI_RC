#ifndef Yul_LCD_H
#define Yul_LCD_H

#include <stdio.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <string.h>
#include <time.h>

void write_word(int data);
void send_command(int comm);
void send_data(int data);
void init();
void clear();
void writeL(int x, int y, char data[]);
char * checkServed(int flag);
int lcdOn_nowstat(int num);
int lcdOn_feedstat(int num);





#endif
