# Hwam_stove component for Home Assistant

The `hwam_stove` component is used to control a [Hwam Stove with Smartcontrol](http://www.hwam.com/) from Home Assistant.

There is currently support for the following device types within Home Assistant:

- `binary_sensor` to monitor various alarm conditions.
- `fan` to start the stove and control the burn level.
- `sensor` for various values and parameters.

When enabled, this component will automatically add its `fan` entity to Home Assistant.


### Configuration

To add a single stove with name `living_room` to Home Assistant, use the following in configuration.yaml.
```yaml
# Example configuration.yaml entry
hwam_stove:
  living_room:
    host: 192.168.1.12
```
__host:__
- description: IP address or hostname of the Hwam Stove.
- required: true
- type: string

__monitored_variables:__
- description: A list of variables to expose as sensors.
- required: false
- type: list
- keys:
    - __algorithm__ Algorithm version on the stove.
    - __burn_level__ Current burn level.
    - __date_time__ Date and time on the stove.
    - __firmware_version__ Firmware version of the stove.
    - __maintenance_alarms__ Maintenance alarms will be added as a series of binary sensors (see [Maintenance Alarms](#maintenance_alarms)).
    - __message_id__ Last known message ID.
    - __new_fire_wood_estimate__ Estimate time when the stove will request new firewood.
    - __night_begin_time__ Night lowering start time.
    - __night_end_time__ Night lowering end time.
    - __night_lowering__ Current night lowering status.
    - __operation_mode__ Current operation mode.
    - __oxygen_level__ Oxygen level in the chimney.
    - __phase__ Current phase.
    - __refill_alarm__ Whether the stove is currently requesting new firewood.
    - __remote_refill_alarm__ Whether the remote refill alarm option is switched on.
    - __remote_version__ Firmware version on the room unit.
    - __room_termperature__ Room temperature in degrees Celsius.
    - __safety_alarms__ Safety alarms will be added as a series of binary sensors (see [Safety Alarms](#safety_alarms)).
    - __stove_temperature__ Chimney temperature in degrees Celsius.
    - __time_since_remote_message__ Number of seconds since the last message was received from the room unit.
    - __time_to_new_fire_wood__ Estimate time until the stove will request new firewood.
    - __updating__ Current updating status.
    - __valve1_position__ Current position of valve 1.
    - __valve2_position__ Current position of valve 2.
    - __valve3_position__ Current position of valve 3.


###Maintenance Alarms

When the `maintenance_alarms` option is added to the list of `monitored_variables`, the following binary sensors will be added to Home Assistant. In each entity id, <name> will be replaced by the name of the stove as specified in configuration.yaml.
- `binary_sensor.maintenance_alarms_<name>` This is a catch-all sensor which will be `on` when any other maintenance alarm is active.
- `binary_sensor.maintenance_alarms_stove_backup_battery_low_<name>` Indicates that the backup battery in the stove is low. Charge or replace the battery.
- `binary_sensor.maintenance_alarms_o2_sensor_fault_<name>` Indicates a fault in the oxygen sensor. Run a self test on the stove. The stove may be used with this error, but the door should be kept open when refilling until permanent flames are seen. Service is recommended as soon as possible.
- `binary_sensor.maintenance_alarms_o2_sensor_offset_<name>` Indicates an offset on the oxygen sensor. Run a self test on the stove. The stove may be used with this error, but the door should be kept open when refilling until permanent flames are seen. Service is recommended as soon as possible.
- `binary_sensor.maintenance_alarms_stove_temperature_sensor_fault_<name>` Indicates a fault in the stove temperature sensor. Run a self test on the stove. The stove may be used with this error, but the door should be kept open when refilling until permanent flames are seen. Service is recommended as soon as possible.
- `binary_sensor.maintenance_alarms_room_temperature_sensor_fault_<name>` Indicates a fault in the room temperature sensor. Replace the batteries in the room unit. The stove may be used with this error.
- `binary_sensor.maintenance_alarms_communication_fault_<name>` Indicates a fault in the communication between the stove and the room unit. Place the room unit closer to the stove and make sure it is switched on. If necessary, replace the batteries in the room unit. The stove may be used with this error.
- `binary_sensor.maintenance_alarms_room_temperature_sensor_battery_low_<name>` Indicates that the battery level in the room unit is low. Replace the batteries in the room unit.


###Safety Alarms

When the `safety_alarms` option is added to the list of `monitored_variables`, the following binary sensors will be added to Home Assistant. In each entity id, <name> will be replaced by the name of the stove as specified in configuration.yaml.
- `binary_sensor.safety_alarms_<name>` This is a catch-all sensor which will be `on` when any other safety alarm is active.
- `binary_sensor.safety_alarms_valve_fault_<name>` Indicates a fault with one or more valves. Restart the stove and run a self test. Do not use the stove until the problem is fixed.
- `binary_sensor.safety_alarms_bad_configuration_<name>` Indicates a fault in the airbox configuration. Update the airbox software with the `format` option enabled. Do not use the stove until the problem is fixed.
- `binary_sensor.safety_alarms_valve_disconnected_<name>` Indicates that one or more valves are not connected. Restart the stove and run a self test. Do not use the stove until the problem is fixed.
- `binary_sensor.safety_alarms_valve_calibration_error_<name>` Indicates a calibration error with one or more valves. Restart the stove and run a self test. Do not use the stove until the problem is fixed.
- `binary_sensor.safety_alarms_chimney_overheat_<name>` Indicates a chimney overheat. The stove will continue to operate in `safety mode` until the temperature is back to normal (below 450 degrees Celsius).
- `binary_sensor.safety_alarms_door_open_too_long_<name>` Indicates that the door has been open for too long.
- `binary_sensor.safety_alarms_manual_safety_alarm_<name>` Indicates a manually triggered safety alarm.
- `binary_sensor.safety_alarms_stove_sensor_fault_<name>` Indicates a fault with one or more sensors. Restart the stove and run a self test. Do not use the stove until the problem is fixed.


###Services

** Service 'hwam_stove.enable_night_lowering' **

Enable the night lowering feature on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

** Service 'hwam_stove.disable_night_lowering' **

Disable the night lowering feature on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

** Service 'hwam_stove.enable_remote_refill_alarm' **

Enable the remote refill alarm option on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

** Service 'hwam_stove.disable_remote_refill_alarm' **

Disable the remote refill alarm option on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.

** Service 'hwam_stove.set_night_lowering_hours' **

Set the night lowering hours. At least one of `start_time` or `end_time` must be provided.
This service takes the following parameters:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.
- __start_time__ _(Optional)_ The time in 24h format at which night lowering should start. Example: `23:30`.
- __end_time__ _(Optional)_ The time in 24h format at which night lowering should end. Example: `07:00`.

** Service 'hwam_stove.set_clock'  **

Set the date and time on the Hwam Stove.
This service takes the following parameter:
- __stove_name__ _(Required)_ The name of the stove as specified in configuration.yaml. Example: `living_room`.
- __date__ _(Optional)_ Date to set on the stove. Defaults to today. Example: `2018-10-23`.
- __time__ _(Optional)_ Time in 24h format to set on the stove. Defaults to the current time. Example: `19:34`.

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