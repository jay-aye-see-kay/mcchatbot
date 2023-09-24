#!/bin/sh

set -e

nix build .#dockerImage
docker load < result
