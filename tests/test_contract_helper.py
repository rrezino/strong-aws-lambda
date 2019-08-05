from dataclasses import dataclass

from contract_helper import _get_all_attrs_from_class, _hydrate_contract_from_event, _validate_keys_in_event, \
    hydrate_contract
from dacite import MissingValueError
from pytest import raises


def test_validate_keys_in_event_when_key_in_dict_single_level_should_not_raise_exception():
    event = dict(level1='test', level11='test2', level111='test3')

    _validate_keys_in_event(event, ['level1', 'level11', 'level111'])


def test_validate_keys_in_event_when_one_key_not_in_dict_single_level_should_raise_exception():
    event = dict(level1='test', level11='test2', level111='test3')

    with raises(ValueError) as exc_info:
        _validate_keys_in_event(event, ['level1', 'level11', 'level113'])
        assert exc_info.value == 'level113 not found in event'


def test_validate_keys_in_event_when_key_in_dict_multi_level_should_not_raise_exception():
    event = dict(level1='test', level11='test2', level2=dict(level111='test3'))

    _validate_keys_in_event(event, ['level1', 'level11', 'level2:level111'])


def test_validate_keys_in_event_when_one_key_in_dict_multi_level_should_not_raise_exception():
    event = dict(level1='test', level11='test2', level2=dict(level111='test3'))

    with raises(ValueError) as exc_info:
        _validate_keys_in_event(event, ['level1', 'level11', 'level2:level112'])

    assert str(exc_info.value) == "Key ['level2:level112'] not found in event"


def test_validate_keys_in_event_when_keys_in_dict_multi_level_should_not_raise_exception():
    event = dict(level1='test', level11='test2', level2=dict(level111='test3'))

    with raises(ValueError) as exc_info:
        _validate_keys_in_event(event, ['level1', 'level11', 'level2:level112', 'level10'])

    assert str(exc_info.value) == "Keys ['level2:level112', 'level10'] not found in event"


@dataclass
class TestClassMatchingFields:
    field1: str
    field2: str
    field3: str


def test_hydrate_contract_from_event_when_all_fields_matches_returns_object_with_all_fields_set():
    event = dict(field1='test', field2='test2', field3='test3')
    test = _hydrate_contract_from_event(TestClassMatchingFields, event)

    assert test.field1 == event['field1'] and test.field2 == event['field2'] and test.field3 == event['field3']


@dataclass
class TestClassMissingFields:
    field1: str
    field2: str


def test_hydrate_contract_from_event_when_missing_field_in_class_returns_object_with_all_fields_set():
    event = dict(field1='test', field2='test2', field3='test3')
    test = _hydrate_contract_from_event(TestClassMissingFields, event)

    assert test.field1 == event['field1'] and test.field2 == event['field2']


@dataclass(frozen=True)
class TestClassMatchingFields:
    field1: str
    field2: str
    field3: str


def test_hydrate_contract_from_event_when_missing_field_in_event_raises_exception():
    event = dict(field1='test', field2='test2')

    with raises(MissingValueError):
        _hydrate_contract_from_event(TestClassMatchingFields, event)


@dataclass(frozen=True)
class TestClassGetAttrs:
    field1: str
    field2: str
    field3: str


def test_get_all_attrs_from_class_return_all_attrs_from_an_object_as_str_list():
    result_list = _get_all_attrs_from_class(TestClassGetAttrs)

    assert result_list == ['field1', 'field2', 'field3']


@dataclass
class TestClassHydrateContract:
    field1: str
    field2: str


def test_hydrate_contract_when_all_fields_are_supplied_should_return_dataclass_with_fields_set():
    event = dict(field1='test', field2='test2')
    contract = hydrate_contract(event, TestClassHydrateContract)

    assert contract.field1 == event['field1'] and contract.field2 == event['field2']


@dataclass
class TestClassLevel2:
    field1_sub: str
    field2_sub: str


@dataclass
class TestClassLevel1:
    field1: str
    field2: TestClassLevel2


def test_get_attr_for_nested_dataclasses_should_return_all_fields():
    attrs = _get_all_attrs_from_class(TestClassLevel1)

    assert attrs == ['field1', 'field2:field1_sub', 'field2:field2_sub']


def test_hydrate_contract_when_nested_contract_classes_with_all_fields_supplied_should_return_class_with_fields_set():
    event = dict(field1='test', field2=dict(field1_sub='test_sub', field2_sub='test_sub'))

    contract = hydrate_contract(event, TestClassLevel1)

    assert contract.field1 == event['field1'] \
           and contract.field2.field1_sub == event['field2']['field1_sub'] \
           and contract.field2.field2_sub == event['field2']['field2_sub']
