import re

from django.forms import ValidationError
from rest_framework import serializers


class CustomCharField(serializers.CharField):
    """
    The "str_method" parameter has been added, it is an optional parameter with
    a default value of None. Accepts 4 values "capitalize", "lower", "title"
    and "upper" both methods of the "str" class. If a method is indicated, it
    will be executed to the value.
    """

    def __init__(self, **kwargs):
        self.str_method = kwargs.pop("str_method", None)
        self.validate_regex = kwargs.pop("validate_regex", None)
        super().__init__(**kwargs)

        if self.str_method is not None:
            accepted_methods = ["capitalize", "lower", "title", "upper"]
            if self.str_method not in accepted_methods:
                message = f'El parámetro "{self.str_method}" no es válido.'
                raise Exception(message)

        if self.validate_regex is not None:
            if not isinstance(self.validate_regex, dict):
                message = "El parámetro 'validate_regex' debe de ser un diccionario."
                raise Exception(message)

            if "regex" not in self.validate_regex.keys():
                message = "La llave 'regex' no existe."
                raise Exception(message)

    def run_validation(self, data):
        if isinstance(data, str):
            if not self.required:
                if self.str_method is not None:
                    do_something = getattr(str, self.str_method)
                    data = do_something(data)

                if self.validate_regex is not None:
                    default_error_message = "El campo no tiene un formato correcto"
                    regex = self.validate_regex.get("regex")
                    error_message = self.validate_regex.get("error_message", default_error_message)

                    if not re.match(regex, data):
                        raise ValidationError(error_message)

        return super().run_validation(data)
