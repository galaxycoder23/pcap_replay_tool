import os
import pyautogui
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
	path = None
	if request.method == "POST":
		path = request.form["filepath"]
	return render_template("index.html", path=path)

#pcap = pyautogui.prompt("Enter path to pcap: ")
#val = "sudo tcpreplay -i eth1 " + pcap
#stream = os.popen(val)
#out = stream.read()
#pyautogui.alert(out)
