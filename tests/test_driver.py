import pytest

from ngage.plugins.eznc import EzncDriver as Driver


def test_init():
    config = {
        "host": "localhost",
        "user": "user",
    }
    #    with pytest.raises as e:
    #        Driver(config)

    drv = Driver(config)
