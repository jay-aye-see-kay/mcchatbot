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

build-x86-image:
  echo "building x86 image..."
  nix build .#buildx86Image && ./result | docker load

build-arm64-image:
  echo "building arm64 image..."
  nix build .#buildArmImage && ./result | docker load

build-images: build-x86-image build-arm64-image

tag-and-push-images:
  #!/bin/sh
  version=$(cat version)
  docker tag "jayayeseekay/mcchatbot:latest" "jayayeseekay/mcchatbot:${version}"
  docker tag "jayayeseekay/mcchatbot:latest-arm64" "jayayeseekay/mcchatbot:${version}-arm64"
  docker push --all-tags "jayayeseekay/mcchatbot"
