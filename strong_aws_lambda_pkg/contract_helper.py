from dataclasses import fields, is_dataclass
from typing import Dict, List, Type, TypeVar

from dacite import from_dict

T = TypeVar("T")


def hydrate_contract(event: Dict, contract_class: Type[T]) -> T:
    attr_list = _get_all_attrs_from_class(contract_class)
    _validate_keys_in_event(event, attr_list)
    return _hydrate_contract_from_event(contract_class, event)


def _hydrate_contract_from_event(contract_class: Type[T], event: dict) -> T:
    return from_dict(data_class=contract_class, data=event)


def _validate_keys_in_event(event: dict, keys_list: List[str]):
    # If you have a key which is in multi level dict as {'test': {'test_level':'value'}}
    # And if you are looking to 'test_level' you may pass 'test:test_level' in the list
    # Where ':' indicates the presence of a sublevel
    missing_keys = list()
    work_dict = event
    while keys_list:
        key_description = keys_list.pop(0)
        keys = key_description.split(':')
        if not _chained_dict_lookup(work_dict, keys):
            missing_keys.append(key_description)

    if missing_keys:
        prefix_string = 'Key' if len(missing_keys) == 1 else 'Keys'
        raise ValueError(f'{prefix_string} {missing_keys} not found in event')


def _get_all_attrs_from_class(klass: Type[T]) -> List:
    result_list = []
    for field in fields(klass):
        if is_dataclass(field.type):
            inner_class_fields = _get_all_attrs_from_class(field.type)
            [result_list.append(f'{field.name}:{inner_class_field}') for inner_class_field in inner_class_fields]
        else:
            result_list.append(field.name)

    return result_list


def _chained_dict_lookup(lookup_dict, keys):
    current_level = lookup_dict
    for key in keys:
        if key in current_level:
            current_level = current_level[key]
        else:
            return None
    return current_level
