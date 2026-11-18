#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button, Color, Port
from pybricks.tools import wait
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor

# Initialize the EV3 Brick
ev3 = EV3Brick()
colors_sensor = ColorSensor(Port.S1)
motor_left = Motor(Port.A)
motor_right = Motor(Port.D)
gyro_sensor = GyroSensor(Port.S2)


# 1. Custom Enum Implementation
# Since MicroPython does not support the standard Enum type, we use a class with constant attributes.
class ParcoursAbschnitt:
    PROGRAMM_ANGEHALTEN = 0
    HAUPTMENU = 1
    LINIENFOLGEN = 2
    FARBFELDSUCHE = 3
    ZYLINDER = 4
    BRUECKE = 5


def run_hauptmenu():
    """
    Displays the menu to manually select the entry point for the course.
    """
    ev3.screen.clear()
    ev3.screen.print("HAUPTMENUE")
    ev3.screen.print("UP: Linienfolgen")
    ev3.screen.print("DOWN: Farbfeld")
    ev3.screen.print("ENTER: Beenden")

    while True:
        pressed = ev3.buttons.pressed()

        # Pressing Enter in the main menu stops the program (Programm angehalten).
        if Button.CENTER in pressed:
            return ParcoursAbschnitt.PROGRAMM_ANGEHALTEN

        # Selecting routines via menu[cite: 3].
        elif Button.UP in pressed:
            run_linienfolgen()
        elif Button.DOWN in pressed:
            return ParcoursAbschnitt.FARBFELDSUCHE

        wait(100)


def run_linienfolgen():
    """
    Routine for line following[cite: 2].
    """
    ev3.screen.clear()
    # Output the current section to the screen for testing purposes[cite: 3].
    ev3.screen.print("STATE: Linienfolgen")
    ev3.screen.print("Warte auf Band...")

    start_gyro_angle = gyro_sensor.angle()

    while True:
        pressed = ev3.buttons.pressed()

        # Exit the routine and return to the main menu via button press[cite: 3].
        if Button.LEFT in pressed or Button.RIGHT in pressed:  # Assuming Left/Right act as 'Menu buttons'
            return ParcoursAbschnitt.HAUPTMENU

        red, green, blue = colors_sensor.rgb()
        reflection = colors_sensor.reflection()

        while reflection > 60:  # Assuming a threshold for detecting the line
            ev3.screen.print("Line detected!" + str(reflection))
            motor_left.run(100)  # Run left motor at 100 deg/s
            motor_right.run(100)  # Run right motor at 100 deg/s
            reflection = colors_sensor.reflection()
            start_gyro_angle = gyro_sensor.angle()

        while reflection <= 60:
            ev3.screen.print("Line lost!" + str(reflection))
            motor_left.run(-50)
            motor_right.run(50)
            reflection = colors_sensor.reflection()
            gyro_angle = gyro_sensor.angle()

            if gyro_angle < start_gyro_angle - 10:
                while gyro_angle < start_gyro_angle + 10 and reflection <= 70:
                    motor_left.run(50)
                    motor_right.run(-50)
                    reflection = colors_sensor.reflection()
                    gyro_angle = gyro_sensor.angle()
                
            if gyro_angle < start_gyro_angle - 10 and reflection <= 70:
                while reflection <= 70 and gyro_sensor.angle() < start_gyro_angle + 90:
                    motor_left.run(0)
                    motor_right.run(-50)
                    reflection = colors_sensor.reflection()

                motor_left.run(0)
                motor_right.run(0)
                if gyro_sensor.angle() > start_gyro_angle + 90:
                    while gyro_sensor.angle() > start_gyro_angle:
                        motor_left.run(-50)
                        motor_right.run(0)

        wait(100)


def run_farbfeldsuche():
    """
    Routine for color field search[cite: 2].
    """
    ev3.screen.clear()
    ev3.screen.print("STATE: Farbfeld")

    while True:
        pressed = ev3.buttons.pressed()

        # Cancel execution and return to main menu.
        if Button.LEFT in pressed or Button.RIGHT in pressed:
            return ParcoursAbschnitt.HAUPTMENU

        wait(100)


# 2. Main Framework Loop
def main():
    # A variable holds the current section of the course[cite: 3].
    current_state = ParcoursAbschnitt.LINIENFOLGEN

    # The framework runs in a while loop that can be manually terminated[cite: 3].
    while current_state != ParcoursAbschnitt.PROGRAMM_ANGEHALTEN:

        if current_state == ParcoursAbschnitt.HAUPTMENU:
            current_state = run_hauptmenu()

        elif current_state == ParcoursAbschnitt.LINIENFOLGEN:
            current_state = run_linienfolgen()

        elif current_state == ParcoursAbschnitt.FARBFELDSUCHE:
            current_state = run_farbfeldsuche()

        # A new section can be easily integrated here by adding an elif block[cite: 2].
        elif current_state == ParcoursAbschnitt.ZYLINDER:
            pass

        wait(50)

    ev3.screen.clear()
    ev3.screen.print("Programm beendet.")


if __name__ == "__main__":
    main()
