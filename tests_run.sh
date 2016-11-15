#!/usr/bin/env bash

cd lambda-cron; python -m pytest tests/
cd ../cli; python -m pytest tests/