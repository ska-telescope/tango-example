"""DeviceProxyRecordReplay proxies a device and stores or rerun interactions"""
import json
import types

from dataclasses import dataclass
from enum import Enum

from tango import DeviceProxy, DevFailed, DeviceAttribute


@dataclass
class Interaction:
    """Describes an interaction"""

    name: str
    args: list
    kwargs: dict
    response: str

    def __str__(self):
        interaction = {}
        interaction["name"] = self.name
        interaction["args"] = self.args
        interaction["kwargs"] = self.kwargs
        interaction["response"] = self.response
        return json.dumps(interaction)


class DeviceProxyRecordReplay:
    """Proxies a device and stores or rerun interactions"""

    def __init__(self, device_name):
        """Init DeviceProxyRecordReplay

        This will set up a device proxy to `device_name` and pass on commands and record
        the interactions.

        Parameters
        ----------
        device_name : string
            The Tango device name to connect to.
        """
        self.device_name = device_name
        self.interactions = []
        try:
            self.proxied_device = DeviceProxy(self.device_name)
        except DevFailed:
            print(f"Could not connect to {self.device_name}")
            raise

    def __getattr__(self, attr):
        """Override getattr

        We do this so we can distinguish between what should be passed on to the proxied
        device and what belongs to this class.

        We also handle functions (or methods) differently to attributes.

        Parameters
        ----------
        attr : string
            The attribute to get, could be attribute/function/method name

        Returns
        -------
        attribute
            The attribute requested, whether from this class or the proxied device
        """
        try:
            return super(DeviceProxyRecordReplay, self).__getattr__(attr)
        except AttributeError:
            return self.__get_class_handler(attr)

    def __get_class_handler(self, name):
        """Here we decide whether to handle a function/method or attribute

        Parameters
        ----------
        name : attribute name
            The name of the requested attribute

        Returns
        -------
        function
            function of attribute handler

        Raises
        ------
        Exception
            If the attribute does not exist on the proxied device
        """
        if not hasattr(self.proxied_device, name):
            raise Exception(
                f"Device {self.device_name} does not have the method/attribute {name}"
            )
        if isinstance(
            getattr(self.proxied_device, name), (types.MethodType, types.FunctionType)
        ):
            handler = self.__method_handler
            handler.__func__.__name__ = name
        else:
            handler = self.__attribute_handler(name)
        return handler

    def __attribute_handler(self, name):
        """Handle the attribute retrieval and storing of the interaction

        Parameters
        ----------
        name : string
            The name of the attribute to be read

        Returns
        -------
        Any
            The attribute value
        """
        result = getattr(self.proxied_device, name)
        self.interactions.append(Interaction(name, [], {}, str(result)))
        return result

    def __method_handler(self, *args, **kwargs):
        """Handle the running of a function against the proxied device and record
        the interaction

        Parameters
        ----------
        args : list
            The args to use in the function
        kwargs : dict
            The kwargs to use in the function

        Returns
        -------
        Any
            The return value of the function

        Raises
        ------
        DevFailed
            If the function fails
        """
        function_name = self.__method_handler.__func__.__name__
        proxied_function = getattr(self.proxied_device, function_name)
        result = None
        try:
            result = proxied_function(*args, **kwargs)
        except DevFailed:
            print(f"Function {function_name} on device {self.device_name} failed")
            raise
        self.interactions.append(Interaction(function_name, args, kwargs, str(result)))
        return result

    def interactions_to_json(self):
        """Dumps the interactions to JSON

        Returns
        -------
        str
            The interaction in JSON format
        """
        interactions_data = {}
        interactions_data["device_name"] = self.device_name
        interactions_data["interactions"] = []
        for interaction in self.interactions:
            interactions_data["interactions"].append(json.loads(str(interaction)))
        return json.dumps(interactions_data)

    def parse_interaction(self, interaction):
        """Parses a interaction dict to Interaction

        Parameters
        ----------
        interaction : dict
            A single interaction

        Returns
        -------
        Interaction
            The Interaction instance of a interaction
        """
        return Interaction(
            interaction["name"],
            interaction["args"],
            interaction["kwargs"],
            interaction["response"],
        )

    def parse_interactions_json(self, json_string):
        """Parses the JSON format of the interactions

        Parameters
        ----------
        json_string : str
            JSON formatted string of all the interactions

        Returns
        -------
        list
            A list of type Interaction

        Raises
        ------
        Exception
            Simple check of the JSON format
        """
        interactions = []
        interactions_dict = json.loads(json_string)
        if "interactions" not in interactions_dict:
            raise Exception("Expected `interactions` in the JSON string")
        for interaction in interactions_dict["interactions"]:
            interactions.append(self.parse_interaction(interaction))
        return interactions

    def add_interactions(self, json_string):
        """Takes a JSON string format of the interactions and adds them to the internal
        list of interactions.

        Parameters
        ----------
        json_string : str
            JSON formatted string of all the interactions
        """
        self.interactions.extend(self.parse_interactions_json(json_string))

    def clear_interactions(self):
        """Clears the internal list of interactions
        """
        self.interactions = []

    def _replay_interaction(self, interaction):
        """Replays a single interaction against the proxied device

        Parameters
        ----------
        interaction : Interaction
            A single interaction

        Returns
        -------
        Any
            The result of the interaction
        """
        proxied_attr = getattr(self.proxied_device, interaction.name)
        if isinstance(proxied_attr, (types.MethodType, types.FunctionType)):
            return proxied_attr(*interaction.args, **interaction.kwargs)
        return proxied_attr

    def replay_interactions(self):
        """Runs all the internal interactions against the device
        """
        print(f"Running interactions against {self.device_name}\n")
        for interaction in self.interactions:
            print(
                f"Running `{interaction.name}` with args, {interaction.args}"
                f" and kwars {interaction.kwargs}"
            )
            response = self._replay_interaction(interaction)
            print(f"Response: {response}\n")

    def validate_interactions_against_device(self, json_string):
        """Gets all the differences between what is expected and the actual interaction
        with the device.

        Parameters
        ----------
        json_string : str
            JSON formatted string of all the interactions

        Returns
        -------
        str
            a list of differences bethween json_string and what actually came from the
            device.
            Note that TimeVal of DeviceAttribute is skiupped as it differs
        """
        interactions = self.parse_interactions_json(json_string)
        differences = []
        for interaction in interactions:
            response = self._replay_interaction(interaction)
            if isinstance(response, DeviceAttribute):
                # `time = ` will differ in DeviceAttribute
                response_lines = str(response).split("\n")
                interaction_lines = interaction.response.split("\n")
                if len(response_lines) != len(interaction_lines):
                    differences.append(
                        f"Expected\n{response}\nGot\n{interaction.response}"
                    )
                    continue

                passed = True
                for response_line, interaction_line in zip(
                    response_lines, interaction_lines
                ):
                    if "TimeVal" not in response_line:
                        if response_line != interaction_line:
                            passed = False
                if not passed:
                    differences.append(f"Interaction: {interaction.name}")
                    differences.append(
                        f"Expected\n{response}\nGot\n{interaction.response}"
                    )
            else:
                if str(response) != interaction.response:
                    differences.append(f"Interaction: {interaction.name}")
                    differences.append(
                        f"Expected\n{response}\nGot\n{interaction.response}"
                    )
        return "\n".join(differences)


