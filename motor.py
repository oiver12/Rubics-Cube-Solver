import serial
import time

sendMode = True
# connecting arduino port to python program
###########################
# change the port here!!
###########################
if sendMode:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)

def up():
    #R L F2 B2 R' L' //sets up D pieces to U
    sendDataAndRespone('R')
    sendDataAndRespone('L')
    sendDataAndRespone('F')
    sendDataAndRespone('F')
    sendDataAndRespone('B')
    sendDataAndRespone('B')
    sendDataAndRespone('r')
    sendDataAndRespone('l')
    sendDataAndRespone('D')
    sendDataAndRespone('R')
    sendDataAndRespone('L')
    sendDataAndRespone('F')
    sendDataAndRespone('F')
    sendDataAndRespone('B')
    sendDataAndRespone('B')
    sendDataAndRespone('r')
    sendDataAndRespone('l')

def up_prime():
    #R L F2 B2 R' L' //sets up D pieces to U
    sendDataAndRespone('R')
    sendDataAndRespone('L')
    sendDataAndRespone('F')
    sendDataAndRespone('F')
    sendDataAndRespone('B')
    sendDataAndRespone('B')
    sendDataAndRespone('r')
    sendDataAndRespone('l')
    sendDataAndRespone('d')
    sendDataAndRespone('R')
    sendDataAndRespone('L')
    sendDataAndRespone('F')
    sendDataAndRespone('F')
    sendDataAndRespone('B')
    sendDataAndRespone('B')
    sendDataAndRespone('r')
    sendDataAndRespone('l')

def down():
    sendDataAndRespone('D')

def down_prime():
    sendDataAndRespone('d')

def right():
    sendDataAndRespone('R')

def right_prime():
    sendDataAndRespone('r')

def left():
    sendDataAndRespone('L')

def left_prime():
    sendDataAndRespone('l')

def front():
    sendDataAndRespone('F')

def front_prime():
    sendDataAndRespone('f')

def back():
    sendDataAndRespone('B')

def back_prime():
    sendDataAndRespone('b')

def sendDataAndRespone(letter: str):
    if sendMode:
        ser.write(letter.encode('utf-8'))
        #block till read
        ser.timeout = 3
        try:
            response = ser.read()
            if response:
                print(f"Received: {response}")
            else:
                print("No data received within the timeout period.")
        except serial.SerialTimeoutException:
            print("Timeout exception")

        #hanlde response

