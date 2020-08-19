from collections import defaultdict
import pytest
from unittest import mock
from pactman import Pact

class TangoPact(Pact):

    def device_proxy_mock(self):
        # TODO: make this a smarter mock
        self.mock_proxy = mock.MagicMock()
        return self.mock_proxy

    def start_mocking(self):
        self.mock_proxy = self.device_proxy_mock()
        self._mock_handler = mock.patch(
            "tango.DeviceProxy", side_effect=lambda fqdn: self.mock_proxy
        )
        self._mock_handler.start()

    def stop_mocking(self):
        self._mock_handler.stop()

    def with_request(self, req_type, name, arg=None):
        self.request_type = req_type
        self.request_name = name
        self.request_arg = arg
        return self


    def will_respond_with(self, reply):
        self.respond_with_reply = reply
        if self.request_type in ['method', 'command']:

            def getter(*args):
                num_args_expected = 0 if self.request_arg is None else 1
                assert len(args) == num_args_expected, "Incorrect number of args..."
                if num_args_expected:
                    assert args[0] == self.request_arg, f"Unexpected arg value '{args[0]}'"
                return reply

            mock_attr = getattr(self.mock_proxy, self.request_name)
            mock_attr.side_effect = getter
        elif self.request_type == 'attribute':
            setattr(self.mock_proxy, self.request_name, reply)
        else:
            raise NotImplementedError(f"Invalid request type {self.request_type}")
        return self

    def setup(self):
        pass

    def verify(self):
        pass
