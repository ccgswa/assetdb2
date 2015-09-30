from django.core.exceptions import ValidationError
import re


def validate_mac(value):
    if not re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", value.lower()) or re.match("[0-9a-f]{12}$", value.lower()):
        raise ValidationError('%s is not a valid MAC address' % value)


def clean_mac(value):
    """
    A helper function for cleaning valid MAC addresses.
    :param value: Any string
    :return: If passed a value in the format AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF or AABBCCDDEEFF returns a valid MAC
    Address in the format AA:BB:CC:DD:EE:FF. Otherwise returns the value unchanged.
    """
    if re.match("[0-9a-f]{2}([:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", value.lower()):
        return value
    elif re.match("[0-9a-f]{2}([-])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", value.lower()):
        return value.replace('-', ':')
    elif re.match("[0-9a-f]{12}$", value.lower()):
        n = 2
        separator = ":"
        value_split = [value[i:i+n] for i in range(0, len(value), n)]
        return separator.join(value_split)
    return value