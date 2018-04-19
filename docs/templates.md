
```yaml
bgp:
  as: 63311
  router_id: 208.200.137.254
  groups:
    - name: chix
      descr_prefix: "Peering: "
      import: filter bgp_in_peer_chix
      export: filter bgp_out_peer
      local_pref: 200
      neighbors:
        - asn: 42
          descr: "PCH-42"
          ip: 206.41.110.42
          max_prefix: 300
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
        - asn: 33713
          tag: rs1
          descr: "ChIX route server 1"
          ip: 206.41.110.4
          max_prefix: 200000
          export: filter bgp_out_chix_rs
          local_pref: 195
```
