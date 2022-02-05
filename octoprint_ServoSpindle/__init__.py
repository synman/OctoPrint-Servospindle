# coding=utf-8
from __future__ import absolute_import
from octoprint.events import Events

import octoprint.plugin
import re

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo


class ServospindlePlugin(
                            octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.StartupPlugin,
                            octoprint.plugin.EventHandlerPlugin,
                            octoprint.plugin.TemplatePlugin,
                        ):

    def __init__(self):
        self.servo_initial_value = None
        self.servo_min_pulse_width = None
        self.servo_max_pulse_width = None
        self.servo_frame_width = None
        self.servo_gpio_pin = None

        self.pigpio_host = None
        self.pigpio_port = None

        self.minimum_speed = None
        self.maximum_speed = None

        self.M5Active = False
        self.servoValue = None

        self.servo = None

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        self._logger.debug("__init__: get_settings_defaults")
        return dict(
            servo_initial_value = -1,
            servo_min_pulse_width = 0.001128,
            servo_max_pulse_width = 0.002,
            servo_frame_width = .02,
            servo_gpio_pin = 26,
            pigpio_host = "octopi-zero2",
            pigpio_port = 32000,
            minimum_speed = 0,
            maximum_speed = 10000,
        )

    ##-- StartupPlugin mix-in
    def on_startup(self, host, port):
        self._logger.debug("__init__: on_startup host=[{}] port=[{}]".format(host, port)))

        self.servo_initial_value = self._settings.get(["servo_initial_value"])
        self.servo_min_pulse_width = self._settings.get(["servo_min_pulse_width"])
        self.servo_max_pulse_width = self._settings.get(["servo_max_pulse_width"])
        self.servo_frame_width = self._settings.get(["servo_frame_width"])
        self.servo_gpio_pin = self._settings.get(["servo_gpio_pin"])

        self.pigpio_host = self._settings.get(["pigpio_host"])
        self.pigpio_port = self._settings.get(["pigpio_port"])

        self.minimum_speed = self._settings.get(["minimum_speed"])
        self.maximum_speed = self._settings.get(["maximum_speed"])

        self.servoValue = self.servo_initial_value

        factory = PiGPIOFactory(host=self.pigpio_host, port=self.pigpio_port)

        self.servo = Servo(
                           self.servo_gpio_pin,
                           pin_factory=factory,
                           initial_value=self.servo_initial_value,
                           min_pulse_width=self.servo_min_pulse_width,
                           max_pulse_width=self.servo_max_pulse_width,
                           frame_width=self.servo_frame_width
                          )


    ##-- gcode sending hook
    def hook_gcode_sending(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        self._logger.debug("__init__: hook_gcode_sending phase=[{}] cmd=[{}] cmd_type=[{}] gcode=[{}]".format(phase, cmd, cmd_type, gcode))
        self.process_gcode_data(cmd)


    ##-- gcode received hook
    def hook_gcode_received(self, comm_instance, line, *args, **kwargs):
        self._logger.debug("__init__: hook_gcode_received line=[{}]".format(line.replace("\r", "<cr>").replace("\n", "<lf>")))
        self.process_gcode_data(line)
        return line


    def process_gcode_data(self, gcode):
        data = gcode.upper().strip()

        if "M5" in data and not self.M5Active:
            self._logger.debug("setting servo to minimum (M5)")
            self.M5Active = True
            self.servo.min()

        if "M3" in data and self.M5Active:
            self._logger.debug("unlocking servo (M3)")
            if not self.servo.value == self.servoValue:
                self._logger.debug("setting servo to [{}]".format(servoValue))
                self.servo.value = self.servoValue
            self.M5Active = False

        match = re.search(r".*[S]\ *(-?[\d.]+).*", data)
        if not match is None:
            speed = float(match.groups(1)[0])
            speedRange = self.maximum_speed - self.minimum_speed
            speedPercent = (speed - self.minimum_speed) / speedRange

            servoValue = 2 * speedPercent - 1
            servoValue = -1 if servoValue < -1 else servoValue
            servoValue = 1 if servoValue > 1 else servoValue

            if not self.servoValue == servoValue:
                self._logger.debug("setting servo reference to [{}]".format(servoValue))
                self.servoValue = servoValue

                if not self.M5Active:
                    self._logger.debug("setting servo to [{}]".format(servoValue))
                    self.servo.value = self.servoValue


    ##-- EventHandlerPlugin mix-in
    def on_event(self, event, payload):
        self._logger.debug(
            "__init__: on_event event=[{}] payload=[{}]".format(event, payload)
        )

        if event == Events.SHUTDOWN:
            self._logger.debug("shutting down")
            self.servo.value = self.servo_initial_value


    ##~~ AssetPlugin mixin
    def get_assets(self):
        self._logger.debug("__init__: get_assets")

        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/ServoSpindle.js"],
            "css": ["css/ServoSpindle.css"],
            "less": ["less/ServoSpindle.less"],
        }


    ##~~ Softwareupdate hook
    def get_update_information(self):
        self._logger.debug("__init__: get_update_information")

        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "ServoSpindle": {
                "displayName": "Servospindle Plugin",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "synman",
                "repo": "OctoPrint-Servospindle",
                "current": self._plugin_version,
                # update method: pip
                "pip": "https://github.com/synman/OctoPrint-Servospindle/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Servospindle Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
# __plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ServospindlePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.sending": __plugin_implementation__.hook_gcode_sending,
        'octoprint.comm.protocol.gcode.received': __plugin_implementation__.hook_gcode_received,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    }
