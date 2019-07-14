float PDA10A=A0;//Assigning PDA10A detector to A0
float readPDA10A;//Declaring our readPDA10A variable
void setup() {
  pinMode(PDA10A,INPUT); // Setting PDA10 (A0) input.

}
void loop() {
  Serial.begin(115200);
  if (Serial.available()>0) {
    readPDA10A=float(analogRead(PDA10A)); //read the value on PDA10A
    Serial.println((readPDA10A*5.0)/1023.0,4); // print voltage & analog-numeric conversion
    Serial.end();
  }
}
