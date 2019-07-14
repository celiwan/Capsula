#include <DueTimer.h>

float PDA10A=A0;//Assigning PDA10A detector to A0
float timeElapsedus = 0.0;


void dataPrint(){
  
  Serial.println((analogRead(A0)*5.0)/4095.0,12); // print voltage & analog-numeric conversion
  Serial.println(timeElapsedus,12);
  timeElapsedus+=0.0002;
  Serial.flush();
  
}

void setup() {
  Serial.begin(115200);
  pinMode(PDA10A,INPUT); // Setting PDA10 (A0) input.
  analogReadResolution(12);
  Timer3.attachInterrupt(dataPrint);
  Timer3.start(200);
}


void loop() {
    while(1){
      
    }
}
