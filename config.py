"""Declarative, lazy and decoupled configuration form environment variables.

Buddy-Config allows to use environment variables in lazy and flexible way. Load
a config settings exactly when they are needed but not at import. Define non-global
defaults. Default values could be different for the same config in each its instance.
Use declarative style.

Examples:

    >>> class MyConf(metaclass=Config):
    >>>     NAME_OF_A_SETTING_A = "NAME_OF_AN_ENVIRONMENT_VARIABLE_A"
    >>>     NAME_OF_A_SETTING_C = "NAME_OF_AN_ENVIRONMENT_VARIABLE_C"
    >>>     NAME_OF_A_SETTING_B = "NAME_OF_AN_ENVIRONMENT_VARIABLE_B", int

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

"""
import functools
import inspect
import os


class ConfigurationError(Exception):
    """Specific error type to indicate non-existing settings."""

    def __init__(self, var_name, setting_name):
        super(ConfigurationError, self).__init__(
            f"The environment variable is not found: {var_name}. Define the environment "
            f"variable or set a default value for the {setting_name} setting."
        )


class ConfigDefautsPasser:
    def __init__(self, **default_settings):
        self._defaults = default_settings


class Config:
    """Metaclass for creation of neat and declarative configuration objects."""

    @staticmethod
    def _ensure_env(setting_func):
        @functools.wraps(setting_func)
        def wrapper(self):
            try:
                res = setting_func(self)
            except KeyError:
                raise ConfigurationError(setting_func.var_name, setting_func.__name__)
            else:
                if not res:
                    raise ConfigurationError(
                        setting_func.var_name, setting_func.__name__
                    )
                return res

        return wrapper

    @staticmethod
    def _cast_as(cst_type):
        if not inspect.isclass(cst_type):
            raise TypeError(f"Casting type must be a class: {cst_type}")

        def _cast(setting_func):
            @functools.wraps(setting_func)
            def wrapper(self):
                return cst_type(setting_func(self))

            return wrapper

        return _cast

    @classmethod
    def _make_setting_prop(cls, setting_name, var_name):
        def _setting_getter(self):
            if setting_name in self._defaults:
                return os.environ.get(var_name, self._defaults[setting_name])
            return os.environ[var_name]

        _setting_getter.var_name = var_name
        _setting_getter.__name__ = setting_name
        _setting_getter = cls._ensure_env(_setting_getter)
        return _setting_getter

    def __new__(cls, class_name, bases, attrs):
        for setting_name, v in attrs.items():
            if setting_name.isupper():
                if isinstance(v, tuple):
                    var_name, cast_type = v
                elif isinstance(v, str):
                    var_name = v
                    cast_type = None

                if not callable(v):
                    _setting_getter = cls._make_setting_prop(setting_name, var_name)
                    if cast_type:
                        _setting_getter = cls._cast_as(cast_type)(_setting_getter)
                else:
                    _setting_getter = v
                _setting_getter = property(_setting_getter)
                attrs[setting_name] = _setting_getter
                bases = (ConfigDefautsPasser,)

        return type(class_name, bases, attrs)
