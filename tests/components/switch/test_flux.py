"""The tests for the Flux switch platform."""
import unittest
from datetime import timedelta
from unittest.mock import patch

from blumate.bootstrap import _setup_component, setup_component
from blumate.components import switch, light
from blumate.const import CONF_PLATFORM, STATE_ON, SERVICE_TURN_ON
import blumate.loader as loader
import blumate.util.dt as dt_util
from tests.common import get_test_home_assistant
from tests.common import fire_time_changed, mock_service


class TestSwitchFlux(unittest.TestCase):
    """Test the Flux switch platform."""

    def setUp(self):
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        # self.hass.config.components = ['flux', 'sun', 'light']

    def tearDown(self):
        """Stop everything that was started."""
        self.hass.stop()

    def test_valid_config(self):
        """Test configuration."""
        assert _setup_component(self.hass, 'switch', {
            'switch': {
                'platform': 'flux',
                'name': 'flux',
                'lights': ['light.desk', 'light.lamp'],
            }
        })

    def test_valid_config_with_info(self):
        """Test configuration."""
        assert _setup_component(self.hass, 'switch', {
            'switch': {
                'platform': 'flux',
                'name': 'flux',
                'lights': ['light.desk', 'light.lamp'],
                'stop_time': '22:59',
                'start_time': '7:22',
                'start_colortemp': '1000',
                'sunset_colortemp': '2000',
                'stop_colortemp': '4000'
            }
        })

    def test_valid_config_no_name(self):
        """Test configuration."""
        assert _setup_component(self.hass, 'switch', {
            'switch': {
                'platform': 'flux',
                'lights': ['light.desk', 'light.lamp']
            }
        })

    def test_invalid_config_no_lights(self):
        """Test configuration."""
        assert not _setup_component(self.hass, 'switch', {
            'switch': {
                'platform': 'flux',
                'name': 'flux'
            }
        })

    def test_flux_when_switch_is_off(self):
        """Test the flux switch when it is off."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=10, minute=30,
                                          second=0)
        sunset_time = test_time.replace(hour=17, minute=0,
                                        second=0)
        sunrise_time = test_time.replace(hour=5, minute=0,
                                         second=0) + timedelta(days=1)
        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        self.assertEqual(0, len(turn_on_calls))

    def test_flux_before_sunrise(self):
        """Test the flux switch before sunrise."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=2, minute=30,
                                          second=0)
        sunset_time = test_time.replace(hour=17, minute=0,
                                        second=0)
        sunrise_time = test_time.replace(hour=5, minute=0,
                                         second=0) + timedelta(days=1)
        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 119)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.591, 0.395])

    # pylint: disable=invalid-name
    def test_flux_after_sunrise_before_sunset(self):
        """Test the flux switch after sunrise and before sunset."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=8, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 180)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.431, 0.38])

    # pylint: disable=invalid-name
    def test_flux_after_sunset_before_stop(self):
        """Test the flux switch after sunset and before stop."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=17, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 153)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.496, 0.397])

    # pylint: disable=invalid-name
    def test_flux_after_stop_before_sunrise(self):
        """Test the flux switch after stop and before sunrise."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=23, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 119)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.591, 0.395])

    # pylint: disable=invalid-name
    def test_flux_with_custom_start_stop_times(self):
        """Test the flux with custom start and stop times."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=17, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id],
                            'start_time': '6:00',
                            'stop_time': '23:30'
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 154)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.494, 0.397])

    # pylint: disable=invalid-name
    def test_flux_with_custom_colortemps(self):
        """Test the flux with custom start and stop colortemps."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=17, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id],
                            'start_colortemp': '1000',
                            'stop_colortemp': '6000'
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 167)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.461, 0.389])

    # pylint: disable=invalid-name
    def test_flux_with_custom_brightness(self):
        """Test the flux with custom start and stop colortemps."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1 = platform.DEVICES[0]

        # Verify initial state of light
        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=17, minute=30, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id],
                            'brightness': 255
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 255)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.496, 0.397])

    def test_flux_with_multiple_lights(self):
        """Test the flux switch with multiple light entities."""
        platform = loader.get_component('light.test')
        platform.init()
        self.assertTrue(
            light.setup(self.hass, {light.DOMAIN: {CONF_PLATFORM: 'test'}}))

        dev1, dev2, dev3 = platform.DEVICES
        light.turn_on(self.hass, entity_id=dev2.entity_id)
        self.hass.pool.block_till_done()
        light.turn_on(self.hass, entity_id=dev3.entity_id)
        self.hass.pool.block_till_done()

        state = self.hass.states.get(dev1.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        state = self.hass.states.get(dev2.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        state = self.hass.states.get(dev3.entity_id)
        self.assertEqual(STATE_ON, state.state)
        self.assertIsNone(state.attributes.get('xy_color'))
        self.assertIsNone(state.attributes.get('brightness'))

        test_time = dt_util.now().replace(hour=12, minute=0, second=0)
        sunset_time = test_time.replace(hour=17, minute=0, second=0)
        sunrise_time = test_time.replace(hour=5,
                                         minute=0,
                                         second=0) + timedelta(days=1)

        with patch('blumate.util.dt.now', return_value=test_time):
            with patch('blumate.components.sun.next_rising',
                       return_value=sunrise_time):
                with patch('blumate.components.sun.next_setting',
                           return_value=sunset_time):
                    assert setup_component(self.hass, switch.DOMAIN, {
                        switch.DOMAIN: {
                            'platform': 'flux',
                            'name': 'flux',
                            'lights': [dev1.entity_id,
                                       dev2.entity_id,
                                       dev3.entity_id]
                        }
                    })
                    turn_on_calls = mock_service(
                        self.hass, light.DOMAIN, SERVICE_TURN_ON)
                    switch.turn_on(self.hass, 'switch.flux')
                    self.hass.pool.block_till_done()
                    fire_time_changed(self.hass, test_time)
                    self.hass.pool.block_till_done()
        call = turn_on_calls[-1]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 171)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.452, 0.386])
        call = turn_on_calls[-2]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 171)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.452, 0.386])
        call = turn_on_calls[-3]
        self.assertEqual(call.data[light.ATTR_BRIGHTNESS], 171)
        self.assertEqual(call.data[light.ATTR_XY_COLOR], [0.452, 0.386])
