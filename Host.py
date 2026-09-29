# Copyright (C) 2026 wawa2016-here
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.


# host.py
import socket
import pickle
import zlib
from mss import mss
import numpy as np
import cv2

PORT = 9999

def get_my_ip():
    """Automatically finds this computer's local IP address to use as the ID"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, just used to find interface IP
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
    my_id = get_my_ip()
    
    # 1. Start listening for incoming connections
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host_socket.bind(('0.0.0.0', PORT))
    host_socket.listen(1)
    
    print("=============================================")
    print(f" YOUR CONNECTION ID IS: {my_id}")
    print(" Give this ID to your friend so they can watch!")
    print("=============================================")
    print("[*] Waiting for viewer to connect...")
    
    conn, addr = host_socket.accept()
    print(f"[*] Connection established with viewer: {addr}")
    
    try:
        with mss() as sct:
            monitor = sct.monitors[1]
            
            while True:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, (1280, 720)) 
                
                serialized = pickle.dumps(frame)
                compressed = zlib.compress(serialized, level=3)
                
                size = len(compressed)
                conn.sendall(size.to_bytes(4, byteorder='big') + compressed)
                
    except (socket.error, BrokenPipeError):
        print("\n[-] Viewer disconnected.")
    except KeyboardInterrupt:
        print("\n[*] Stopping screen share...")
    finally:
        conn.close()
        host_socket.close()

if __name__ == "__main__":
    main()
