#!/usr/bin/env bash

task db:seed
task data:extract
task annotations:get
task annotations:process
task statistics:tf-idf
task statistics:topics
task statistics:dashboard

uv run comp370
