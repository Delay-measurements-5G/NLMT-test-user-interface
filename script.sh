#!/bin/bash

nlmt_client() {
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

  echo "🚀 Running NLMT client, saving output to $FULL_OUTPUT_PATH"
  ./nlmt client -i "$INTERVAL" -l "$SIZE" -d "$DURATION" -o "$FULL_OUTPUT_PATH" "$HOST" 2>&1 | tee "$FULL_OUTPUT_PATH"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
  fi

  deactivate
}

nlmt_server() {
  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  NMAT_DIR="$BASE_DIR/nmat"

  cd "$NMAT_DIR/nlmt" || { echo "❌ Cannot cd to nlmt directory"; exit 1; }
  source ../nlmt_env/bin/activate

  echo "🖥️ Starting NLMT server..."
  ./nlmt server

  deactivate
}

iperf_client() {
  HOST=$1
  DURATION=$2
  OUTPUT_FILE=$3

  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  OUTPUT_DIR="$BASE_DIR/output"
  mkdir -p "$OUTPUT_DIR"
  FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

  echo "🚀 Running iPerf TCP client to $HOST for $DURATION seconds"
  iperf3 -c "$HOST" -J -t "$DURATION" 2>&1 | tee "$FULL_OUTPUT_PATH"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
  fi
}

iperf_client_reverse() {
  HOST=$1
  DURATION=$2
  OUTPUT_FILE=$3

  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  OUTPUT_DIR="$BASE_DIR/output"
  mkdir -p "$OUTPUT_DIR"
  FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

  echo "🚀 Running iPerf TCP client in reverse mode to $HOST for $DURATION seconds"
  iperf3 -c "$HOST" -J -t "$DURATION" -R 2>&1 | tee "$FULL_OUTPUT_PATH"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
  fi
}

iperf_client_udp() {
  HOST=$1
  DURATION=$2
  BANDWIDTH=$3
  OUTPUT_FILE=$4

  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  OUTPUT_DIR="$BASE_DIR/output"
  mkdir -p "$OUTPUT_DIR"
  FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

  echo "🚀 Running iPerf UDP client to $HOST for $DURATION seconds at $BANDWIDTH bandwidth"
  iperf3 -c "$HOST" -J -t "$DURATION" -u -b "$BANDWIDTH" 2>&1 | tee "$FULL_OUTPUT_PATH"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
  fi
}

iperf_client_udp_reverse() {
  HOST=$1
  DURATION=$2
  BANDWIDTH=$3
  OUTPUT_FILE=$4

  BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  OUTPUT_DIR="$BASE_DIR/output"
  mkdir -p "$OUTPUT_DIR"
  FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

  echo "🚀 Running iPerf UDP client in reverse mode to $HOST for $DURATION seconds at $BANDWIDTH bandwidth"
  iperf3 -c "$HOST" -J -t "$DURATION" -u -b "$BANDWIDTH" -R 2>&1 | tee "$FULL_OUTPUT_PATH"

  if [ -f "$FULL_OUTPUT_PATH" ]; then
    echo "✅ Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Failed to save output file."
  fi
}

iperf_server() {
  echo "🖥️ Starting iPerf3 server..."
  iperf3 -s
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
  iperf_client)
    if [ $# -ne 3 ]; then
      echo "Usage: $0 iperf_client <HOST> <DURATION> <OUTPUT_FILE>"
      exit 1
    fi
    iperf_client "$@"
    ;;
  iperf_client_reverse)
    if [ $# -ne 3 ]; then
      echo "Usage: $0 iperf_client_reverse <HOST> <DURATION> <OUTPUT_FILE>"
      exit 1
    fi
    iperf_client_reverse "$@"
    ;;
  iperf_client_udp)
    if [ $# -ne 4 ]; then
      echo "Usage: $0 iperf_client_udp <HOST> <DURATION> <BANDWIDTH> <OUTPUT_FILE>"
      exit 1
    fi
    iperf_client_udp "$@"
    ;;
  iperf_client_udp_reverse)
    if [ $# -ne 4 ]; then
      echo "Usage: $0 iperf_client_udp_reverse <HOST> <DURATION> <BANDWIDTH> <OUTPUT_FILE>"
      exit 1
    fi
    iperf_client_udp_reverse "$@"
    ;;
  iperf_server)
    iperf_server
    ;;
  *)
    echo "Usage:"
    echo "  $0 nlmt_client <HOST> <DURATION> <INTERVAL> <SIZE> <OUTPUT_FILE>"
    echo "  $0 nlmt_server"
    echo "  $0 iperf_client <HOST> <DURATION> <OUTPUT_FILE>"
    echo "  $0 iperf_client_reverse <HOST> <DURATION> <OUTPUT_FILE>"
    echo "  $0 iperf_client_udp <HOST> <DURATION> <BANDWIDTH> <OUTPUT_FILE>"
    echo "  $0 iperf_client_udp_reverse <HOST> <DURATION> <BANDWIDTH> <OUTPUT_FILE>"
    echo "  $0 iperf_server"
    exit 1
    ;;
esac

