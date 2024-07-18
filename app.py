import os
import pyautogui
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

pcap = pyautogui.prompt("Enter path to pcap: ")
val = "sudo tcpreplay -i eth1 " + pcap
stream = os.popen(val)
out = stream.read()
pyautogui.alert(out)