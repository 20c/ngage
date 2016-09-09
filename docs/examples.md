
### Helper Scripts

These scripts, located in the `scripts/` directory, assume all config snippets are created in a directory called `gen/$hostname` and usually numbered in the order they should be executed. For example:

```
$ ls -la gen/chix0.ch2/
    
00-basesys.conf
01-chassis.conf
03-interfaces.conf
99-qfx.conf
```

#### diff.sh

```sh
{!scripts/diff.sh!}
```

#### pushone.sh

```sh
{!scripts/pushone.sh!}
```
