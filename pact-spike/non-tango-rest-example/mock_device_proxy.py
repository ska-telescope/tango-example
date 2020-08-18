from collections import defaultdict
import pytest
from unittest import mock
from pactman import Pact

class TangoPact(Pact):

    mock_proxy = mock.MagicMock()

    @property
    def device_proxy_mock(self): # make this a smarter mock
        self.mock_proxy = mock.MagicMock()
        return self.mock_proxy

    def start_mocking(self):
        self.mock_device_proxies = defaultdict(self.device_proxy_mock)
        self._mock_handler = mock.patch(
            "tango.DeviceProxy", side_effect=lambda fqdn: self.mock_device_proxies[fqdn]
        )
        self._mock_handler.start()

    def stop_mocking(self):
        self._mock_handler.stop()

    def with_request(self, method):
        return self

    def will_respond_with(self, body):
        self.mock_proxy.read_attribute.return_value = body
        return self

    def setup(self):
        pass

    def verify(self):
        pass
