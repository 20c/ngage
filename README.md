
# ngage

[![PyPI](https://img.shields.io/pypi/v/ngage.svg?maxAge=3600)](https://pypi.python.org/pypi/ngage)
[![PyPI](https://img.shields.io/pypi/pyversions/ngage.svg?maxAge=3600)](https://pypi.python.org/pypi/ngage)
[![Tests](https://github.com/20c/ngage/workflows/tests/badge.svg)](https://github.com/20c/ngage)
[![Codecov](https://img.shields.io/codecov/c/github/20c/ngage/master.svg?maxAge=3600)](https://codecov.io/github/20c/ngage)

network gadget automation glorious environment


## Synopsis

This is a joining of various automation scripts I've used in various places. As I switch things over to use this, I'll merge features and probably change some interfaces. Currently it should be considered a beta script as code is merged and tested. All components are used in production, but obviously the merge process may introduce bugs and growing pains.


## Usage

```
Usage: ngage [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  commit    commit changes on a device
  config    view and interact with the config
  diff      get diff from device
  pull      pull config from a device
  push      push config to a device
  rollback  rollback device config
```

### Common Options

```
Options:
  --quiet                     no output at all
  --verbose                   enable more verbose output
  --home TEXT                 specify the home directory,
                              by default will check in order:
                                  $NGAGE_HOME,
                                  ./.ngage,
                                  ~/.config/ngage
  --debug                     enable extra debug output
```

### Connection Options

```
Options:
  --user TEXT                 username
  --password TEXT             password to use if not using key auth
  --type TEXT                 type of connection, default eznc
  --port TEXT                 port to connect to, default per platform
```

If auth fails, it will prompt for passowrd, for initial config to push users and ssh keys, you could do:

```
ngage push 00-system.conf --user=root $HOSTNAME
```

### push

```
Usage: ngage push [OPTIONS] HOST [FILES]...

  push config to a device

Options:
  --quiet                     no output at all
  --verbose                   enable more verbose output
  --home TEXT                 specify the home directory, by default will
                              check in order: $NGAGE_HOME, ./.ngage,
                              /home/grizz/.config/ngage
  --debug                     enable extra debug output
  --password TEXT             password to use if not using key auth
  --user TEXT                 username
  --type TEXT                 type of connection, default eznc
  --port TEXT                 port to connect to, default per platform
  --check / --no-check        commit check config
  --commit / --no-commit      commit changes
  --diff / --no-diff          show diff of changes
  --lock / --no-lock          lock config for exclusive access
  --rollback / --no-rollback  rollback changes after push
  --help                      Show this message and exit.
```


### pull

```
Usage: ngage pull [OPTIONS] HOST [FILENAME]

  pull config from a device

Options:
  --quiet            no output at all
  --verbose          enable more verbose output
  --home TEXT        specify the home directory, by default will check in
                     order: $NGAGE_HOME, ./.ngage, /home/grizz/.config/ngage
  --debug            enable extra debug output
  --password TEXT    password to use if not using key auth
  --user TEXT        username
  --type TEXT        type of connection, default eznc
  --port TEXT        port to connect to, default per platform
  --output-dir TEXT  directory to save file to, will be named from filename
                     option
  --help             Show this message and exit.
```

### Utility functions

Useful for debugging, working on device “directly” with a git log.

```
  commit    commit changes on a device
  diff      get diff from device
  rollback  rollback device config
```

## Supported Devices

By default ngage uses a native Junos client written with eznc, it also suppots
pushing config via a [NAPALM](http://napalm.readthedocs.io/en/latest/) plugin. To specify a NAPALM driver, use `type=napalm:$driver`, for example `type=napalm:ios`


## Documentation

Documentation is created with mkdocs and available at <http://ngage.readthedocs.io/en/latest/>


## License

Copyright 2015-2021 20C, LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this softare except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
