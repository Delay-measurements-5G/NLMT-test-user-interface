import streamlit as st
import os
import json
import datetime
import subprocess
import matplotlib.pyplot as plt
import statistics

st.set_page_config("📡 NLMT 5G Test Automation Dashboard", layout="wide")
st.title("📡 NLMT - 5G Network Test Automation Interface")
st.markdown("An all-in-one interface to run and analyze latency, jitter, and packet loss using **NLMT** on the 5G commercial setup.")

# Sidebar configuration
st.sidebar.header("🛠️ Configure Your Test")
test_type = st.sidebar.selectbox("Select Test Type", ["Latency", "Jitter", "Packet Loss", "All"])
target_hosts = st.sidebar.text_input("Target Hosts (comma-separated)", "google.com,cloudflare.com")
duration = st.sidebar.text_input("Duration (e.g., 60s)", "60s")
interval = st.sidebar.text_input("Interval (e.g., 100ms)", "100ms")

run_test = st.sidebar.button("▶️ Run Test")

# Ensure output directory exists
os.makedirs("nlmt_outputs", exist_ok=True)

def run_nlmt(hosts, dur, inter):
    output_files = []
    for host in hosts:
        host_clean = host.strip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_file = f"nlmt_outputs/{host_clean}_{timestamp}.json"
        cmd = ["./bin/nlmt", "-t", dur, "-i", inter, "-j", host_clean, "-o", out_file]
        st.code("Running: " + " ".join(cmd))
        subprocess.run(cmd)
        output_files.append(out_file)
    return output_files

def analyze_and_plot(data, host):
    st.subheader(f"📊 Results for `{host}`")
    measurements = data.get("measurements", [])
    if not measurements:
        st.warning("No data to analyze.")
        return

    latencies = [m.get("latency_ms", 0) for m in measurements]
    timestamps = [m.get("timestamp") for m in measurements]

    # Plot graph
    fig, ax = plt.subplots()
    ax.plot(timestamps, latencies, marker='o', color='dodgerblue')
    ax.set_title("📈 Latency Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Latency (ms)")
    st.pyplot(fig)

    # Show summary
    if latencies:
        st.markdown("#### 📋 Summary")
        st.write({
            "Min Latency (ms)": round(min(latencies), 2),
            "Max Latency (ms)": round(max(latencies), 2),
            "Average Latency (ms)": round(statistics.mean(latencies), 2),
            "Jitter (std dev)": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
            "Total Packets": len(latencies)
        })

# Run selected tests
if run_test:
    st.info("Test started...")
    hosts = [h.strip() for h in target_hosts.split(",")]
    files = run_nlmt(hosts, duration, interval)
    st.success("✅ Test completed!")

    for file in files:
        host_name = os.path.basename(file).split("_")[0]
        st.markdown(f"### 📁 Output: `{file}`")
        with open(file, "r") as f:
            result_data = json.load(f)
            analyze_and_plot(result_data, host_name)

# Upload previous result
st.markdown("---")
st.markdown("## 📤 Upload NLMT Result (JSON)")
uploaded_file = st.file_uploader("Upload `.json` result", type=["json"])
if uploaded_file:
    try:
        data = json.load(uploaded_file)
        host_name = uploaded_file.name.split("_")[0]
        analyze_and_plot(data, host_name)
    except Exception as e:
        st.error(f"Error loading file: {e}")
