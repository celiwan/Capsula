const int pwm_pump = 3; // la PWM de la pompe
const int pwm_motor = 9; // la PWM du moteur
const int direction_pump = 2; // la broche sens de la pompe
const int direction_motor = 8; // la broche sens du moteur
//const int brake_pump = 9; // la broche frein de la pompe
//onst int brake_motor = 8; // la broche frein du moteur
int dutycycle_pump = 0; // initialisation pwm pompe
int dutycycle_motor = 0; // initialisation pwm moteur
int state_d_pump = 0; // initialisation direction pompe
int state_d_motor = 0; // initialisation direction moteur
int value = 0; // la valeur qui sera reçu du Raspebrry
int actual_value_pump = 1; // valeur test de changement de duty cycle pour la pompe
int actual_value_motor = 1; // valeur test de changement de duty cycle pour le moteur
// Il est important d'initialiser ces valeurs à 0 pour rentrer dans le premier "if"
void setup() 
{
  pinMode(pwm_pump, OUTPUT);
  pinMode(pwm_motor, OUTPUT);
  pinMode(direction_pump, OUTPUT);
  pinMode(direction_motor, OUTPUT);
  //pinMode(brake_pump, OUTPUT);
  //pinMode(brake_motor, OUTPUT);
  Serial.begin(9600);
}
  

void loop()
{ 
  if (Serial.available())  {
    value = Serial.parseInt();  // on soustrait le caractère 0, qui vaut 48 en ASCII
    if (value>=1000 && value <=1100 && value!=actual_value_pump)
    {
      dutycycle_pump=value*255/100;
      //analogWrite(pwm_pump, dutycycle_pump);
      actual_value_pump = value;
      // on stocke la valeur actuelle du duty cycle 
      // pour ne refaire cette condition que si elle a été changée
    }
    if (value>=0 && value <=100 && value!=actual_value_motor) 
    {
      dutycycle_motor=(value*255)/100;
      //analogWrite(pwm_motor, dutycycle_motor);
      actual_value_motor = value; 
      // on stocke la valeur actuelle du duty cycle 
      // pour ne refaire cette condition que si elle a été changée
    }
    if (value==200) 
    {
      digitalWrite(direction_motor, (state_d_motor) ? HIGH:LOW);
      state_d_motor = !state_d_motor;
    }
    if (value==1200) 
    {
      digitalWrite(direction_pump, (state_d_pump) ? HIGH:LOW);
      state_d_pump = !state_d_pump;
    }
    if (value==300) 
    {
      digitalWrite(direction_motor, HIGH);
      analogWrite(pwm_motor,255);
      delay(5000);
      digitalWrite(direction_motor, LOW);
      delay(5000);
      analogWrite(pwm_motor,0);      
    }
    if (value==1300) 
    {
      digitalWrite(direction_pump, HIGH);
      analogWrite(pwm_pump,255);
      delay(5000);
      digitalWrite(direction_pump, LOW);
      delay(5000);
      analogWrite(pwm_pump,0);      
    }
    if (value==400) analogWrite(pwm_motor, dutycycle_motor);
    if (value==1400) analogWrite(pwm_pump, dutycycle_pump);
    if (value==500) analogWrite(pwm_motor, 0);
    if (value==1500) analogWrite(pwm_pump, 0);
    //if (value==600) digitalWrite(brake_motor, HIGH);
    //if (value==601) digitalWrite(brake_motor, LOW);
    //if (value==1600) digitalWrite(brake_pump, HIGH);
    //if (value==1601) digitalWrite(brake_pump, LOW);
    Serial.flush();   
  }
}
         

