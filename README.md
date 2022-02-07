# OctoPrint-Servospindle

Servo Spindle enables you to control a "servo" (typically an Electronic Speed Controller) triggered off of GRBL
gcode commands sent to your CNC machine and the status the machine reports for spindle mode and spindle speed.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/synman/OctoPrint-Servospindle/archive/master.zip

The ideal setup for this plugin is using hardware based PWM timing on GPIO 18, 19, 12, or 13.  This facilitated by use of the **rpi-hardware-pwm** library that provides a simple implementation for interacting directly with your CPU's timing clock.  This enables precise hardware based pulse width modulation which is critical when controlling an electronic speed control.  

Follow the (simple) procedure documented for **rpi-hardware-pwm** to properly configure it here:  https://github.com/Pioreactor/rpi_hardware_pwm#installation

Initial tests were reasonable with **gpiozero** and **pigpio** but I noticed a rare "jitter" that just isn't something I can tolerate when running a CNC spindle at 15,000+ RPM.  If you do decide to go the software PWM timing route, it is fully supported, but buyers beware.  You'll need **pigpiod** installed somewhere accessible to your Octoprint server.  It can be running on the same machine as Octoprint or it can be installed on a remote computer (which is pretty nifty).

All dependent client **gpiozero**, **pigpio**, **rpi-hardware-pwm** python libraries are installed automatically with Servo Spindle.  

## Configuration

There is no Plugin Settings UI at this time but this plugin is fully configurable via Octoprint's config.yaml file.

### Default Settings

    plugins:
      ServoSpindle:
        gpio_library: rpi_hardware_pwm
        servo_min_duty_cycle: 5
        servo_max_duty_cycle: 10
        servo_initial_value: -1
        servo_min_pulse_width: 0.001
        servo_max_pulse_width: 0.002
        servo_frame_width: .02
        servo_gpio_pin: 26
        pigpio_host: 127.0.0.1
        pigpio_port: 8888
        minimum_speed: 0
        maximum_speed: 10000

gpio_library can be set to **rpi_hardware_pwm** or **pigpio**.

The following settings apply to **rpi_hardware_pwm**:
    
    servo_min_duty_cycle: 5
    servo_max_duty_cycle: 10

    * servo_min_duty_cycle is used as the servo_initial_value with this implementation

The following settings apply to **pigpio**:

    servo_initial_value: -1
    servo_min_pulse_width: 0.001
    servo_max_pulse_width: 0.002
    servo_frame_width: .02
    servo_gpio_pin: 26
    pigpio_host: 127.0.0.1
    pigpio_port: 8888

The following settings are global:

    gpio_library: rpi_hardware_pwm or pigpio
    minimum_speed: 0
    maximum_speed: 10000

**minimum_speed** and **maximum_speed** can be arbitrary but are intended to represent your GRBL spindle speed value range.  To be consistent with your GRBL controller, you should set these to the same values you have for min/max spindle speed in GRBL's $31 and $30 settings, but this is not absolutely necessary.  Whatever S### value provided is re-scaled from the minimum/maximum speed range to the **servo_min_duty_cycle** and **servo_max_duty_cycle** range when using **rpi_hardware_pwm** or the **servo_min_pulse_width** and **servo_max_pulse_width** range if using **pigpio**.