if __name__ == "__main__":
    # Proxy the device
    dpr = DeviceProxyRecordReplay("test/power_supply/1")

    # Interact with the device, all actions are passed onto the real device
    state = dpr.State()
    assert str(state) == "STANDBY"
    dpr.ramp(1.2)
    current = dpr.current
    assert current == 1.2
    dpr.ramp(2.4)
    current = dpr.current
    assert current == 2.4
    voltage_attr = dpr.read_attribute("voltage")
    assert voltage_attr.name == "voltage"
    assert voltage_attr.value == 240

    # get the JSON representation of all the interactions
    interactions_json_before = dpr.interactions_to_json()
    print(interactions_json_before)

    # Clear out all the interactions
    dpr.clear_interactions()

    # Add back the interactions
    dpr.add_interactions(interactions_json_before)

    # Confirm the parsing
    interactions_json_after = dpr.interactions_to_json()
    assert interactions_json_before == interactions_json_after

    # Replay all the loaded interactions
    print("\nREPLAY\n")
    dpr.replay_interactions()

    # Run the interactions against the device and verify they are the same
    diff = dpr.validate_interactions_against_device(interactions_json_after)
    assert not diff
    try:
        # Check the negative case
        interactions_json_after = json.loads(interactions_json_after)
        interactions_json_after["interactions"][0]["response"] = "GARBAGERESPONSE"
        diff = dpr.validate_interactions_against_device(
            json.dumps(interactions_json_after)
        )
        print(diff)
        assert not diff
    except AssertionError:
        pass
    else:
        raise Exception("Should have asserted")
