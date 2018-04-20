

### Global

### BGP config

Nested under the `bgp` variable, is a `groups` list containing peers


Example in YAML:

```yaml
bgp:
  asn: 63311
  router_id: 208.200.137.254
  groups:
    - name: chix
      descr_prefix: "Peering: "
      import_policy: bgp_in_peer_chix
      export_policy: bgp_out_peer
      local_pref: 200
      neighbors:
        - asn: 42
          descr: "PCH-42"
          ip: 206.41.110.42
          max_prefix: 600
        - asn: 42
          descr: "PCH-42"
          ip: 2001:504:41:110::42
          max_prefix: 600
        - asn: 15169
          descr: "Google"
          ip: 206.41.110.37
          max_prefix: 15000
          password: secure
        - asn: 33713
          tag: rs0
          descr: "ChIX route server 0"
          ip: 206.41.110.66
          max_prefix: 200000
          export: filter bgp_out_chix_rs
          local_pref: 195
          med: 100
        - asn: 33713
          tag: rs1
          descr: "ChIX route server 1"
          ip: 206.41.110.4
          max_prefix: 200000
          export: filter bgp_out_chix_rs
          local_pref: 195
```
