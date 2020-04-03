import functools

from elasticapm import Client as ElasticClient
from elasticapm.utils.disttracing import TraceParent
from elasticapm.conf.constants import TRANSACTION


def start_transaction(tango_device_instance, transaction_type):
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
    # parent = TraceParent.from_string('00-03d67dcdd62b7c0f7a675424347eee3a-5f0e87be26015733-01')
    transaction = tango_device_instance.apm_client.begin_transaction(f"{device_name}")
    tango_device_instance.logger.info(
        f"Start transaction {tango_device_instance} {transaction_type} {transaction.id}"
    )

    return transaction


def end_transaction(transaction, name, result):
    transaction.result = result
    transaction.name = name
    transaction.end()
    transaction.tracer.queue_func(TRANSACTION, transaction.to_dict())


def apm(func):
    @functools.wraps(func)
    def wrapper_apm(*args, **kwargs):
        device_instance = args[0]
        transaction = start_transaction(device_instance, func.__name__)
        transaction_description = f"{device_instance} {func.__name__}"

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
