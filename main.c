#include <stdio.h>
#include <wiringPi.h>
#include <stdlib.h>
#include <unistd.h>
#include "Yul_LCD.h"
#define button_gpio 7  //gpio 4
#define led_gpio 0  //gpio 17

int flagl = 0;

void workMotor(){
   system("python ./motor");
}

void takePhoto(){//파이 카메라
    system("./photo.sh yf1");
}

int scanButton (int btn_scan){
    if(digitalRead (btn_scan== HIGH)){ // Low is pushed
            return 1; }
            
    
    flagl ^= 1;
    digitalWrite(led_gpio, flagl);
   // takePhoto();
    workMotor();
    while(digitalRead (btn_scan) == LOW){
     delay(10);
    }
       
    return 1;
    }   

int  start (int num)
{
    int button_flag = 0;
    int lcd_flag;
    printf ("param %d \n",num);
    if (wiringPiSetup () == -1)
        return 1;
   
    pinMode (led_gpio, OUTPUT);
    digitalWrite(led_gpio, 0);

    pinMode (button_gpio, INPUT);
    pullUpDnControl (button_gpio, PUD_UP);

    scanButton(button_flag);
    lcd_flag=num;
    switch(lcd_flag){
        case 1:
            lcdOn_nowstat(lcd_flag);
            break;
        case 2:
            lcdOn_nowstat(lcd_flag);
            break;
        case 3:
            lcdOn_feedstat(lcd_flag);
            break;
    }
    delay(1);

    return 0;
}

int main (int argc, char *argv[]){

    int num = atoi(argv[1]);
    start(num);
    return 1;

}

