#!/bin/bash

# Arguments
HOST=$1
DURATION=$2
INTERVAL=$3
SIZE=$4         # packet size (length)
OUTPUT_FILE=$5  # e.g. result.json

# Base directory is script's directory
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Paths
NMAT_DIR="$BASE_DIR/nmat"
OUTPUT_DIR="$BASE_DIR/output"
mkdir -p "$OUTPUT_DIR"
FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

# Go to nlmt inside nmat
cd "$NMAT_DIR/nlmt" || { echo "Cannot cd to nlmt directory"; exit 1; }

# Activate virtualenv
source ../nlmt_env/bin/activate

echo "Running nlmt client, saving output to $FULL_OUTPUT_PATH"

# Run nlmt client with packet size (-l SIZE) and output file (-o)
./nlmt client -i "${INTERVAL}" -l "${SIZE}" -d "${DURATION}" -o "$FULL_OUTPUT_PATH" "$HOST" 2>&1 | tee "$OUTPUT_DIR/$OUTPUT_FILE"

# Check if output saved
if [ -f "$FULL_OUTPUT_PATH" ]; then
  echo "✅ Output saved to $FULL_OUTPUT_PATH"
else
  echo "❌ Failed to save output file."
  echo "Check $OUTPUT_DIR/$OUTPUT_FILE for details."
fi

# Deactivate environment
deactivate
