from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

import pytz


class Field:
    def __init__(self, required=False, _d=None):
        self.required = required
        self.__doc__ = _d
        super().__init__()

    def __get__(self, instance, objtype):
        if instance._data.get(self.name, None) is None:
            instance._data[self.name] = self.initialize()
        return instance._data[self.name]

    def __set__(self, instance, value):
        raise AttributeError("Read-only!")

    def __delete__(self, instance):
        del instance._data[self.name]

    def __set_name__(self, owner, name):
        self.name = name


class StringField(Field):

    def __set__(self, instance, value):
        instance._data[self.name] = value


class NumericField(Field):
    def __init__(self, places=0, required=False, _d=None):
        self.places = places
        super().__init__(required=required, _d=_d)

    def __set__(self, instance, value):
        if not isinstance(value, (Decimal, int)):
            raise TypeError("Value is not a decimal or int")
        if isinstance(value, int):
            value = Decimal(value)
        instance._data[self.name] = str(value.quantize(
            Decimal('1') / 10 ** self.places, ROUND_HALF_UP
        ))


class DateField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, date):
            raise TypeError("Value is not a date")
        instance._data[self.name] = value.isoformat()


class LocalDateTimeField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, datetime):
            raise TypeError("Value is not a datetime")
        if value.utcoffset() is None:
            raise TypeError("Value is not timezone-aware")
        instance._data[self.name] = value.isoformat().strftime('%Y-%m-%dT%H:%M:%S')


class ISODateTimeField(Field):
    def __set__(self, instance, value):
        if not isinstance(value, datetime):
            raise TypeError("Value is not a datetime")
        if value.utcoffset() is None:
            raise TypeError("Value is not timezone-aware")
        instance._data[self.name] = value.astimezone(pytz.UTC).isoformat().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
