
# ngage

[![PyPI version](https://badge.fury.io/py/ngage.svg)](https://badge.fury.io/py/ngage)
[![Build Status](https://travis-ci.org/20c/ngage.svg?branch=master)](https://travis-ci.org/20c/ngage)
[![Code Health](https://landscape.io/github/20c/ngage/master/landscape.svg?style=flat)](https://landscape.io/github/20c/ngage/master)
[![Codecov](https://img.shields.io/codecov/c/github/20c/ngage/master.svg?maxAge=2592000)](https://codecov.io/github/20c/ngage)
[![Requires.io](https://img.shields.io/requires/github/20c/ngage.svg?maxAge=2592000)](https://requires.io/github/20c/ngage/requirements)

network gadget config twirler


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

Apache-2.0

