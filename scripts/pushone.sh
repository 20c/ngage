#!/bin/bash

set -x
hostname=$1
shift

if test -z "$hostname"; then
  echo 'usage, pushone <hostname> [OPTIONS]'
  exit 1
fi

ngage push $hostname gen/$hostname/* $@

