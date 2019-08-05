from strong_aws_lambda import custom_resource_error_handler


@custom_resource_error_handler
def method_with_error():
    raise RuntimeError('Something nasty happened')


@custom_resource_error_handler
def method_with_proper_result():
    return {'All': 'is good'}


def test_error_handler_should_wrap_function_and_catch_exception_and_respond_with_cloudformation_message():
    result = method_with_error()

    assert isinstance(result, dict)
    assert 'Status' in result
    assert result['Status'] == 'FAILED'
    assert 'Reason' in result
    assert result['Reason'] == 'Something nasty happened'


def test_error_handler_should_not_touch_result_when_no_error_raised():
    result = method_with_proper_result()

    assert 'All' in result
    assert result['All'] == 'is good'
