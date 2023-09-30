default:
  just --list

check-formatting:
  isort . --check-only
  black . --check

format:
  isort .
  black .

test:
  python -m unittest

build-image:
  nix build .#dockerImage
  docker load < result
