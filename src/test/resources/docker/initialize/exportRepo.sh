#!/usr/bin/env bash

cd /data/src/test/resources/docker/initialize/cis
rm configuration-items.xml
/opt/xld/cli/bin/cli.sh -username admin -password admin -f /data/src/test/resources/docker/initialize/exportCIs.py

