import socket
import threading
from collections import deque
import signal
import time
import readchar
import select

# Replace your picar MAC address here and in the car's pi_socket.py
server_addr = '2C:CF:67:4D:49:B8'
server_port = 1

buf_size = 1024

client_sock = None
server_sock = None
sock = None

exit_event = threading.Event()

message_queue = deque([])
output = ""

dq_lock = threading.Lock()
output_lock = threading.Lock()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def start_client():
    global sock
    global dq_lock
    global output_lock
    global exit_event
    global message_queue
    global output
    global server_addr
    global server_port
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.settimeout(60)
    sock.connect((server_addr,server_port))
    sock.settimeout(None)
    print("Connected")
    sock.setblocking(False)

    while not exit_event.is_set():
        if dq_lock.acquire(blocking=False):

            if(len(message_queue) > 0):
                try:
                    sent = sock.send(bytes(message_queue[0], 'utf-8'))
                except Exception as e:
                    exit_event.set()
                    dq_lock.release()
                    continue
                if sent < len(message_queue[0]):
                    message_queue[0] = message_queue[0][sent:]
                else:
                    message_queue.popleft()
            dq_lock.release()
        

        rlist, _, _ = select.select([sock], [], [], 0.1)
        if rlist:
            try:
                data = sock.recv(1024).decode("utf-8")
                if data:
                    print(data)
            except socket.error as e:
                data = ""
                print("Socket error")
                #no data
    sock.close()
    print("client thread end")


def keyboard_control():
    print("Keyboard control active. Use WASD to control the PiCar-X movement, IKJL for head movement. Press CTRL+C to quit.")
    while not exit_event.is_set():
        try:
            key = readchar.readkey().lower()
        except KeyboardInterrupt:
            exit_event.set()
            break
        # Map key presses to commands. You can extend this mapping.
        if key in ('w', 'a', 's', 'd', 'i', 'k', 'j', 'l'):
            command = f"CMD:{key}\r\n"
            with dq_lock:
                message_queue.append(command)
        elif key == readchar.key.CTRL_C:
            exit_event.set()
            continue
        time.sleep(0.1)

cth = threading.Thread(target=start_client)
cth.start()

kbd_thread = threading.Thread(target=keyboard_control)
kbd_thread.start()

cth.join()
kbd_thread.join()

print("Disconnected.")
print("All done.")