import argparse
import serial
import sys
import time

UBOOT_FLAG = "Hit Esc key to stop autoboot"
UBOOT_PROMPT = "DVF99 #"

def read_serial():
    serial_output = ser.readline().decode()
    return serial_output

parser = argparse.ArgumentParser(description="Dumps hex data with U-Boot 'md' command via serial console")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true")
group.add_argument("-q", "--quiet", action="store_true")
parser.add_argument("-d", "--serial-device", default="/dev/ttyUSB0")
parser.add_argument("-r", "--baud-rate", default="115200")
args = parser.parse_args()

if args.verbose:
    print("Opening serial port {}...".format(args.serial_device))
    try:
        ser = serial.Serial(args.serial_device, args.baud_rate, timeout=1, write_timeout=0)
        print("You may now power on your device\nWaiting to recieve data...")
    except (FileNotFoundError, serial.serialutil.SerialException):
        print("{} does not exist, program terminating...".format(args.serial_device))
        sys.exit(2)
    while True:
        output = read_serial()
        if output:
            print(output, end='')
        if UBOOT_FLAG in output:
            print("Entering U-Boot prompt...")
            ser.write(chr(27).encode())
        if UBOOT_PROMPT in output:
            print("The program is about to dump the entire device firmware, this may take a while.")
            ser.write(b'qspi read.partial core $loadaddr 0x200; qspi read.partial factory $devtree_addr 0x4000')
            ser.write(chr(10).encode())
            time.sleep(1)
            ser.write(b'md.b 42000000 131f20')
            ser.write(chr(10).encode())
            break
        else:
            continue
    with open('dump', 'w') as dump_file:
        output = read_serial()
        while len(output) > 10:
            output = read_serial()
            print(output, end='')
            dump_file.write(output)
    ser.close()
    print("terminating ...")