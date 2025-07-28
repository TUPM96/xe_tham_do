import socket
import threading
import subprocess

# Cau hinh server
HOST = '0.0.0.0'  # Lang nghe moi dia chi
PORT = 8888       # Cong tuy chon

def handle_client(conn, addr):
    print(f"[KET NOI MOI] {addr} da ket noi.")
    try:
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"[MAT KET NOI] {addr}")
                    break
                # Gia su Flutter gui chuoi ky tu dieu khien (vi du: "FORWARD", "LEFT", "STOP", ...)
                command = data.decode('utf-8').strip()
                print(f"[NHAN] {addr}: {command}")
                # Thuc thi command nay vao cmd_line (command line)
                # Can than bao mat! O day chi chay demo echo lai lenh
                try:
                    # Vi du: thuc thi lenh gia lap, thay the bang lenh that cua ban
                    result = subprocess.run(['echo', command], capture_output=True, text=True)
                    output = result.stdout.strip()
                except Exception as e:
                    output = f"LOI: {e}"
                # Gui lai ket qua cho client (tuy chon)
                conn.sendall(output.encode('utf-8'))
    except Exception as e:
        print(f"[LOI] {addr}: {e}")

def start_server():
    print("[KHOI DONG] Server socket dang chay...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LANG NGHE] Dia chi: {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()