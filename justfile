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

tag-and-push-image:
  #!/bin/sh
  version=$(cat version)
  docker tag "jayayeseekay/mcchatbot:latest" "jayayeseekay/mcchatbot:$version"
  docker push --all-tags "jayayeseekay/mcchatbot"
