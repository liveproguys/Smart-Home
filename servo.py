import time
import serial

class Servo:
    def __init__(self, port="COM6", baud_rate=115200):
        self.serial = serial.Serial(port, baud_rate)
    
    def checksum(self, buf):
        total = sum(buf) - 0x55 - 0x55
        return (~total) & 0xFF

    def serial_serro_wirte_cmd(self, id=None, w_cmd=None, dat1=None, dat2=None):
        buf = bytearray(b'\x55\x55')
        buf.append(id)
        
        if dat1 is None and dat2 is None:
            buf.append(3)
        elif dat1 is not None and dat2 is None:
            buf.append(4)
        elif dat1 is not None and dat2 is not None:
            buf.append(7)
            
        buf.append(w_cmd)
        
        if dat1 is not None and dat2 is None:
            buf.append(dat1 & 0xFF)
        elif dat1 is not None and dat2 is not None:
            buf.extend([(dat1 & 0xFF), ((dat1 >> 8) & 0xFF)])
            buf.extend([(dat2 & 0xFF), ((dat2 >> 8) & 0xFF)])
            
        buf.append(self.checksum(buf))
        self.serial.write(buf)
    
    def write(self, servo_id, pulse, duration=300):
        pulse = max(0, min(pulse, 1000))
        duration = max(0, min(duration, 30000))
        
        LOBOT_SERVO_MOVE_TIME_WRITE = 1
        self.serial_serro_wirte_cmd(servo_id, LOBOT_SERVO_MOVE_TIME_WRITE, pulse, duration)
        
    def close(self):
        self.serial.close()
#Example code:
"""
a=Servo("/dev/ttyUSB0")
while True:
    a.write(1,100)
    a.write(2,500)
    a.write(3,500)
    a.write(4,500)
    a.write(6,500)
    a.write(5,500)
    time.sleep(1)
"""