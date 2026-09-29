# Copyright (C) 2026 wawa2016-here
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.


# viewer.py
import socket
import pickle
import zlib
import cv2
import numpy as np

PORT = 9999

def main():
    # The "ID" is simply the host's IP address
    host_id = input("Enter the Host's Connection ID: ").strip()
    if not host_id:
        print("Invalid ID.")
        return

    viewer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Attempting to connect to ID {host_id}...")
    
    try:
        viewer_socket.connect((host_id, PORT))
        print("[*] Connected successfully! Opening video window...")
        
        data_buffer = b""
        window_title = "Live Screen Share Feed"
        
        while True:
            while len(data_buffer) < 4:
                packet = viewer_socket.recv(4096)
                if not packet: 
                    break
                data_buffer += packet
                
            if not data_buffer:
                print("[-] Host closed the connection.")
                break
                
            packed_size = data_buffer[:4]
            data_buffer = data_buffer[4:]
            msg_size = int.from_bytes(packed_size, byteorder='big')
            
            while len(data_buffer) < msg_size:
                data_buffer += viewer_socket.recv(max(4096, msg_size - len(data_buffer)))
                
            frame_data = data_buffer[:msg_size]
            data_buffer = data_buffer[msg_size:]
            
            decompressed = zlib.decompress(frame_data)
            frame = pickle.loads(decompressed)
            frame = np.array(frame)
            
            cv2.imshow(window_title, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"[-] Connection failed: {e}")
    finally:
        viewer_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
