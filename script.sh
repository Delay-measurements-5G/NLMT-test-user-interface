#!/bin/bash

# --- Script Configuration ---
set -e -u -o pipefail

# --- Global Variables ---
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NMAT_DIR="$BASE_DIR/nmat"
OUTPUT_DIR="$BASE_DIR/output"
PID_DIR="$BASE_DIR/pids" # Directory to store process IDs for servers
LOG_DIR="$BASE_DIR/logs" # Directory for server logs

# Create necessary directories on script start
mkdir -p "$OUTPUT_DIR"
mkdir -p "$PID_DIR"
mkdir -p "$LOG_DIR"


# ==============================================================================
# SERVER MANAGEMENT FUNCTIONS
# ==============================================================================

iperf_server() {
  local PID_FILE="$PID_DIR/iperf_server.pid"
  local LOG_FILE="$LOG_DIR/iperf_server.log"

  echo "🖥️  Starting iPerf3 server (background mode via PID file)..."

  if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null; then
    echo "🟡 iPerf3 server is already running (PID $(cat "$PID_FILE")). Stop it first with 'stop_iperf_server'."
    return 1
  fi

  # Start iperf3 in the background, redirecting all output to a log file.
  # 'nohup' ensures it keeps running even if the script's shell is closed.
  nohup iperf3 -s -B 0.0.0.0 > "$LOG_FILE" 2>&1 &

  # Capture the Process ID (PID) of the background job and save it.
  local PID=$!
  echo $PID > "$PID_FILE"

  sleep 1 # Give it a moment to start up or fail.

  # Verify the process is actually running.
  if ps -p $PID > /dev/null; then
    echo "✅ iPerf3 server started successfully in the background (PID: $PID)."
    echo "   Log file is at: $LOG_FILE"
  else
    echo "❌ Failed to start iPerf3 server. Check the log for errors:"
    echo "-----------------------------------------------------"
    cat "$LOG_FILE"
    echo "-----------------------------------------------------"
    rm -f "$PID_FILE" # Clean up failed attempt
    return 1
  fi
}

stop_iperf_server() {
  local PID_FILE="$PID_DIR/iperf_server.pid"
  echo "🛑 Stopping iPerf3 server..."

  if [ -f "$PID_FILE" ]; then
    local PID
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
      # Use sudo to ensure we have permission to kill the process
      sudo kill "$PID"
      rm -f "$PID_FILE"
      echo "✅ iPerf3 server (PID: $PID) stopped."
    else
      echo "🟡 Stale PID file found. No process with PID $PID exists. Cleaning up."
      rm -f "$PID_FILE"
    fi
  else
    # As a fallback, try to pkill any leftovers.
    if pgrep -f "iperf3 -s" > /dev/null; then
        echo "🟡 PID file not found, but found a running iperf3 server. Killing it..."
        sudo pkill -f "iperf3 -s"
        echo "✅ iPerf3 server stopped."
    else
        echo "🟡 No iPerf3 server was running."
    fi
  fi
}

nlmt_server() {
  local PID_FILE="$PID_DIR/nlmt_server.pid"
  echo "🖥️  Starting NLMT server (background mode)..."

  if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE")" > /dev/null; then
    echo "🟡 NLMT server is already running (PID $(cat "$PID_FILE")). Stop it first with 'stop_nlmt_server'."
    return 1
  fi

  (
    cd "$NMAT_DIR/nlmt" || exit 1
    source ../nlmt_env/bin/activate
    exec nohup ./nlmt server > "$LOG_DIR/nlmt_server.log" 2>&1
  ) &

  local PID=$!
  echo $PID > "$PID_FILE"
  sleep 1

  if ps -p $PID > /dev/null; then
    echo "✅ NLMT server started successfully in the background (PID: $PID)."
  else
    echo "❌ Failed to start NLMT server."
    rm -f "$PID_FILE"
    return 1
  fi
}

