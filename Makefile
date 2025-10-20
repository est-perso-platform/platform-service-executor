SHELL := /bin/bash
.DEFAULT_GOAL := build

IMAGE ?= my-platform-agent
TAG ?= latest
DOCKERFILE ?= Dockerfile
CONTEXT ?= .
BUILD_ARGS ?=
PLATFORM ?= linux/amd64
BUILDKIT ?= 1

.PHONY: help build tag push run

help:
	@printf "Usage:\n"
	@printf "  make build IMAGE=<name> TAG=<tag> [DOCKERFILE=<file>] [CONTEXT=<dir>] [BUILD_ARGS='--build-arg KEY=VAL'] [PLATFORM=<platform>]\n"
	@printf "  make push  IMAGE=<name> TAG=<tag>\n"
	@printf "  make tag   IMAGE=<name> TAG=<tag> NEW_TAG=<new>\n"
	@printf "  make run   IMAGE=<name> TAG=<tag>\n"

build:
	@echo "Building $(IMAGE):$(TAG) from $(DOCKERFILE) (context: $(CONTEXT))"
	@DOCKER_BUILDKIT=$(BUILDKIT) docker build $(if $(PLATFORM),--platform $(PLATFORM)) -f $(DOCKERFILE) -t $(IMAGE):$(TAG) $(BUILD_ARGS) $(CONTEXT)

tag:
	@if [ -z "$(NEW_TAG)" ]; then echo "ERROR: specify NEW_TAG=<tag>"; exit 1; fi
	@docker tag $(IMAGE):$(TAG) $(IMAGE):$(NEW_TAG)
	@echo "Tagged $(IMAGE):$(TAG) as $(IMAGE):$(NEW_TAG)"

push:
	@echo "Pushing $(IMAGE):$(TAG)"
	@docker push $(IMAGE):$(TAG)

run:
	@echo "Running $(IMAGE):$(TAG)"
	@docker run --rm -it $(IMAGE):$(TAG)
