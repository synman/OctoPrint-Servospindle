# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import re

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo

class ServospindlePlugin(octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
                         octoprint.plugin.StartupPlugin,
                         octoprint.plugin.TemplatePlugin):

     def __init__(self):
         self.servo_initial_value = None
         self.servo_min_pulse_width = None
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
         return {
             servo_initial_value = -1,
             servo_min_pulse_width = 0.001128,
             servo_gpio_pin = 26,
             pigpio_host = "octopi-zero2",
             pigpio_port = 32000,
             minimum_speed = 0,
             maximum_speed = 10000
         }


     def on_after_startup(self):
         self._logger.debug("__init__: on_after_startup")

         self.servo_initial_value = self._settings.get(["servo_initial_value"])
         self.servo_min_pulse_width = self._settings.get(["servo_min_pulse_width"])
         self.servo_gpio_pin = self._settings.get(["servo_gpio_pin"])

         self.pigpio_host = self._settings.get(["pigpio_host"])
         self.pigpio_port = self._settings.get(["pigpio_port"])

         self.minimum_speed = self._settings.get(["minimum_speed"])
         self.maximum_speed = self._settings.get(["maximum_speed"])

         self.servoValue = self.servo_initial_value

         factory = PiGPIOFactory(host=self.pigpio_host, port=self.pigpio_port)
         self.servo = Servo(self.servo_gpio_pin,
                            pin_factory=factory,
                            initial_value=self.servo_initial_value,
                            min_pulse_width=self.min_pulse_width)


    # #-- gcode sending hook
    def hook_gcode_sending(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        self._logger.debug("__init__: hook_gcode_sending phase=[{}] cmd=[{}] cmd_type=[{}] gcode=[{}]".format(phase, cmd, cmd_type, gcode))
        command = cmd.upper().strip()

        if "M5" in command:
            self._logger.debug("setting servo to minimum (M5)")
            self.M5Active = True
            self.servo.min()

        if "M3" in command:
            self._logger.debug("unlocking servo (M3)")
            self.servo.value = self.servoValue
            self.M5Active = False

        match = re.search(r".*[S]\ *(-?[\d.]+).*", command)
        if not match is None:
            speed = float(match.groups(1)[0])
            speedRange = self.maximum_speed - self._minimum_speed
            speedPercent = (speed - self.minumum_speed) / speedRange

            servoValue = 2 * speedPercent - 1
            servoValue = -1 if servoValue < -1 else servoValue
            servoValue = 1 if servoValue > 1 else servoValue

            self.servoValue = servoValue

            if !self.M5Active:
                self._logger.debug("setting servo to [{}]".format(servoValue))
                servo.value = servoValue

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/ServoSpindle.js"],
            "css": ["css/ServoSpindle.css"],
            "less": ["less/ServoSpindle.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
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
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ServospindlePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.sending": __plugin_implementation__.hook_gcode_sending,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
