import streamlit as st
import os
import json
import datetime
import subprocess
import matplotlib.pyplot as plt
import statistics

st.set_page_config("📡 NLMT 5G Test Automation Dashboard", layout="wide")
st.title("📡 NLMT - 5G Network Test Automation Interface")
st.markdown("An all-in-one interface to run and analyze delay, jitter, and packet loss using **NLMT** on the 5G commercial setup.")

# Sidebar configuration
st.sidebar.header("🛠️ Configure Your Test")
target_hosts = st.sidebar.text_input("Target Host (e.g., 0.0.0.0:2112)", "0.0.0.0:2112")
duration = st.sidebar.text_input("Test Duration (e.g., 6s)", "6s")
interval = st.sidebar.text_input("Send Interval (e.g., 100ms)", "100ms")
packet_size = st.sidebar.text_input("Packet Size (bytes)", "100")
output_file = st.sidebar.text_input("Output Filename (e.g., result.json)", "result.json")
run_test = st.sidebar.button("▶️ Run Test")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

def run_nlmt(hosts, dur, inter, size, out_file):
    for host in hosts:
        host_clean = host.strip()
        cmd = [
            "./script.sh",
            host_clean,
            dur,
            inter,
            size,
            out_file
        ]
        st.code("Running: " + " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Test for {host_clean} failed: {e}")

def analyze_and_plot(data, host):
    st.subheader(f"📊 Results for `{host}`")

    round_trips = data.get("round_trips", [])
    if not round_trips:
        st.warning("No data found in `round_trips`.")
        return

    # Extract RTT delay in milliseconds
    delays_ms = [entry["delay"]["rtt"] / 1e6 for entry in round_trips if "delay" in entry and entry["delay"].get("rtt") is not None]
    seqnos = [entry["seqno"] for entry in round_trips if "delay" in entry and entry["delay"].get("rtt") is not None]

    if not delays_ms:
        st.warning("No valid RTT delays found in data.")
        return

    # Plot RTT delay graph
    fig, ax = plt.subplots()
    ax.plot(seqnos, delays_ms, marker='o', color='mediumseagreen')
    ax.set_title("📈 Round-Trip Delay Over Sequence Number")
    ax.set_xlabel("Packet Sequence Number")
    ax.set_ylabel("RTT Delay (ms)")
    st.pyplot(fig)

    # Show statistical summary
    st.markdown("#### 📋 Summary")
    st.write({
        "Min RTT (ms)": round(min(delays_ms), 2),
        "Max RTT (ms)": round(max(delays_ms), 2),
        "Average RTT (ms)": round(statistics.mean(delays_ms), 2),
        "Jitter (std dev, ms)": round(statistics.stdev(delays_ms), 2) if len(delays_ms) > 1 else 0,
        "Total Packets": len(delays_ms)
    })

# Run test
if run_test:
    st.info("Test started...")
    hosts = [h.strip() for h in target_hosts.split(",")]
    run_nlmt(hosts, duration, interval, packet_size, output_file)
    st.success("✅ Test completed!")

    try:
        with open(f"output/{output_file}", "r") as f:
            result_data = json.load(f)
            analyze_and_plot(result_data, hosts[0])
    except Exception as e:
        st.error(f"Error reading result file: {e}")

# Upload past result
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

