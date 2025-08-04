import socket
import json

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

if ip.startswith("172."):
    import netifaces as ni
    ip = ni.ifaddresses("Wi-Fi")[ni.AF_INET][0]["addr"]  
with open("backend/ip.json", "w") as f:
    json.dump({"ip": ip}, f)

print(" Saved IP to backend/ip.json:", ip)
