#!/usr/bin/env bash

cd "$(dirname "$0")"

pipenv shell "$1"
