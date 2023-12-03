from control.control_layer import ControlLayer


cl = ControlLayer("192.168.0.112::11419::468926548725586293::/home/abhinav/.temp/abhinav.txt", ishost=True)

try:
    cl.start()
except KeyboardInterrupt:
    cl.stop()
    exit(0)
