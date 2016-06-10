"""
A component which allows you to send data to an Influx database.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/influxdb/
"""
import logging

import pymongo.errors

from blumate.helpers.entity import Entity
import blumate.util as util
from blumate import bootstrap
from pymongo.monitoring import CommandListener
from blumate.const import (EVENT_BLUMATE_STOP,
                           EVENT_BLUMATE_START,
                           EVENT_STATE_CHANGED,
                           EVENT_PLATFORM_DISCOVERED,
                           STATE_ACTIVE,
                           STATE_IDLE,
                           STATE_UNKNOWN,
                           ATTR_DISCOVERED,
                           ATTR_FRIENDLY_NAME,
                           ATTR_SERVICE)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mongo"
DEPENDENCIES = []

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 27017
DEFAULT_TZ_AWARE = True
DEFAULT_SOCKET_TIMEOUT_MS = None
DEFAULT_SSL = False
DEFAULT_MAX_POOL_SIZE = 100
DEFAULT_SOCKET_KEEP_ALIVE = False

REQUIREMENTS = ['pymongo==3.2.2']

CONF_HOST = 'host'
CONF_PORT = 'port'
CONF_TZ_AWARE = 'tz_aware'
CONF_SOCKET_TIMEOUT_MS = 'socket_timeout_ms'
CONF_SSL = 'ssl'
CONF_MAX_POOL_SIZE = 'max_pool_size'
CONF_SOCKET_KEEP_ALIVE = 'socket_keep_alive'

SERVICE_UNLOCK = 'unlock'
SERVICE_DISCOVER_DATABASES = 'discover_databases'
SERVICE_DISCONNECT = 'disconnect'

__client = None


class MongoCommandEvent(CommandListener):
    """
    https://api.mongodb.com/python/current/api/pymongo/monitoring.html#module-pymongo.monitoring
    """

    def started(self, event):
        _LOGGER.debug("Command {0.command_name} with request id "
                      "{0.request_id} started on server "
                      "{0.connection_id}".format(event))

    def succeeded(self, event):
        _LOGGER.info("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "succeeded in {0.duration_micros} "
                     "microseconds".format(event))

    def failed(self, event):
        _LOGGER.warn("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "failed in {0.duration_micros} "
                     "microseconds".format(event))


class Mongo(Entity):
    def __init__(self, bmss, config):
        """Setup the MongoDB component."""
        self.__state = STATE_UNKNOWN

        self.bmss = bmss

        self.__config = config[DOMAIN]
        self.__host = util.convert(self.__config.get(CONF_HOST), str, DEFAULT_HOST)
        self.__port = util.convert(self.__config.get(CONF_PORT), int, DEFAULT_PORT)
        self.__tz_aware = util.convert(self.__config.get(CONF_TZ_AWARE), bool, DEFAULT_TZ_AWARE)
        self.__socket_timeout_ms = util.convert(self.__config.get(CONF_SOCKET_TIMEOUT_MS), int, DEFAULT_SOCKET_TIMEOUT_MS)
        self.__ssl = util.convert(self.__config.get(CONF_SSL), bool, DEFAULT_SSL)
        self.__max_pool_size = util.convert(self.__config.get(CONF_MAX_POOL_SIZE), int, DEFAULT_MAX_POOL_SIZE)
        self.__socket_keep_alive = util.convert(self.__config.get(CONF_SOCKET_KEEP_ALIVE),
                                                int,
                                                DEFAULT_SOCKET_KEEP_ALIVE)

        from pymongo import MongoClient

        self.__client = MongoClient(host = self.__host,
                                    port = self.__port,
                                    tz_aware=self.__tz_aware,
                                    maxPoolSize=self.__max_pool_size,
                                    socketTimeoutMS =self.__socket_timeout_ms,
                                    ssl = self.__ssl,
                                    socketKeepAlive = self.__socket_keep_alive,
                                    document_class = dict,
                                    connect = True,
                                    event_listeners = [MongoCommandEvent()])

        # Will fail here if connection is not able to be established
        assert(self.__client is not None)
        self.__state = STATE_IDLE
        bmss.bus.listen_once(EVENT_BLUMATE_STOP, self.disconnect)
        bmss.bus.listen_once(EVENT_BLUMATE_START, self.discover_databases)
        bmss.services.register(DOMAIN, SERVICE_DISCOVER_DATABASES, self.discover_databases)
        bmss.services.register(DOMAIN, SERVICE_UNLOCK, self.unlock)
        bmss.services.register(DOMAIN, SERVICE_DISCONNECT, self.disconnect)

    def discover_databases(self, event):
        """Discover available databases."""
        self.__state = STATE_ACTIVE
        database_list = self.__client.database_names()
        self.__state = STATE_ACTIVE
        _LOGGER.info("Available Databases: %s", database_list)

    def unlock(self, event):
        """Enables writes to the server."""
        _LOGGER.debug("Unlocking server...")
        self.__client.unlock()

        if self.__client.is_locked:
            _LOGGER.warn("Server is still locked. Maybe a permissions issue?")

        else:
            _LOGGER.info("Server is unlocked.")


    def disconnect(self, event):
        """Disconnect from the MongoDB Server."""
        _LOGGER.debug("Disconnecting from MongoDB Server...")
        self.__client.close()
        _LOGGER.info("Disconnected from MongoDB Server.")

setup = Mongo
