# OctoPrint-Servospindle

Servo Spindle enables you to control a "servo" (typically an Electronic Speed Controller) triggered off of GRBL
gcode commands sent to and the status reported by your CNC machine.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/synman/OctoPrint-Servospindle/archive/master.zip

You'll need **pigpiod** installed somewhere accessible to your Octoprint server.  It can be running on
the same machine as Octoprint or it can installed on a remote computer.

The dependent **gpiozero** and **pigpio** libraries as installed automatically with Servo Spindle.

## Configuration

There is no Plugin Settings UI at this time but this plugin is fully configurable via Octoprint's config.yaml file.

** Default Settings **

plugins:
  ServoSpindle:
    servo_initial_value: -1
    servo_min_pulse_width: 0.001
    servo_max_pulse_width: 0.002
    servo_frame_width: .02
    servo_gpio_pin: 26
    pigpio_host: 127.0.0.1
    pigpio_port: 8888
    minimum_speed: 0
    maximum_speed: 10000
