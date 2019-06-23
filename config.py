import functools
import inspect
import os
from collections import namedtuple


class Setting:
    def __init__(self, name, default=None, cast_type=None):
        self.name = name
        self.default = default
        if inspect.isclass(cast_type):
            self.cast_type = cast_type
        else:
            raise TypeError(f"{cast_type} is not a class.")


class ConfigurationError(Exception):
    def __init__(self, var_name):
        super(ConfigurationError, self).__init__(
            f"The environment variable is not found: {var_name}. Define the environment "
            "variable or set a default value for the setting."
        )


class Config:
    @staticmethod
    def _ensure_env(setting_func):
        @functools.wraps(setting_func)
        def wrapper(self):
            try:
                res = setting_func(self)
            except KeyError:
                raise ConfigurationError(setting_func.var_name)
            else:
                if not res:
                    raise ConfigurationError(setting_func.var_name)
                return res

        return wrapper

    @staticmethod
    def _cast_as(cst_type):
        def _cast(setting_func):
            @functools.wraps(setting_func)
            def wrapper(self):
                return cst_type(setting_func(self))

            return wrapper

        return _cast

    def __new__(cls, class_name, bases, attrs):
        for name in attrs:
            if name.isupper():
                setting = Setting(*attrs[name])

                if setting.default:

                    def _setting_getter(self):
                        return os.environ.get(setting.name, setting.default)

                else:

                    def _setting_getter(self):
                        return os.environ[setting.name]

                _setting_getter.__name__ = name
                _setting_getter.var_name = setting
                attrs[name] = cls._ensure_env(_setting_getter)
                if setting.cast_type:
                    attrs[name] = cls._cast_as(setting.cast_type)(attrs[name])

        return type(class_name, bases, attrs)
