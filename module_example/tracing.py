import functools
import elasticapm

def apm(func):
    @functools.wraps(func)
    def wrapper_apm(*args, **kwargs):
        class_name = func.__qualname__.split(".")[-2]
        function_name = func.__name__
        the_class_instance = args[0]
        device_name = the_class_instance.get_name()
        transaction_description = f"{class_name} {device_name} {function_name}"
        defaults = {}
        try:
            if not hasattr(the_class_instance, 'apm_client'):
                apm_client = elasticapm.Client(
                    {
                        'SERVICE_NAME': class_name,
                        'SERVER_URL': 'http://apm-server-logging-test:8200'
                    },
                    **defaults
                )
                setattr(the_class_instance, 'apm_client', apm_client)

            the_class_instance.apm_client.begin_transaction(transaction_description)
            res = func(*args, **kwargs)
        except Exception:
            the_class_instance.apm_client.capture_exception()
            the_class_instance.apm_client.end_transaction(transaction_description, "Failed")
            raise
        else:
            the_class_instance.apm_client.end_transaction(transaction_description, "Success")
        return res
    return wrapper_apm

