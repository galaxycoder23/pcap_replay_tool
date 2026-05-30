"""GUI tool for packet capture replay using the tcpreplay utility."""

# Imports
import time  # Used for the typewriter effect
from datetime import datetime  # To name merged PCAP
import threading  # For multi-threading
import os  # To create the upload folder
import shutil  # For use in deleting files
import streamlit as st  # For the app infrastucture itself
import paramiko  # SSH from Python app
from scp import SCPClient  # SCP

# SSH credentials
ssh_host = st.secrets["ip_address"]
SSH_PORT = 22
SSH_USER = st.secrets["username"]
SSH_PASSWORD = st.secrets["password"]


# SSH setup
def get_ssh():
    """Create and return an SSH client connected to the target machine."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically adds the hostname and new host key to the local HostKeys object, and saves it
    client.connect(ssh_host, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD)
    return client


st.set_page_config(page_title="Network traffic replay application", page_icon="✨")

st.title("Network traffic replay application")

# Subtitle and typewriter formatting
def stream_data(string):
    """Create typewriter-style text on screen."""
    for character in list(string):
        yield character + ""
        time.sleep(0.01)

st.write_stream(stream_data("Replay packet captures using tcpreplay"))


# Allow user to upload PCAP files
st.subheader("Upload packet captures:")

filename = None
remote_path = None
replay_speed = ""


# Function to display tcpreplay command to user (called further down the page)
def display_command():
    """Display tcpreplay command to user"""
    if file_uploads:
        st.subheader("Command that will be run: ")
        st.session_state["replay_command"] = (
            "sudo -S tcpreplay -i eth1 -vv"
            + str(replay_speed)
            + " "
            + remote_path
            + " > /tmp/tcpreplay.log 2>&1"
        )
        st.code(st.session_state["replay_command"], language="bash")


def delete_files():
    """Delete files which are no longer required once the tcpreplay process is complete"""
    # Windows
    if os.path.exists("./upload_folder/"):
        shutil.rmtree("./upload_folder/")
    if os.path.exists("./replay_pid.txt"):
        os.remove("./replay_pid.txt")
    # Linux
    client = get_ssh()
    client.exec_command("rm ~/Documents/packet_captures/*")
    client.close()


file_uploads = st.file_uploader(
    "Upload files",
    type=(["pcap"]),
    accept_multiple_files=True,
    on_change=display_command,
)
if file_uploads:
    if not (os.path.exists("./upload_folder/")):
        os.mkdir("./upload_folder/")
    if len(file_uploads) == 1:
        filename = file_uploads[0].name
        with open("./upload_folder/" + filename, "wb") as f:
            for uploaded_file in file_uploads:
                f.write(uploaded_file.getvalue())  # For uploaded file as bytes
                st.download_button(
                    "Download PCAP",
                    uploaded_file.getvalue(),
                    file_name=filename,
                    mime="application/vnd.tcpdump.pcap",
                )
    else:
        for uploaded_file in file_uploads:
            filename = st.text_input("Enter a name for the merged PCAP:")
            if not filename:
                filename = "mergedpcap_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = filename + ".pcap"
        with open("./upload_folder/" + filename, "wb") as f:
            for uploaded_file in file_uploads:
                f.write(uploaded_file.getvalue())  # For uploaded file as bytes
        with open("./upload_folder/" + filename, "rb") as merged_file:
            st.download_button(
                "Download merged PCAP",
                merged_file,
                file_name=filename,
                mime="application/vnd.tcpdump.pcap",
            )
    remote_path = "~/Documents/packet_captures/" + filename


# Adjust replay speed
st.write("---")
st.subheader("Packet capture replay speed")
option = st.selectbox(
    "What speed would you like to replay the packet capture at?",
    ["x0.5", "Normal", "x2", "x3", "x4", "x8", "Top speed"],
    index=1,
)
if option == "Normal":
    replay_speed = ""
elif option == "Top speed":
    replay_speed = " -t"
else:
    multiplier = option[1:]
    replay_speed = " -x " + multiplier
st.write("---")

display_command()


# SCP to transfer PCAP
def upload_file_to_remote(local_file, remote_directory, client):
    """Transfer file from local machine to remote machine using SCP"""
    with SCPClient(client.get_transport()) as scp:
        scp.put("./upload_folder/" + local_file, remote_directory)


# Replay traffic
def replay_traffic():
    """Replay traffic using the tcpreplay utility"""
    client = get_ssh()
    client.exec_command("mkdir -p ~/Documents/packet_captures")
    try:
        upload_file_to_remote(filename, remote_path, client)
        stdin, stdout, _ = client.exec_command(st.session_state["replay_command"])
        stdin.write(st.secrets["password"] + "\n")
        stdin.flush()
        time.sleep(0.5)
        pid_client = get_ssh()
        _, pid_out, _ = pid_client.exec_command("pgrep tcpreplay")
        pid = pid_out.read().decode().strip()
        with open("./replay_pid.txt", "w", encoding="utf-8") as pid_file:
            pid_file.write(pid)
        pid_client.close()
        stdout.channel.recv_exit_status()
    finally:
        delete_files()
        client.close()


if st.button("Start traffic replay"):
    t = threading.Thread(target=replay_traffic)
    t.daemon = True
    t.start()


# Stop replay of traffic
def stop_traffic():
    """Terminate tcpreplay process"""
    client = get_ssh()
    if os.path.exists("./replay_pid.txt"):
        with open("./replay_pid.txt", "r", encoding="utf-8") as pid_file:
            pid = pid_file.read().strip()
        stdin, stdout, _ = client.exec_command(f"sudo -S kill {pid}", get_pty=True)
        stdin.write(st.secrets["password"] + "\n")
        stdin.flush()
        stdout.read()
    client.close()
    delete_files()


if st.button("Stop traffic replay and delete files", type="primary"):
    stop_traffic()
