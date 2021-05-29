"""Declarative, lazy and decoupled configuration form environment variables.

Buddy-Config allows to use environment variables in lazy and flexible way. Load
a config settings exactly when they are needed but not at import. Define non-global
defaults. Default values could be different for the same config in each of its instance.
Use declarative style.

Examples:

    >>> class MyConf(metaclass=Config):
    >>>     NAME_OF_A_SETTING_A = "NAME_OF_AN_ENVIRONMENT_VARIABLE_A", str
    >>>     NAME_OF_A_SETTING_C = "NAME_OF_AN_ENVIRONMENT_VARIABLE_C", int, lambda x: x ** 2
    >>>     NAME_OF_A_SETTING_B = "NAME_OF_AN_ENVIRONMENT_VARIABLE_B", int
    >>>     COMBINED_SETTING = (
    >>>         lambda self: int(self.NAME_OF_A_SETTING_A) + self.NAME_OF_A_SETTING_B
    >>>     )

    >>> my_conf = MyConf(NAME_OF_A_SETTING_A=2)
    >>> print(my_conf.NAME_OF_A_SETTING_A)
    >>> os.environ["NAME_OF_AN_ENVIRONMENT_VARIABLE_C"] = "3"
    >>> print(my_conf.NAME_OF_A_SETTING_C)
    >>> try:
    >>>     print(my_conf.NAME_OF_A_SETTING_B)
    >>> except ConfigurationError as e:
    >>>     print(e)
    >>> os.environ["NAME_OF_AN_ENVIRONMENT_VARIABLE_B"] = "1"
    >>> print(my_conf.NAME_OF_A_SETTING_B, type(my_conf.NAME_OF_A_SETTING_B))
    >>> print(my_conf.COMBINED_SETTING)
"""
import functools
import os
import re


class Boolean:
    def __call__(self, value):
        if isinstance(value, str):
            if not re.match(r"^true|false|0|1$", value, re.IGNORECASE):
                raise ValueError("The environment variable is not boolean convertible.")
            return bool(re.match(r"true|1", value, re.IGNORECASE))
        elif isinstance(value, bool):
            return value
        raise ValueError("The default value is not boolean convertible.")


class ConfigurationError(Exception):
    """Specific error type to indicate non-existing settings."""

    def __init__(self, var_name, setting_name):
        super(ConfigurationError, self).__init__(
            f"The environment variable is not found: {var_name}. Define the environment "
            f"variable or set a default value for the {setting_name} setting."
        )


class ConfigDefautsPasser:
    """Base class to add defaults for the settings."""

    def __init__(self, **default_settings):
        self._defaults = default_settings


class Config:
    """Metaclass for creation of neat and declarative configuration objects."""

    @staticmethod
    def _ensure_env(setting_func):
        """Check if the variable is set in the environment."""

        @functools.wraps(setting_func)
        def wrapper(self):
            try:
                res = setting_func(self)
            except KeyError:
                raise ConfigurationError(setting_func.var_name, setting_func.__name__)
            else:
                if res is None:
                    raise ConfigurationError(
                        setting_func.var_name, setting_func.__name__
                    )
                return res

        return wrapper

    @staticmethod
    def _apply_processor(processor):
        """Apply a custom setting value processor."""
        if not callable(processor):
            raise TypeError(
                "Processor should be a callable — a class or a function: {}|{}".format(
                    type(processor), processor
                )
            )

        def _apply(setting_func):
            @functools.wraps(setting_func)
            def wrapper(self):
                return processor(setting_func(self))

            return wrapper

        return _apply

    @staticmethod
    def _apply_type(type_):
        """Cast a setting to a type."""
        if not issubclass(type_, (int, float, str, bytes, bool)):
            raise TypeError(
                "Cast type must be a pure data type: int, float, str or bytes."
                "Actual type is: {}".format(type(type_))
            )

        def _apply(setting_func):
            @functools.wraps(setting_func)
            def wrapper(self):
                nonlocal type_
                if issubclass(type_, bool):
                    type_ = Boolean()
                return type_(setting_func(self))

            return wrapper

        return _apply

    @staticmethod
    def _ensure_type(setting_func):
        """Ensure that a setting after custom processing still of pure data types."""

        @functools.wraps(setting_func)
        def wrapper(self):
            res = setting_func(self)
            if not isinstance(res, (int, float, str, bytes)):
                raise TypeError(
                    "Custom setting processors must return pure "
                    "data types: int, float, str or bytes"
                )
            return res

        return wrapper

    @classmethod
    def _make_setting_prop(cls, setting_name, var_name):
        """Create a setting property"""

        def _setting_getter(self):
            if setting_name in self._defaults:
                return os.getenv(var_name, self._defaults[setting_name])
            return os.environ[var_name]  # Raise an error if no default present

        _setting_getter.var_name = var_name
        _setting_getter.__name__ = setting_name
        _setting_getter = cls._ensure_env(_setting_getter)
        return _setting_getter

    def __new__(cls, class_name, bases, attrs):
        """Create a config class from a declarative definition."""
        for setting_name, setting in attrs.items():
            if setting_name.isupper():
                if not callable(setting):
                    setting = list(setting)
                    var_name = setting.pop(0)
                    setting_type = setting.pop(0)
                    pre_processors = setting if setting else None

                    _setting_getter = cls._make_setting_prop(setting_name, var_name)
                    if pre_processors:
                        for i in pre_processors:
                            _setting_getter = cls._apply_type(setting_type)(
                                _setting_getter
                            )
                            _setting_getter = cls._apply_processor(i)(_setting_getter)
                    _setting_getter = cls._apply_type(setting_type)(_setting_getter)
                else:
                    _setting_getter = cls._ensure_type(setting)

                _setting_getter = property(_setting_getter)
                attrs[setting_name] = _setting_getter
                bases = (ConfigDefautsPasser,)

        return type(class_name, bases, attrs)
