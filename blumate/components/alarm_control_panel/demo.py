"""
Demo platform that has two fake alarm control panels.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
import blumate.components.alarm_control_panel.virtual as virtual


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Demo alarm control panel platform."""
    add_devices([
        virtual.VirtualAlarm(hass, 'Alarm', '1234', 5, 10),
    ])