stop_nlmt_server() {
  local PID_FILE="$PID_DIR/nlmt_server.pid"
  echo "🛑 Stopping NLMT server..."

  if [ -f "$PID_FILE" ]; then
    local PID
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
      sudo kill "$PID"
      rm -f "$PID_FILE"
      echo "✅ NLMT server (PID: $PID) stopped."
    else
      echo "🟡 Stale PID file found. No process with PID $PID exists. Cleaning up."
      rm -f "$PID_FILE"
    fi
  else
    echo "🟡 No NLMT server was running (PID file not found)."
  fi
}


# ==============================================================================
# CLIENT FUNCTIONS (UNCHANGED NAMES)
# ==============================================================================

run_client() {
  local DESCRIPTION="$1"; local OUTPUT_FILE="$2"; shift 2
  local FULL_OUTPUT_PATH="$OUTPUT_DIR/$OUTPUT_FILE"
  echo "🚀 Running $DESCRIPTION"
  "$@" 2>&1 | tee "$FULL_OUTPUT_PATH"
  if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "✅ Success! Output saved to $FULL_OUTPUT_PATH"
  else
    echo "❌ Command failed with exit code ${PIPESTATUS[0]}. Check log in $FULL_OUTPUT_PATH"
    return 1
  fi
}

nlmt_client() {
  (
    cd "$NMAT_DIR/nlmt" || exit 1
    source ../nlmt_env/bin/activate
    run_client "NLMT client" "$5" ./nlmt client -i "$3" -l "$4" -d "$2" -o "$OUTPUT_DIR/$5" "$1"
  )
}

iperf_client() { run_client "iPerf TCP client" "$3" iperf3 -c "$1" -J -t "$2"; }
iperf_client_reverse() { run_client "iPerf TCP client (reverse)" "$3" iperf3 -c "$1" -J -t "$2" -R; }
iperf_client_udp() { run_client "iPerf UDP client" "$4" iperf3 -c "$1" -J -t "$2" -u -b "$3"; }
iperf_client_udp_reverse() { run_client "iPerf UDP client (reverse)" "$4" iperf3 -c "$1" -J -t "$2" -u -b "$3" -R; }


# ==============================================================================
# COMMAND DISPATCHER
# ==============================================================================

if [ $# -eq 0 ]; then set -- "help"; fi
COMMAND=$1; shift

case "$COMMAND" in
  iperf_server) iperf_server ;;
  stop_iperf_server) stop_iperf_server ;;
  nlmt_server) nlmt_server ;;
  stop_nlmt_server) stop_nlmt_server ;;

  nlmt_client)
    if [ $# -ne 5 ]; then echo "Usage: $0 nlmt_client <HOST> <DUR> <INT> <SIZE> <FILE>"; exit 1; fi
    nlmt_client "$@" ;;
  iperf_client)
    if [ $# -ne 3 ]; then echo "Usage: $0 iperf_client <HOST> <DUR> <FILE>"; exit 1; fi
    iperf_client "$@" ;;
  iperf_client_reverse)
    if [ $# -ne 3 ]; then echo "Usage: $0 iperf_client_reverse <HOST> <DUR> <FILE>"; exit 1; fi
    iperf_client_reverse "$@" ;;
  iperf_client_udp)
    if [ $# -ne 4 ]; then echo "Usage: $0 iperf_client_udp <HOST> <DUR> <BW> <FILE>"; exit 1; fi
    iperf_client_udp "$@" ;;
  iperf_client_udp_reverse)
    if [ $# -ne 4 ]; then echo "Usage: $0 iperf_client_udp_reverse <HOST> <DUR> <BW> <FILE>"; exit 1; fi
    iperf_client_udp_reverse "$@" ;;

  help|*)
    echo "Usage: $0 <command> [options...]"
    echo ""
    echo "Server Commands:"
    echo "  iperf_server                 Start iPerf3 server in the background."
    echo "  stop_iperf_server            Stop background iPerf3 server."
    echo "  nlmt_server                  Start NLMT server in the background."
    echo "  stop_nlmt_server             Stop background NLMT server."
    echo ""
    echo "Client Commands:"
    echo "  (List of client commands...)"
    exit 1
    ;;
esac

#V1.2.1