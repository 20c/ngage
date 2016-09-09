#!/bin/bash

set -x
hostname=$1
shift

if test -z "$hostname"; then
  echo "usage, $0 <hostname> [OPTIONS]"
  exit 1
fi

ngage push --diff --no-commit $hostname gen/$hostname/* $@
ngage rollback $hostname

