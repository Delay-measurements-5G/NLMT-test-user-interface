import streamlit as st
import os
import json
import subprocess
import matplotlib.pyplot as plt
import statistics

st.set_page_config("NetTester : 5G Test Automation Dashboard", layout="wide")
st.title("📡 5G Network Testing Automation Interface : NetTester")
st.markdown("Choose between running **NLMT** or **iPerf** for analyzing network performance.")

# Mode selection
mode = st.sidebar.radio("Select Test Mode", ["NLMT", "iPerf"])

# Shared Configuration Inputs
st.sidebar.markdown("### 🌐 General Test Parameters")
target_hosts = st.sidebar.text_input("Target Host (e.g., 0.0.0.0:2112)", "0.0.0.0:2112")
duration = st.sidebar.text_input("Test Duration (e.g., 6s or 10)", "6s")

# Only show packet size & interval in NLMT mode
if mode == "NLMT":
    interval = st.sidebar.text_input("Send Interval (e.g., 100ms)", "100ms")
    packet_size = st.sidebar.text_input("Packet Size (bytes)", "100")
else:
    interval = None
    packet_size = None

output_file = st.sidebar.text_input("Output Filename (e.g., result.json)", "result.json")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# --------------------------- NLMT MODE --------------------------- #
if mode == "NLMT":
    st.sidebar.header("🛠️ NLMT Controls")
    run_test = st.sidebar.button("▶️ Run NLMT Client Test")
    run_server = st.sidebar.button("🖥️ Start NLMT Server")

    def run_nlmt_client(hosts, dur, inter, size, out_file):
        for host in hosts:
            cmd = ["./script.sh", "nlmt_client", host.strip(), dur, inter, size, out_file]
            st.code("Running: " + " ".join(cmd))
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                st.error(f"Client test for {host} failed: {e}")

    def run_nlmt_server():
        cmd = ["./script.sh", "nlmt_server"]
        st.code("Running: " + " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
            st.success("✅ Server started successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Failed to start server: {e}")

    def analyze_and_plot(data, host):
        st.subheader(f"📊 Results for `{host}`")
        round_trips = data.get("round_trips", [])
        if not round_trips:
            st.warning("No data found in `round_trips`.")
            return

        delays_ms = [entry["delay"]["rtt"] / 1e6 for entry in round_trips if "delay" in entry and entry["delay"].get("rtt") is not None]
        seqnos = [entry["seqno"] for entry in round_trips if "delay" in entry and entry["delay"].get("rtt") is not None]

        if not delays_ms:
            st.warning("No valid RTT delays found in data.")
            return

        fig, ax = plt.subplots()
        ax.plot(seqnos, delays_ms, marker='o', color='mediumseagreen')
        ax.set_title("📈 Round-Trip Delay Over Sequence Number")
        ax.set_xlabel("Packet Sequence Number")
        ax.set_ylabel("RTT Delay (ms)")
        st.pyplot(fig)

        st.markdown("#### 📋 Summary")
        st.write({
            "Min RTT (ms)": round(min(delays_ms), 2),
            "Max RTT (ms)": round(max(delays_ms), 2),
            "Average RTT (ms)": round(statistics.mean(delays_ms), 2),
            "Jitter (std dev, ms)": round(statistics.stdev(delays_ms), 2) if len(delays_ms) > 1 else 0,
            "Total Packets": len(delays_ms)
        })

    if run_test:
        st.info("🚀 Starting NLMT client test...")
        hosts = [h.strip() for h in target_hosts.split(",")]
        run_nlmt_client(hosts, duration, interval, packet_size, output_file)
        st.success("✅ NLMT client test completed!")

        try:
            with open(f"output/{output_file}", "r") as f:
                result_data = json.load(f)
                analyze_and_plot(result_data, hosts[0])
        except Exception as e:
            st.error(f"Error reading result file: {e}")

    if run_server:
        st.info("🖥️ Starting NLMT server...")
        run_nlmt_server()

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

# --------------------------- iPerf MODE --------------------------- #
else:
    st.sidebar.header("⚙️ iPerf Controls")
    use_udp = st.sidebar.checkbox("Use UDP", False)
    use_reverse = st.sidebar.checkbox("Enable Reverse Mode", False)
    run_iperf_client = st.sidebar.button("▶️ Run iPerf Client")
    run_iperf_server = st.sidebar.button("🖥️ Start iPerf Server")

    bandwidth = st.sidebar.text_input("Bandwidth (e.g., 10M)", "10M") if use_udp else None

    def analyze_iperf_json(file_path):
        if not os.path.exists(file_path):
            st.warning("⚠️ iPerf output file not found for analysis.")
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            st.error(f"Error reading iPerf JSON output: {e}")
            return

        intervals = data.get("intervals")
        if intervals is None:
            intervals = data.get("end", {}).get("streams", [])
            if not intervals:
                st.warning("No valid throughput data found in JSON.")
                return

        seq_numbers = []
        throughputs = []

        if isinstance(intervals, list) and "streams" in intervals[0]:
            for i, interval in enumerate(intervals):
                total_bps = sum(stream.get("bits_per_second", 0) for stream in interval["streams"])
                seq_numbers.append(i + 1)
                throughputs.append(total_bps / 1e6)
        elif isinstance(intervals, list):
            for i, stream in enumerate(intervals):
                bps = stream.get("bits_per_second", 0)
                seq_numbers.append(i + 1)
                throughputs.append(bps / 1e6)

        if not throughputs:
            st.warning("No throughput data found.")
            return

        fig, ax = plt.subplots()
        ax.plot(seq_numbers, throughputs, marker='o', color='dodgerblue')
        ax.set_title("📈 iPerf Throughput Over Time Intervals")
        ax.set_xlabel("Sequence Number (Interval)")
        ax.set_ylabel("Throughput (Mbps)")
        st.pyplot(fig)

        st.markdown("#### 📋 Throughput Summary")
        st.write({
            "Min Throughput (Mbps)": round(min(throughputs), 2),
            "Max Throughput (Mbps)": round(max(throughputs), 2),
            "Average Throughput (Mbps)": round(statistics.mean(throughputs), 2),
            "Std Dev Throughput (Mbps)": round(statistics.stdev(throughputs), 2) if len(throughputs) > 1 else 0,
            "Total Intervals": len(throughputs),
        })

    def run_iperf_script_client():
        cmd = ["./script.sh"]
        host = target_hosts.strip()
        dur = duration.strip()
        out_file = output_file.strip()

        if use_udp and use_reverse:
            cmd += ["iperf_client_udp_reverse", host, dur, bandwidth, out_file]
        elif use_udp:
            cmd += ["iperf_client_udp", host, dur, bandwidth, out_file]
        elif use_reverse:
            cmd += ["iperf_client_reverse", host, dur, out_file]
        else:
            cmd += ["iperf_client", host, dur, out_file]

        st.code("Running: " + " ".join(cmd))

        try:
            subprocess.run(cmd, check=True)
            st.success("✅ iPerf client test completed!")
            analyze_iperf_json(os.path.join("output", out_file))
        except subprocess.CalledProcessError as e:
            st.error(f"❌ iPerf client failed:\n{e}")

    def run_iperf_script_server():
        cmd = ["./script.sh", "iperf_server"]
        st.code("Running: " + " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)
            st.success("✅ iPerf server started successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Failed to start iPerf server:\n{e}")

    if run_iperf_client:
        st.info("🚀 Starting iPerf client test via script...")
        run_iperf_script_client()

    if run_iperf_server:
        st.info("🖥️ Starting iPerf server via script...")
        run_iperf_script_server()

    st.markdown("---")
    st.markdown("## 📤 Upload iPerf Result (JSON)")
    uploaded_iperf_file = st.file_uploader("Upload iPerf `.json` result", type=["json"])
    if uploaded_iperf_file:
        try:
            with open(os.path.join("output", uploaded_iperf_file.name), "wb") as f:
                f.write(uploaded_iperf_file.read())
            analyze_iperf_json(os.path.join("output", uploaded_iperf_file.name))
        except Exception as e:
            st.error(f"Error loading file: {e}")
#V1.2.1
