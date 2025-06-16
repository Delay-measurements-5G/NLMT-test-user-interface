import streamlit as st
import subprocess
import threading
import time
import json
import gzip
import glob
import os
import uuid

# CONFIGURATION
DEFAULT_SERVER = "irtt.heistp.net"
DEFAULT_HMAC = "irttuser"
NLMT_PATH = " "  # PATH for where NLMT is installed

# Run nlmt subprocess
def run_nlmt(server, hmac_key, duration_sec, output_dir, output_callback):
    cmd = [
        NLMT_PATH, "client",
        "--hmac", hmac_key,
        "-d", f"{duration_sec}s",
        "-o", "d",
        f"--outdir={output_dir}",
        server
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in iter(process.stdout.readline, ''):
        output_callback(line.strip())

    process.wait()

# Get latest generated json file inside the output directory
def get_latest_json(output_dir):
    files = sorted(glob.glob(os.path.join(output_dir, 'cl_*.json.gz')), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

# Parse and display json result
def parse_and_show_json(json_file):
    with gzip.open(json_file, 'rt') as f:
        data = json.load(f)

    st.subheader("📊 Final Summary Results:")
    if "summary" in data:
        for metric, values in data["summary"].items():
            st.write(f"### {metric}")
            for stat, val in values.items():
                st.write(f"- {stat}: {val}")
    else:
        st.write("⚠ No summary found in the JSON file")

# Streamlit UI starts here
st.title("🌐 NLMT Network Latency Measurement Tool")

# Input form
with st.form("nlmt_form"):
    duration = st.number_input("Test Duration (seconds)", min_value=10, max_value=600, value=60, step=10)
    server = st.text_input("NLMT Server", value=DEFAULT_SERVER)
    hmac_key = st.text_input("HMAC Key", value=DEFAULT_HMAC)
    submitted = st.form_submit_button("Start Test")

if submitted:
    # Create a unique directory for this run
    unique_outdir = os.path.join("/tmp/", str(uuid.uuid4()))
    os.makedirs(unique_outdir, exist_ok=True)

    st.write(f"🚀 Starting NLMT Test for {duration} seconds...")
    st.write(f"Using output directory: {unique_outdir}")

    # Output box for real-time logs
    output_box = st.empty()

    def stream_output_callback(line):
        output_box.text(line)

    # Start the subprocess in separate thread
    thread = threading.Thread(target=run_nlmt, args=(server, hmac_key, duration, unique_outdir, stream_output_callback))
    thread.start()

    # While the test is running, keep UI responsive
    while thread.is_alive():
        time.sleep(1)

    st.success("✅ Test Completed!")

    # Wait briefly to ensure file system is flushed
    time.sleep(2)

    # Attempt to locate and parse output JSON file
    latest_json = get_latest_json(unique_outdir)
    if latest_json:
        st.write(f"Parsing result file: {latest_json}")
        parse_and_show_json(latest_json)
    else:
        st.error("❌ No JSON result file found in output directory!")
