"""Validate a pact against a target device"""
import argparse

from tango_record_replay import DeviceProxyRecordReplay


def validate_pact_against_device(args):
    """Validate a pact against a device

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments
    """
    pact_string = args.pact_file.read()
    proxied_device = DeviceProxyRecordReplay(args.tango_device_name)
    result = proxied_device.validate_interactions_against_device(pact_string)
    if result:
        print(result)
    else:
        print("Pact passes")


def main():
    """Entrypoint for the script
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--tango_device_name",
        type=str,
        help="The Tango device name",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--pact_file",
        type=argparse.FileType("r"),
        help="Path to the pact file",
        required=True,
    )
    args = parser.parse_args()
    validate_pact_against_device(args)


if __name__ == "__main__":
    main()
