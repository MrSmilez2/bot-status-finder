# Third Party Library
from rest_framework import serializers


class IntegerLengthValidator:
    def __init__(self, min_length=None, max_length=None, *, length=None):
        self.min_length = length or min_length
        self.max_length = length or max_length

    def __call__(self, value):
        length = len(str(value))
        min_length_cond = self.min_length and length < self.min_length
        max_length_cond = self.max_length and length > self.max_length
        if min_length_cond or max_length_cond:
            error = f"Wrong integer parameter length for value {value}"
            raise serializers.ValidationError(error)
