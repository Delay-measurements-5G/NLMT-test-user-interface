# create ui/ux here using streamlit
import streamlit as st
import os
import json
import datetime
import subprocess
import matplotlib.pyplot as plt
import statistics

# Set UI configs
st.set_page_config("NLMT 5G Test Dashboard", layout="wide")
st.title("📡 NLMT - 5G Network Test Interface")
st.markdown("This interface lets you run latency, jitter, and packet loss tests using NLMT.")

# Sidebar for test inputs
st.sidebar.header("🧪 Configure Test")

test_type = st.sidebar.selectbox("Select Test Type", ["Latency", "Jitter", "Packet Loss"])
target_hosts = st.sidebar.text_input("Target Hosts (comma-separated)", "google.com,cloudflare.com")
duration = st.sidebar.text_input("Duration (e.g., 60s)", "60s")
interval = st.sidebar.text_input("Interval (e.g., 100ms)", "100ms")
output_format = st.sidebar.selectbox("Output Format", ["json"])

run_button = st.sidebar.button("▶️ Run Test")

# Output folder setup
os.makedirs("nlmt_outputs", exist_ok=True)

def run_nlmt(hosts, dur, inter, fmt):
    output_files = []
    for host in hosts:
        host_clean = host.strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_file = f"nlmt_outputs/{host_clean}_{timestamp}.{fmt}"
        cmd = [
            "./bin/nlmt", "-t", dur, "-i", inter,
            "-j" if fmt == "json" else "-c", host_clean,
            "-o", out_file
        ]
        st.code(" ".join(cmd))
        subprocess.run(cmd)
        output_files.append(out_file)
    return output_files

def plot_graph(data):
    latencies = [m["latency_ms"] for m in data["measurements"]]
    timestamps = [m["timestamp"] for m in data["measurements"]]

    fig, ax = plt.subplots()
    ax.plot(timestamps, latencies, color='blue', marker='o')
    ax.set_title("📈 Latency Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Latency (ms)")
    st.pyplot(fig)

    if latencies:
        st.subheader("📊 Summary Stats")
        st.write({
            "Min (ms)": min(latencies),
            "Max (ms)": max(latencies),
            "Avg (ms)": round(statistics.mean(latencies), 2),
            "Jitter (std dev)": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
        })

# Run and show results
if run_button:
    hosts = [h.strip() for h in target_hosts.split(",")]
    st.info("Running tests...")
    files = run_nlmt(hosts, duration, interval, output_format)
    st.success("Test Completed ✅")

    for file in files:
        st.markdown(f"### 📁 Output: {file}")
        with open(file, 'r') as f:
            data = json.load(f)
        plot_graph(data)

# Upload section
st.markdown("## 📤 Or Upload NLMT JSON Result")
uploaded = st.file_uploader("Upload result file", type=["json"])
if uploaded:
    data = json.load(uploaded)
    st.json(data)
    plot_graph(data)
