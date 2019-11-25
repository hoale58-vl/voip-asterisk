#include <stdio.h>
#include <wiringPi.h>

int main (void)
{
  int i = 0;

//   int listGpio[8] = {11, 10, 14, 6, 13, 12, 5, 4};
  int listGpio[8] = {3, 2, 1, 0, 16, 15, 7, 9};

  wiringPiSetup () ;

  for (i=0; i<26; i++)
  	pinMode (i, OUTPUT) ;
    for (i=0; i<8; i++){
        printf("Reset\n");
        digitalWrite (listGpio[i], HIGH) ;
    }

    for (;;)
    {
        for (i=0; i<8; i++){
            digitalWrite (listGpio[i], LOW) ;	
            delay(500);
        }
        
        for (i=0; i<8; i++){
            digitalWrite (listGpio[i], HIGH) ;
            delay(500);	// Off
        }

        
        
    }
    

    // for (;;)
    // {
    //     for (i=0; i<9; i++){
    //         printf("Reset\n");
    //         digitalWrite (i, HIGH) ;
    //     }

    //         delay(5000);	// Off
        
    //     for (i=0; i<9; i++){
    //         printf("Reset\n");
    //         digitalWrite (i, LOW) ;	
    //     }
    //     delay(5000);
    // }
    
}