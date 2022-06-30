import serial
import time
import traceback
import numpy as np

class ESP301:
    def __init__(self, com_port='COM3', baudrate=921600, parity='N', bytesize=8, stopbits=1):
        self.ser = serial.Serial(com_port, baudrate, timeout=5)
        
        #wait until motion is done
    def wait_till_done(self, n_iter=100, pause=0.2, let_settle=True, settle_pause=0.25):
        #print('wait_till_done')
        for _ in range(n_iter):
            time.sleep(pause)
            self.ser.write(b'1MD?\r\n')
            line = self.ser.readline().decode().rstrip('\r\n')
            #print('Is motion done? (0: NOT done; 1: done): {}'.format(line))
            if int(line) == 1:
                break
        if let_settle:
            for _ in range(n_iter):
                self.ser.write(b'1TP\r\n')
                pos1 = float(self.ser.readline().decode().rstrip('\r\n'))
                time.sleep(settle_pause)
                self.ser.write(b'1TP\r\n')
                pos2 = float(self.ser.readline().decode().rstrip('\r\n'))
                if round(pos1,3) == round(pos2,3):
                    break
        return None
        #checks for errors or port connection
    def check_error(self):
        # not needed for queries, but use when instructing to do something
        
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")

        command = "TB?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()
        if response == b'':
            return (False, "Response timed out. " + '[' + response.decode('ascii') + ']')
        
        response = response.strip().decode('ascii')

        if response[0] == '0':
            return (True, "No errors.")
        else:
            # flush the error buffer
            for n in range(10):
                self.ser.write(command.encode('ascii'))
                self.ser.readline()
            # flush the serial input buffer
            time.sleep(0.1)
            self.ser.reset_input_buffer()
            return (False, response)

        #turns on motor
    def axis_on(self):
        # if not self.ser.is_open:
        #     return (False, "Serial port " + self._port + " is not open. ")
        # if not self.is_axis_num_valid(axis_number):
        #     return (False, "Axis number is not valid or not part of passed tuple during construction.")

        command = str(1) + "MO\r"
        self.ser.write(command.encode('ascii'))

        was_successful, message = self.check_error()
        if not was_successful:
            return (was_successful, message)

        command = str(1) + "MO?\r"
        self.ser.write(command.encode('ascii'))
        response = self.ser.readline()

        if response.strip().decode('ascii') == '1':
            return (True, "Axis " + str(1) + " motor successfully turned ON.")
        else:
            # also means timeout
            return (False, "Axis " + str(1) + " motor failed to turned ON.")
        
        
        #turns on axis motor. sets units to mm, sets home to 0and  gos to home position
    def initialize(self):
        was_successful, message = self.check_error()# just used to flush error and serial input buffer if there is an error
        if not was_successful:
            return (was_successful, message)
        self.ser.reset_input_buffer() # flush the serial input buffer even if there was no error
        # Make sure axis motor is turned on
        was_turned_on, message = self.axis_on()
        if not was_turned_on:
            self._is_initialized = False
            return (was_turned_on, message)
        # set units to mm, homing value to 0 
        command = str(1) + "sn2" + "\r"    #sn3 for micrometer
        self.ser.write(command.encode('ascii')) 
        command = str(1) + "sh0" + '\r'    #set home to '0'
        self.ser.write(command.encode('ascii'))
        self.set_home()
        # Make sure initialization of settings was successful
        was_successful, message = self.check_error()
        if not was_successful:
            self._is_initialized = False
            return (was_successful, message)
            was_homed, message = self.set_home()
    
        self._is_initialized = True
        return (True, "Successfully initialized axes by setting units to mm, settings max/current speeds, and homing. Current position set to zero.")
        
        #put a command from the esp301 docu in
    def write(self, command):
        command= command +'\r\n'
        self.ser.write(command.encode('ascii'))
        return None
    def read_after_write(self, command):
        command= command +'\r\n'
        self.ser.write(command.encode('ascii'))
        return self.ser.readline().decode().rstrip('\r\n')
    
        #close serial Port connection
    def close(self):
        self.ser.close()
        print('Is port still open?: ', self.ser.is_open)
        
        #put out current position of the stage in number of units
        #if initialized the units are in mm
    def get_pos(self):
        self.ser.write(b'1TP\r\n')
        line = float(self.ser.readline().decode().rstrip('\r\n'))
        return line

        #pos = float / input the number of units the stage should travel absolut
    def set_pos_abs(self, pos):
        self.ser.write('1PA {}\r\n'.format(pos).encode())
        # self.wait_till_done(pause=0.1, n_iter=100, let_settle=True)
        return None
        
        #pos = float / input the number of units the stage should travel relativ
    def set_pos_rel(self, pos):
        self.ser.write('1PR {}\r\n'.format(pos).encode())
        # self.wait_till_done(pause=0.1, n_iter=100, let_settle=True)
        return None

        #go to the home position of the stage. if not defined it is the middle of the stage
    def set_home(self):
        if not self.ser.is_open:
            return (False, "Serial port " + self._port + " is not open. ")
        command = '1OR\r\n'
        self.ser.write(command.encode('ascii'))
        self.wait_till_done(n_iter=50)
        return None

