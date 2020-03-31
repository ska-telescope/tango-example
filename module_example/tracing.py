import functools
import elasticapm

defaults = {}
apm_client = elasticapm.Client(
    {
        'SERVICE_NAME': 'CalenderClock',
        'SERVER_URL': 'http://apm-server-logging-test:8200'
    },
    **defaults
)

def apm(func):
    @functools.wraps(func)
    def wrapper_apm(*args, **kwargs):
        try:
            apm_client.begin_transaction("CalendarClock")
            res = func(*args, **kwargs)
        except Exception:
            apm_client.capture_exception()
            apm_client.end_transaction(f"CalendarClock {func.__name__!r}", "Failed")
            raise
        else:
            apm_client.end_transaction(f"CalendarClock {func.__name__!r}", "Success")
        return res
    return wrapper_apm
