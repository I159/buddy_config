# buddy_config
Decoupled and lazy library to get settings from an environment variables.

## Motivation
Environment variables are the most common way to configure projects, based on Docker, hosted on clouds, e.t.c. In the end, it is a secure and simple way. So grab variables from an environment is the only feature of the package.

The first issue that becomes obvious at the simplest approach for getting environment variables is attempting to get the environment variables too early. For example, an app is initialized by tests, and you need different values for the settings at different tests. But if the values obtained in this way:

__init__.py
```
import os

VAR_A = os.environ['VAR_A']
```

module_a.py

```
from . import *

def a():
    b(VAR_A)
```

test.py
```
from . import module_a

class Test(unittest.TestCase):
    @mock.patch('os', 'environ', {"VAR_A": 1})
    def test_a(self, env):
        ...
```

The values are already loaded to the memory. Therefore mock will not work. And the saddest part that this issue is not solved in most of the advanced configuration libraries. So this is the first issue solved here by Buddy Config.

## Installation

    pip install buddy_config

## Getting started

Buddy Config aims to be as declarative as possible.

    import buddy_config


    class MyConf(metaclass=buddy_config.Config):
        NAME_OF_A_SETTING_A = "NAME_OF_AN_ENVIRONMENT_VARIABLE_A", str

This is a minimum of declaration that you need to have a setting. Let's pale it out. The name of a class attribute is the name of the setting, exactly how you suppose to call it. A string at position 0 of the following tuple is a name of an environment variable that you will retrieve from the environment. And the type class at position 1 of the tuple is the type value after it is retrieved from the environment. Both values are required.

To use the config, you need to instantiate it:


    my_conf = MyConfig()

*The value is not going to be retrieved until you actually get the attribute from the 
config.*

    print(my_config.NAME_OF_A_SETTING_A)

Also it is not cached.

    os.environ["NAME_OF_AN_ENVIRONMENT_VARIABLE_A"] = "3"
    print(my_config.NAME_OF_A_SETTING_A)

Defaults are flexible and could be different per instance of the config.

    my_conf_a = MyConfig(NAME_OF_A_SETTING_A=1)
    my_conf_b = MyConfig(NAME_OF_A_SETTING_A=2)

    print(my_conf_a.NAME_OF_A_SETTING_A)
    print(my_conf_b.NAME_OF_A_SETTING_A)

Moreover, you can add pre-processing of retrieved values.


    class MyConf(metaclass=Config):
        NAME_OF_A_SETTING_C = "NAME_OF_AN_ENVIRONMENT_VARIABLE_C", int, lambda x: x ** 2

The optional items of the tuple are pre-processors. A pre-processor is a callable that must return a value of int, float, string, or bytes value.

If you need to create a combined setting using values from environment variables, no problem, buddy config can do that:


    class MyConf(metaclass=Config):
        NAME_OF_A_SETTING_A = "NAME_OF_AN_ENVIRONMENT_VARIABLE_A", str
        NAME_OF_A_SETTING_B = "NAME_OF_AN_ENVIRONMENT_VARIABLE_B", int
        COMBINED_SETTING = (
            lambda self: int(self.NAME_OF_A_SETTING_A) + self.NAME_OF_A_SETTING_B
        )
