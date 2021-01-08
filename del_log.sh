#!/bin/bash


find . -name "*.log*" | xargs rm -rf
find . -name "*.lock" | xargs rm -rf
find ./test_results/   -name "*.txt" | xargs rm -rf
