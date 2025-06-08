#ifdef USE_BASE

#ifdef POLOLU_VNH5019
  // Them thu vien Pololu VNH5019
  #include "DualVNH5019MotorShield.h"

  // Tao doi tuong dieu khien dong co
  DualVNH5019MotorShield drive;

  // Ham khoi tao driver dong co
  void initMotorController() {
    drive.init();
  }

  // Ham dat toc do cho mot dong co
  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) drive.setM1Speed(spd);
    else drive.setM2Speed(spd);
  }

  // Ham tien loi dat toc do cho ca hai dong co
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#elif defined POLOLU_MC33926
  // Them thu vien Pololu MC33926
  #include "DualMC33926MotorShield.h"

  // Tao doi tuong dieu khien dong co
  DualMC33926MotorShield drive;

  // Ham khoi tao driver dong co
  void initMotorController() {
    drive.init();
  }

  // Ham dat toc do cho mot dong co
  void setMotorSpeed(int i, int spd) {
    if (i == LEFT) drive.setM1Speed(spd);
    else drive.setM2Speed(spd);
  }

  // Ham tien loi dat toc do cho ca hai dong co
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#elif defined L298_MOTOR_DRIVER
  // Ham khoi tao driver L298
  void initMotorController() {
    digitalWrite(RIGHT_MOTOR_ENABLE, HIGH);
    digitalWrite(LEFT_MOTOR_ENABLE, HIGH);
  }

  // Ham dat toc do va chieu quay cho mot dong co
  void setMotorSpeed(int i, int spd) {
    unsigned char reverse = 0;

    if (spd < 0)
    {
      spd = -spd;
      reverse = 1;
    }
    if (spd > 255)
      spd = 255;

    if (i == LEFT) {
      if      (reverse == 0) { analogWrite(LEFT_MOTOR_FORWARD, spd); analogWrite(LEFT_MOTOR_BACKWARD, 0); }
      else if (reverse == 1) { analogWrite(LEFT_MOTOR_BACKWARD, spd); analogWrite(LEFT_MOTOR_FORWARD, 0); }
    }
    else { // RIGHT
      if      (reverse == 0) { analogWrite(RIGHT_MOTOR_FORWARD, spd); analogWrite(RIGHT_MOTOR_BACKWARD, 0); }
      else if (reverse == 1) { analogWrite(RIGHT_MOTOR_BACKWARD, spd); analogWrite(RIGHT_MOTOR_FORWARD, 0); }
    }
  }

  // Ham tien loi dat toc do cho ca hai dong co
  void setMotorSpeeds(int leftSpeed, int rightSpeed) {
    setMotorSpeed(LEFT, leftSpeed);
    setMotorSpeed(RIGHT, rightSpeed);
  }
#else
  // Bao loi neu chua chon driver dong co
  #error A motor driver must be selected!
#endif

#endif