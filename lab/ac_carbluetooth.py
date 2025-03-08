import socket
import threading
from collections import deque
import signal
import time
from picarx import Picarx

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


px = Picarx()

def handler(signum, frame):
    exit_event.set()

signal.signal(signal.SIGINT, handler)

def start_client():
    global server_addr
    global server_port
    global server_sock
    global sock
    global exit_event
    global message_queue
    global output
    global dq_lock
    global output_lock

    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((server_addr, server_port))
    server_sock.listen(1)
    server_sock.settimeout(30)
    sock, address = server_sock.accept()
    print("Connected")
    server_sock.settimeout(None)
    sock.setblocking(0)

    buffer = ""
    
    

    while not exit_event.is_set():
        with dq_lock:
            if len(message_queue) > 0:
                msg = message_queue[0]
                try:
                    sent = sock.send(bytes(msg, 'utf-8'))
                    print("Car sent:", msg)
                except Exception as e:
                    exit_event.set()
                    break
                if sent < len(msg):
                    message_queue[0] = msg[sent:]
                else:
                    message_queue.popleft()
        try:
            # Receiving commands
            data = sock.recv(1024).decode('utf-8')
            if data:
                buffer += data

                while "\r\n" in buffer:
                    line,buffer = buffer.split("\r\n", 1)

                if line.startswith("CMD:"):
                    cmd = line[4:]
                    response = "RPi: unknown command\r\n"
                    
                    if cmd == 'w':
                        px.set_dir_servo_angle(0)
                        px.forward(80)
                        cur_angle = px.dir_current_angle
                        response = f"RPi: moving forward {cur_angle}\r\n"
                        
                    elif cmd == 's':
                        px.set_dir_servo_angle(0)
                        px.backward(80)
                        cur_angle = px.dir_current_angle
                        response = f"RPi: moving backward {cur_angle}\r\n"
                        
                    elif cmd == 'a':
                        px.set_dir_servo_angle(-35)
                        px.forward(80)
                        cur_angle = px.dir_current_angle
                        response = f"RPi: turning left {cur_angle}\r\n"
                        
                    elif cmd == 'd':
                        px.set_dir_servo_angle(35)
                        px.forward(80)
                        cur_angle = px.dir_current_angle
                        response = f"RPi: turning right {cur_angle}\r\n"
                        
                    elif cmd == 'i':
                        tilt_angle = px.cam_tilt_cali_val
                        tilt_angle += 5
                        if tilt_angle > 65:
                            tilt_angle = 65
                            print("Maximum tilt reached")
                        px.set_cam_tilt_angle(tilt_angle)
                        tilt_angle = px.cam_tilt_cali_val
                        response = f"RPi: tilting head up {tilt_angle}\r\n"
                        
                    elif cmd == 'k':
                        # Adjust head tilt down
                        tilt_angle = px.cam_tilt_cali_val
                        tilt_angle -= 5
                        if tilt_angle < -35:
                            tilt_angle = -35
                            print("Minimum tilt reached")
                        px.set_cam_tilt_angle(tilt_angle)
                        
                    
                        response = f"RPi: tilting head down{tilt_angle}\r\n"
                        
                    elif cmd == 'j':
                        # Adjust head pan left
                        pan_angle = px.cam_pan_cali_val
                        if pan_angle == -90:
                            pan_angle = -90
                            print("Min pan angle reached")
                        px.set_cam_pan_angle(pan_angle)
                        
                        response = f"RPi: turning head left {pan_angle}\r\n"
                        
                    elif cmd == 'l':
                        # Adjust head pan right
                        pan_angle = px.cam_pan_cali_val
                        if pan_angle == 90:
                            pan_angle = 90
                            print("Max pan angle reached")
                        px.set_cam_pan_angle(pan_angle)
                        response = f"RPi: turning head right {pan_angle}\r\n"
                        
                    message_queue.append(response)
                    print("Car queued response:", response)
                    # After a short command, you may want to stop or reset.
                    time.sleep(0.5)
                    px.forward(0)  # Stop the car after moving
                else:
                    print("Received unknown command:", line)
        except:
            pass
            
                
    server_sock.close()
    sock.close()
    print("client thread end")


cth = threading.Thread(target=start_client)
cth.start()

while not exit_event.is_set():
    time.sleep(0.1)

cth.join()

print("Disconnected.")
print("All done.")