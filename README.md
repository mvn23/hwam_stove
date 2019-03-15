# Hwam_stove component for Home Assistant

The `hwam_stove` component is used to control a [Hwam Stove with Smartcontrol](http://www.hwam.com/) from Home Assistant.

There is currently support for the following device types within Home Assistant:

- Binary Sensor
- Fan
- Sensor

When enabled, this component will automatically add its fan entity to Home Assistant.


### Configuration
```yaml
# Example configuration.yaml entry
hwam_stove:
  living_room:
    host: 192.168.1.12
```
__host:__
- description: "IP to connect to the Hwam Stove device as supported by [PyStove](https://pypi.org/project/pystove/)."
- required: true
- type: string

__monitored_variables:__
- description: "A list of variables to expose as sensors."
- required: false
- type: list
- keys:
    - __algorithm__ Room temperature in celcius.
    - __burn_level__ Room temperature in celcius.
    - __date_and_time__ Room temperature in celcius.
    - __firmware_version__ Room temperature in celcius.
    - __maintenance_alarms__ Room temperature in celcius.
    - __message_id__ Room temperature in celcius.
    - __new_firewood_estimate__ Room temperature in celcius.
    - __night_begin_time__ Room temperature in celcius.
    - __night_end_time__ Room temperature in celcius.
    - __night_lowering__ Room temperature in celcius.
    - __operation_mode__ Room temperature in celcius.
    - __oxygen_level__ Room temperature in celcius.
    - __phase__ Room temperature in celcius.
    - __remote_version__ Room temperature in celcius.
    - __room_termperature__ Room temperature in celcius.
    - __safety_alarms__ Room temperature in celcius.
    - __stove_temperature__ Room temperature in celcius.
    - __time_since_remote_message__ Room temperature in celcius.
    - __time_to_new_firewood__ Room temperature in celcius.
    - __valve1_position__ Room temperature in celcius.
    - __valve2_position__ Room temperature in celcius.
    - __valve3_position__ Room temperature in celcius.

###Services

** Service 'hwam_stove.enable_night_lowering' **

Enable the night lowering feature on the Hwam Stove.
This service takes the stove_name as parameter.

** Service 'hwam_stove.disable_night_lowering' **

Disable the night lowering feature on the Hwam Stove.
This service takes the stove_name as parameter.

** Service 'hwam_stove.set_night_lowering_hours' **

Set the night lowering hours.

** Service 'hwam_stove.set_clock'  **

Provide the date and time to the Hwam Stove. When the Hwam Stove is capable of getting the date and time via NTP, it will overwrite the value set by the service.


###Example

A full configuration example for the Hwam Stove with Smartcontrol looks like the one below.

```yaml
# Full example configuration.yaml entry
hwam_stove:
  living_room:
    host: 192.168.1.12
    monitored_variables:
      - room_temperature
      - stove_temperature
      - oxygen_level
      - refill_alarm
```