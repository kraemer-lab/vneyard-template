#!/usr/bin/env bash
#
# This script is used to test the pipeline
#
# We use a script to provide maximum flexibility in testing (remove old results, etc.)
# though they will generally call snakemake to execute the _test rule with a
# test configuration file.

# Remove any old results
rm -rf results/out

# Run the pipeline, specifying a test configuration file and target rule `_test`
snakemake --cores 1 --configfile=config/.test.yaml _test
