# GUI tool for packet capture replay using tcpreplay

Run the following commands in PowerShell, Command Prompt, or a terminal of your choice.

---

## Prerequisites
- Host machine (Windows) to run this application
- Target machine (Linux) to run the tcpreplay utility
- `Python` and `pip` installed on the host machine

---

## Installation instructions

### Download Python
Download the Windows MSI installer from [python.org](https://www.python.org/downloads/windows/).

### If installing on a Windows Server (as MSIs cannot be installed directly), run the following commands: 
``` shell
Add-AppxPackage -path "<PATH>"
```
``` shell
python
```

### Install required dependencies
``` shell
python -m venv venv
.\venv\Scripts\activate
```
Press Enter, then:
``` shell
pip install -r requirements.txt
```
### Validate Streamlit installation
``` shell
streamlit hello
```

### If `SSH` and `tcpreplay` haven't been installed on Linux:
``` bash
sudo apt install openssh-server
sudo systemctl start ssh
sudo apt install tcpreplay
```

---

### Air-gapped setup
If the target Windows machine has no internet access, download the packages on another Windows machine with Internet access and copy them across:

**On machine with Internet access (prerequisite of `Python` and `pip` installed):**
``` shell
pip download -r requirements.txt -d .\wheelhouse
```
Then copy the `.\wheelhouse` folder to the target Windows machine so the dependencies can be used when running the application.

**On Windows host machine:**
``` shell
pip install --no-index --find-links=.\wheelhouse -r requirements.txt
```

---

## Configuration
Update `.streamlit/secrets.toml` with the Linux machine's IP address, username and password for SSH:

---

## Run application
To run the application, activate the venv and run the application:
``` shell
.\venv\Scripts\activate
```
Press Enter, then:
``` shell
streamlit run .\pcap_replay_tool.py
```

To deactivate the venv:
``` shell
deactivate
```

---

**NB: If Python is not within the terminal's environment variables, you can prepend `py -m` to the start of each shell command.**
