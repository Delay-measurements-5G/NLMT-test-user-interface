import streamlit as st
import os
import json
import subprocess
import matplotlib.pyplot as plt
import statistics

st.set_page_config("📡 5G Test Automation Dashboard", layout="wide")
st.title("📡 5G Network Test Automation Interface")
st.markdown("Choose between running **NLMT** or **iPerf** for analyzing network performance.")

# Mode selection
mode = st.sidebar.radio("Select Test Mode", ["NLMT", "iPerf"])

# Shared Configuration Inputs
st.sidebar.markdown("### 🌐 General Test Parameters")
target_hosts = st.sidebar.text_input("Target Host (e.g., 0.0.0.0:2112)", "0.0.0.0:2112")
duration = st.sidebar.text_input("Test Duration (e.g., 6s or 10)", "6s")
interval = st.sidebar.text_input("Send Interval (e.g., 100ms)", "100ms")
packet_size = st.sidebar.text_input("Packet Size (bytes)", "100")
output_file = st.sidebar.text_input("Output Filename (e.g., result.json)", "result.json")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# ----------------------------- NLMT MODE ----------------------------- #
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

    # Upload section for NLMT
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

# ----------------------------- iPerf MODE ----------------------------- #
else:
    st.sidebar.header("⚙️ iPerf Controls")
    use_udp = st.sidebar.checkbox("Use UDP", False)
    run_iperf_client = st.sidebar.button("▶️ Run iPerf Client")
    run_iperf_server = st.sidebar.button("🖥️ Start iPerf Server")

    def run_iperf(server_ip, duration, udp=False):
        cmd = ["iperf3", "-c", server_ip, "-t", duration]
        if udp:
            cmd.append("-u")
        st.code("Running: " + " ".join(cmd))
        try:
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            st.success("✅ iPerf client test completed!")
            st.text_area("📄 Raw Output", result.stdout, height=300)
        except subprocess.CalledProcessError as e:
            st.error(f"❌ iPerf client failed: {e.stderr}")

    def start_iperf_server():
        cmd = ["iperf3", "-s"]
        st.code("Running: " + " ".join(cmd))
        try:
            subprocess.Popen(cmd)  # run in background
            st.success("✅ iPerf server started!")
        except Exception as e:
            st.error(f"❌ Failed to start iPerf server: {e}")

    if run_iperf_client:
        st.info("🚀 Running iPerf client test...")
        run_iperf(target_hosts.strip(), duration.strip(), use_udp)

    if run_iperf_server:
        st.info("🖥️ Starting iPerf server...")
        start_iperf_server()

