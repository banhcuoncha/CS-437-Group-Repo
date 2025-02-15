from picarx import Picarx
from vilib import Vilib
import time



# Functions are imported from Sunfounder's vilib library https://github.com/sunfounder/vilib

# Sunfounder's picar-x/example/7.display.py
# def face_detect(flag):
#     print("Face Detect:" + str(flag))
#     Vilib.face_detect_switch(flag)


def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.show_fps()
    Vilib.display(local=True, web=True)
    Vilib.face_detect_switch(True)
    Vilib.traffic_detect_switch(True)

    while True:
 
        # Face detection, from vilib/example/face_detection.py
        flag_face = Vilib.face_obj_parameter['n']
        if flag_face != 0:
            x = Vilib.face_obj_parameter['x']
            y = Vilib.face_obj_parameter['y']
            w = Vilib.face_obj_parameter['w']
            h = Vilib.face_obj_parameter['h']
            print(f"{flag_face} faces found, the largest block coordinate=({x}, {y}), size={w}*{h}")
        # Disabled for less terminal cluttering
        #else:
            #print(f'No face found')


        # Traffic sign detection, from vilib/example/traffic_sign_detect.py
        flag_traffic = Vilib.traffic_sign_obj_parameter['t']
        if flag_traffic != 'none':
            x = Vilib.traffic_sign_obj_parameter['x']
            y = Vilib.traffic_sign_obj_parameter['y']
            w = Vilib.traffic_sign_obj_parameter['w']
            h = Vilib.traffic_sign_obj_parameter['h']
            acc = Vilib.traffic_sign_obj_parameter['acc']

            print(f"{flag_traffic} ({acc}%), coordinate=({x}, {y}), size={w}*{h}")
        # Disabled for less terminal cluttering
        #else:
            #print(f'No traffic sign found')
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        Vilib.camera_close()
