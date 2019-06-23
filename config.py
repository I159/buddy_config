import functools
import inspect
import os
from collections import namedtuple


class Setting:
    name = None
    cast_type = None

    def __init__(self, name, cast_type=None):
        self.name = name
        if cast_type:
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


class ConfigDefautsPasser:
    def __init__(self, **default_settings):
        self._defaults = default_settings


class Config:
    _defaults = {}

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
                # FIXME: save setting to a dict and then operate on separate Setting instances.
                setting = (
                    Setting(*attrs[name])
                    if isinstance(attrs[name], tuple)
                    else Setting(attrs[name])
                )

                def _setting_getter(self):
                    # FIXME: save setting to a dict and then operate on separate Setting instances.
                    if setting.name in self._defaults:
                        return os.environ.get(
                            setting.name, self._defaults[setting.name]
                        )
                    return os.environ[setting.name]

                _setting_getter.__name__ = name
                _setting_getter.var_name = setting
                attrs[name] = cls._ensure_env(_setting_getter)
                if setting.cast_type:
                    attrs[name] = cls._cast_as(setting.cast_type)(attrs[name])
                # attrs[name] = property(attrs[name])
                bases = (ConfigDefautsPasser,)

        return type(class_name, bases, attrs)


if __name__ == "__main__":

    class MyConf(metaclass=Config):
        AAA = "AAAa"
        BBB = "BBBb", int

    my_conf = MyConf(AAA=2)
    my_conf.AAA()
