import abc
import logging
from blumate.const import STATE_ACTIVE, STATE_IDLE, STATE_UNKNOWN,  STATE_UNAVAILABLE
from blumate.helpers.entity import Entity
from blumate.helpers.entity_component import EntityComponent

DOMAIN = 'database'
SCAN_INTERVAL = 30
DISCOVERY_PLATFORMS = {}

ENTITY_ID_FORMAT = DOMAIN + '.{}'

def setup(bmss, config):
    component = EntityComponent(
        logging.getLogger(__name__), DOMAIN, bmss, SCAN_INTERVAL,
        DISCOVERY_PLATFORMS)

    component.setup(config)

class Database(Entity):
    def state(self):
        if self.is_active:
            return STATE_ACTIVE
        elif self.is_available:
            return STATE_IDLE
        elif self.is_available is None:
            return STATE_UNKNOWN
        else:
            return STATE_UNAVAILABLE

    @property
    def is_active(self):
        """Returns True if an operation is occurring on the database."""
        return False

    @abc.abstractproperty
    def is_available(self):
        """Returns True if database is available for reads/writes."""
        pass

    @abc.abstractmethod
    def create_collection(self, name):
        """
        Create a collection.

        :param name: The name of the new collection.
        :type name: str
        :return True if creation successful, False otherwise.
        :rtype: bool
        """
        pass

    @abc.abstractmethod
    def delete_collection(self, name):
        """
        Delete a collection.

        :param name: The name of the collection to delete.
        :type name: str
        :return True if delete was successful, False otherwise.
        :rtype: bool
        """
        pass



