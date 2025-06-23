#!/bin/bash

nlmt_client() {
  # Arguments
  HOST=$1
  DURATION=$2
  INTERVAL=$3
  SIZE=$4
  OUTPUT_FILE=$5

  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  NMAT_DIR="$BASE_DIR/nmat"
  OUTPUT_DIR="$BASE_DIR/output"
  mkdir -p "$OUTPUT_DIR"
  FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

  cd "$NMAT_DIR/nlmt" || { echo "❌ Cannot cd to nlmt directory"; exit 1; }

  source ../nlmt_env/bin/activate

  echo "🚀 Running nlmt client, saving output to $FULL_OUTPUT_PATH"

  ./nlmt client -i "${INTERVAL}" -l "${SIZE}" -d "${DURATION}" -o "$FULL_OUTPUT_PATH" "$HOST" 2>&1 | tee "$OUTPUT_DIR/$OUTPUT_FILE"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
    echo "Check $OUTPUT_DIR/$OUTPUT_FILE for details."
  fi

  deactivate
}

nlmt_server() {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  NMAT_DIR="$BASE_DIR/nmat"

  cd "$NMAT_DIR/nlmt" || { echo "❌ Cannot cd to nlmt directory"; exit 1; }

  source ../nlmt_env/bin/activate

  echo "🖥️ Starting nlmt server..."

  ./nlmt server

  deactivate
}

# ---------- Command Dispatcher ----------

COMMAND=$1
shift

case "$COMMAND" in
  nlmt_client)
    if [ $# -ne 5 ]; then
      echo "Usage: $0 nlmt_client <HOST> <DURATION> <INTERVAL> <SIZE> <OUTPUT_FILE>"
      exit 1
    fi
    nlmt_client "$@"
    ;;
  nlmt_server)
    nlmt_server
    ;;
  *)
    echo "Usage:"
    echo "  $0 nlmt_client <HOST> <DURATION> <INTERVAL> <SIZE> <OUTPUT_FILE>"
    echo "  $0 nlmt_server"
    ;;
esac

