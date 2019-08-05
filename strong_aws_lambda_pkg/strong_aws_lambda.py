import datetime
import traceback
from functools import wraps
from typing import Type, TypeVar

from aws_lambda_context import LambdaContext
from lambda_utils import LambdaLogger

from contract_helper import hydrate_contract

T = TypeVar("T")


def custom_resource_error_handler(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as ex:
            return {'Status': 'FAILED', 'Reason': str(ex)}

    return decorated


def aws_lambda(contract_class: Type[T]):
    def wrapper(function):
        @wraps(function)
        def decorated(event: dict, context: LambdaContext):
            is_custom_resource = __is_custom_resource(event)
            try:
                duration = 0
                logger = LambdaLogger(event, context)
                event_to_log = __get_event_without_correlation_id(event)

                logger.info('Calling lambda handler with', params=event_to_log)
                started_datetime = datetime.datetime.now()
                try:
                    try:
                        params = hydrate_contract(event, contract_class)
                        return_value = function(params, logger)
                    finally:
                        duration = int((datetime.datetime.now() - started_datetime).total_seconds() * 1000)

                    logger.info('Lambda handler finished with', duration_ms=duration, exception_occurred=False,
                                params=event_to_log)

                except Exception as e:
                    logger.error('Lambda handler finished with', duration_ms=duration, exception_occurred=True,
                                 exception_stacktrace=__get_stacktrace(e), exception_object=e, params=event_to_log)
                    raise e
                return return_value
            except Exception as ex:
                if is_custom_resource:
                    return {'Status': 'FAILED', 'Reason': str(ex)}
                else:
                    raise

        return decorated

    return wrapper


def __get_stacktrace(exception: Exception) -> str:
    return ''.join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))


def __get_event_without_correlation_id(event: dict):
    if not isinstance(event, dict):
        return event

    result_dict = event.copy()
    result_dict.pop('correlation_id', None)
    return result_dict


def __is_custom_resource(event: dict) -> bool:
    return 'ResourceProperties' in event
