import functools
import json

from elasticapm import Client as ElasticClient
from elasticapm.utils.disttracing import TraceParent
from elasticapm.conf.constants import TRANSACTION


def start_transaction(tango_device_instance, transaction_type, args):
    if not hasattr(tango_device_instance, "apm_client"):
        defaults = {}
        class_name = str(tango_device_instance).split("(")[0]
        apm_client = ElasticClient(
            {
                "SERVICE_NAME": class_name,
                "SERVER_URL": "http://apm-server-logging-test:8200",
            },
            **defaults,
        )
        setattr(tango_device_instance, "apm_client", apm_client)

    device_name = tango_device_instance.get_name()
    device_instance = args[0]

    args_json_string = None
    if len(args) == 2:
        if isinstance(args[1], str):
            arg_string = args[1]
            device_instance.logger.info(f"args for args1 {arg_string}")
            try:
                args_json_string = json.loads(arg_string)
            except ValueError:
                pass

    parent_id = None
    if args_json_string:
        if "parent_id" in args_json_string:
            parent_id = args_json_string["parent_id"]
            device_instance.logger.info(f"args for read parent_id {parent_id}")

    if parent_id:
        parent = TraceParent.from_string(parent_id)
        txn = tango_device_instance.apm_client.begin_transaction(
            f"{device_name}", trace_parent=parent
        )
        tango_device_instance.logger.info(
            f"Start transaction {tango_device_instance} {transaction_type} {txn.id} {parent_id}"
        )
    else:
        txn = tango_device_instance.apm_client.begin_transaction(f"{device_name}")
        parent_id = txn.trace_parent.to_string()
        tango_device_instance.logger.info(
            f"Start transaction {tango_device_instance} {transaction_type} {txn.id} None"
        )

    if args_json_string:
        args_json_string["parent_id"] = parent_id
        device_instance.logger.info(f"args for JSON loaded {args_json_string}")
        args = (args[0], json.dumps(args_json_string))

    return txn, args


def end_transaction(transaction, name, result):
    transaction.result = result
    transaction.name = name
    transaction.end()
    transaction.tracer.queue_func(TRANSACTION, transaction.to_dict())


def apm(func):
    @functools.wraps(func)
    def wrapper_apm(*args, **kwargs):
        device_instance = args[0]
        transaction_description = f"{device_instance} {func.__name__}"

        device_instance.logger.info(f"args for {device_instance} {args}")
        device_instance.logger.info(f"args for len {len(args)}")
        transaction, args = start_transaction(device_instance, func.__name__, args)

        res = None
        try:
            res = func(*args, **kwargs)
        except Exception:
            device_instance.apm_client.capture_exception()
            end_transaction(transaction, transaction_description, "Fail")
            raise

        device_instance.logger.info(
            f"After transaction  {transaction.id} {func.__name__!r}"
        )
        end_transaction(transaction, transaction_description, "Success")

        return res

    return wrapper_apm
