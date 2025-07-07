import socket
import json
import os
import subprocess
import platform

def get_local_ip():
    try:
        # Try to get Windows WiFi adapter IP first
        if platform.system() == "Windows":
            try:
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Wireless LAN adapter Wi-Fi' in line or 'WiFi' in line:
                        # Look for IPv4 address in the next few lines
                        for j in range(i, min(i+10, len(lines))):
                            if 'IPv4 Address' in lines[j] and '192.168.' in lines[j]:
                                ip = lines[j].split(':')[-1].strip()
                                return ip
            except:
                pass
        
        # Fallback method
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