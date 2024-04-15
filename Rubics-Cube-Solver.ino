#define MOTOR_DOWN_STEP 4
#define MOTOR_DOWN_DIR 5
#define MOTOR_LEFT_STEP 11
#define MOTOR_LEFT_DIR 10
#define MOTOR_RIGHT_STEP 7
#define MOTOR_RIGHT_DIR 6
#define MOTOR_FRONT_STEP 3
#define MOTOR_FRONT_DIR 2
#define MOTOR_BACK_STEP 9
#define MOTOR_BACK_DIR 8

#define MOTOR_ENABLE 2

void turnMotorQuarter(int motorStep, int motorDir, bool clockwise)
{
    if (clockwise)
    {
        digitalWrite(motorDir, HIGH);
    }
    else
    {
        digitalWrite(motorDir, LOW);
    }
    for (int i = 0; i < 50; i++)
    {
        digitalWrite(motorStep, HIGH);
        delayMicroseconds(1500);
        digitalWrite(motorStep, LOW);
        delayMicroseconds(15000);
    }
    delay(500);
}

void setup()
{
    Serial.begin(9600);
    pinMode(MOTOR_DOWN_STEP, OUTPUT);
    pinMode(MOTOR_DOWN_DIR, OUTPUT);
    pinMode(MOTOR_LEFT_STEP, OUTPUT);
    pinMode(MOTOR_LEFT_DIR, OUTPUT);
    pinMode(MOTOR_RIGHT_STEP, OUTPUT);
    pinMode(MOTOR_RIGHT_DIR, OUTPUT);
    pinMode(MOTOR_FRONT_STEP, OUTPUT);
    pinMode(MOTOR_FRONT_DIR, OUTPUT);
    pinMode(MOTOR_BACK_STEP, OUTPUT);
    pinMode(MOTOR_BACK_DIR, OUTPUT);
    pinMode(MOTOR_ENABLE, OUTPUT);
    digitalWrite(MOTOR_ENABLE, HIGH);
}

void loop()
{
    if (Serial.available())
    {
        char read_Byte = Serial.read();
        switch (read_Byte)
        {
        // // anschalten
        // case 'a':
        //     digitalWrite(MOTOR_ENABLE, HIGH);
        //     break;
        // // ausschalten
        // case 'A':
        //     digitalWrite(MOTOR_ENABLE, LOW);
        //     break;
        // D
        case 'D':
            turnMotorQuarter(MOTOR_DOWN_STEP, MOTOR_DOWN_DIR, true);
            Serial.write("o");
            break;
        // D'
        case 'd':
            turnMotorQuarter(MOTOR_DOWN_STEP, MOTOR_DOWN_DIR, false);
            Serial.write("o");
            break;
        // L
        case 'L':
            turnMotorQuarter(MOTOR_LEFT_STEP, MOTOR_LEFT_DIR, true);
            Serial.write("o");
            break;
        // L'
        case 'l':
            turnMotorQuarter(MOTOR_LEFT_STEP, MOTOR_LEFT_DIR, false);
            Serial.write("o");
            break;
        // R
        case 'R':
            turnMotorQuarter(MOTOR_RIGHT_STEP, MOTOR_RIGHT_DIR, true);
            Serial.write("o");
            break;
        // R'
        case 'r':
            turnMotorQuarter(MOTOR_RIGHT_STEP, MOTOR_RIGHT_DIR, false);
            Serial.write("o");
            break;
        // F
        case 'F':
            turnMotorQuarter(MOTOR_FRONT_STEP, MOTOR_FRONT_DIR, true);
            Serial.write("o");
            break;
        // F'
        case 'f':
            turnMotorQuarter(MOTOR_FRONT_STEP, MOTOR_FRONT_DIR, false);
            Serial.write("o");
            break;
        // B
        case 'B':
            turnMotorQuarter(MOTOR_BACK_STEP, MOTOR_BACK_DIR, true);
            Serial.write("o");
            break;
        // B'
        case 'b':
            turnMotorQuarter(MOTOR_BACK_STEP, MOTOR_BACK_DIR, false);
            Serial.write("o");
            break;
        }
    }
}