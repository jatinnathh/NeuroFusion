import socket
import json
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())

def update_ip_files():
    ip = get_local_ip()
    ip_config = {"ip": ip}
    
    # List of files to update
    ip_files = [
        "backend/ip.json",
        "screens/ip.json"
    ]
    
    for file_path in ip_files:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(ip_config, f)
        print(f"Updated {file_path} with IP: {ip}")

if __name__ == "__main__":
    update_ip_files()