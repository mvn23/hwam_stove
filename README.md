# Hwam_stove component for Home Assistant

The `hwam_stove` component is used to control a [Hwam Stove with Smartcontrol](http://www.hwam.com/) from Home Assistant.

There is currently support for the following device types within Home Assistant:

- `binary_sensor` to monitor various alarm conditions.
- `fan` to start the stove and control the burn level.
- `sensor` for various values and parameters.

### Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=hwam_stove)

### Services

__Service 'hwam_stove.enable_night_lowering'__

Enable the night lowering feature on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

__Service 'hwam_stove.disable_night_lowering'__

Disable the night lowering feature on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

__Service 'hwam_stove.enable_remote_refill_alarm'__

Enable the remote refill alarm option on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

__Service 'hwam_stove.disable_remote_refill_alarm'__

Disable the remote refill alarm option on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

__Service 'hwam_stove.set_night_lowering_hours'__

Set the night lowering hours. At least one of `start_time` or `end_time` must be provided.
This service takes the following parameters:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.
- __start_time__ _(Optional)_ The time in 24h format at which night lowering should start. Example: `23:30`.
- __end_time__ _(Optional)_ The time in 24h format at which night lowering should end. Example: `07:00`.

__Service 'hwam_stove.set_clock'__

Set the date and time on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.
- __date__ _(Optional)_ Date to set on the stove. Defaults to today. Example: `2018-10-23`.
- __time__ _(Optional)_ Time in 24h format to set on the stove. Defaults to the current time. Example: `19:34`.

### Example

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
