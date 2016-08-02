
# Use with Ansible

## Output files from ansible

With output variable set to where you want it to go, for example
```
generated_config_dir: gen
config_output_dir: "{{config_output_dir}}/{{inventory_hostname}}"
```

```
- name: building configuration
  template: >
    src={{item.1}}.conf
    dest={{config_output_dir}}/{{'%02d' % item.0}}-{{item.1}}.conf
  with_indexed_items:
    - common
    - chassis
    - interfaces

- name: building platform specific configuration
  template: >
    src={{basesys.platform.name}}.conf
    dest="{{config_output_dir}}/99-{{basesys.platform.name}}.conf"
```


## Run deploy with ngage

pushone.sh
```
#!/bin/bash

hostname=$1
shift

if test -z "$hostname"; then
  echo 'usage, pushone <hostname> [OPTIONS]'
  exit 1
fi

ngage push $hostname gen/$hostname/* $@
```

You can then run `./pushone.sh $hostname --diff` to see changes or `./pushone.sh $hostname --commit` to push changes.


