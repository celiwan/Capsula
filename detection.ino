
//Detection
float detector = A0; //Assigning detector to A0
float readDetector;
float DelayDetect = 1; // Timer of detection in milliseconds
float microDelayDetect = 0.001; // Value to add to the current time for next timepoint
float DataTime = 0.000000; // Initialization of time


void dataFile() {
  Serial.print(DataTime, 8); // print time
  Serial.print('\t');
  readDetector = float(analogRead(detector));
  Serial.println((readDetector*5)/1023,8); // print voltage & analog-numeric conversion
  DataTime += microDelayDetect;
  delay(DelayDetect);
}

void setup() {
  pinMode(detector, INPUT); // Setting PDA10 (A0) input
  Serial.begin(250000); // Initialization of serial port
}

byte varCompteur = 0; // La variable compteur

void loop() {
  dataFile();
}



