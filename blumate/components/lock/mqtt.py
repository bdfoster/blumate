"""
Support for MQTT locks.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/lock.mqtt/
"""
import logging

import voluptuous as vol

import blumate.components.mqtt as mqtt
from blumate.components.lock import LockDevice
from blumate.const import CONF_NAME, CONF_OPTIMISTIC, CONF_VALUE_TEMPLATE
from blumate.components.mqtt import (
    CONF_STATE_TOPIC, CONF_COMMAND_TOPIC, CONF_QOS, CONF_RETAIN)
from blumate.helpers import template
import blumate.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['mqtt']

CONF_PAYLOAD_LOCK = 'payload_lock'
CONF_PAYLOAD_UNLOCK = 'payload_unlock'

DEFAULT_NAME = "MQTT Lock"
DEFAULT_PAYLOAD_LOCK = "LOCK"
DEFAULT_PAYLOAD_UNLOCK = "UNLOCK"
DEFAULT_OPTIMISTIC = False

PLATFORM_SCHEMA = mqtt.MQTT_RW_PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PAYLOAD_LOCK, default=DEFAULT_PAYLOAD_LOCK):
        cv.string,
    vol.Optional(CONF_PAYLOAD_UNLOCK, default=DEFAULT_PAYLOAD_UNLOCK):
        cv.string,
    vol.Optional(CONF_OPTIMISTIC, default=DEFAULT_OPTIMISTIC): cv.boolean,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the MQTT lock."""
    add_devices_callback([MqttLock(
        hass,
        config[CONF_NAME],
        config.get(CONF_STATE_TOPIC),
        config[CONF_COMMAND_TOPIC],
        config[CONF_QOS],
        config[CONF_RETAIN],
        config[CONF_PAYLOAD_LOCK],
        config[CONF_PAYLOAD_UNLOCK],
        config[CONF_OPTIMISTIC],
        config.get(CONF_VALUE_TEMPLATE))])


# pylint: disable=too-many-arguments, too-many-instance-attributes
class MqttLock(LockDevice):
    """Represents a lock that can be toggled using MQTT."""

    def __init__(self, hass, name, state_topic, command_topic, qos, retain,
                 payload_lock, payload_unlock, optimistic, value_template):
        """Initialize the lock."""
        self._state = False
        self._hass = hass
        self._name = name
        self._state_topic = state_topic
        self._command_topic = command_topic
        self._qos = qos
        self._retain = retain
        self._payload_lock = payload_lock
        self._payload_unlock = payload_unlock
        self._optimistic = optimistic

        def message_received(topic, payload, qos):
            """A new MQTT message has been received."""
            if value_template is not None:
                payload = template.render_with_possible_json_value(
                    hass, value_template, payload)
            if payload == self._payload_lock:
                self._state = True
                self.update_ha_state()
            elif payload == self._payload_unlock:
                self._state = False
                self.update_ha_state()

        if self._state_topic is None:
            # Force into optimistic mode.
            self._optimistic = True
        else:
            mqtt.subscribe(hass, self._state_topic, message_received,
                           self._qos)

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """The name of the lock."""
        return self._name

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        return self._state

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return self._optimistic

    def lock(self, **kwargs):
        """Lock the device."""
        mqtt.publish(self.hass, self._command_topic, self._payload_lock,
                     self._qos, self._retain)
        if self._optimistic:
            # Optimistically assume that switch has changed state.
            self._state = True
            self.update_ha_state()

    def unlock(self, **kwargs):
        """Unlock the device."""
        mqtt.publish(self.hass, self._command_topic, self._payload_unlock,
                     self._qos, self._retain)
        if self._optimistic:
            # Optimistically assume that switch has changed state.
            self._state = False
            self.update_ha_state()
