import argparse
import serial
import sys
import time
import hexdump
import subprocess
import os

_UBOOT_FLAG = 'Hit Esc key to stop autoboot'
_UBOOT_PROMPT = 'DVF99 #'
_FLASH_READ_CMD = b'qspi read.partial core $loadaddr 0x200; qspi read.partial factory $devtree_addr 0x4000'
_DUMP_CMD = b'md.b 42000000 131f20'
_SED_CMD = ['sed', '-i', r's/^.*\(\([0-9A-Fa-f]\{2\}\s\)\{15\}[0-9A-Fa-f]\{2\}\).*$/\1/g;s/^DVF99.*$//g']
_CONVERT2BIN_CMD = 'xxd -r -p {0}/{1} > {0}/{1}.dat'

def parse_args():
    parser = argparse.ArgumentParser(description="Dumps HT814 hex data and cenverts it to a binary file")
    parser.add_argument('-n', '--file-name', default='HT814')
    parser.add_argument('-f', '--destination-folder', default='.')
    parser.add_argument('-d', '--serial-device', default='/dev/ttyUSB0')
    parser.add_argument('-r', '--baud-rate', default='115200')
    parser.add_argument('--uboot-flag', required=False, default=_UBOOT_FLAG)
    parser.add_argument('--uboot-prompt', default=_UBOOT_PROMPT)
    parser.add_argument('--flash-read-command', default=_FLASH_READ_CMD)
    parser.add_argument('--dump-command', default=_DUMP_CMD)
    parser.add_argument('--sed-command', default=_SED_CMD)
    parser.add_argument('--conversion-command', default=_CONVERT2BIN_CMD)
    args = parser.parse_args()
    return args

def read_serial(ser):
    try:
        serial_output = ser.readline().decode()
    except UnicodeDecodeError:
        print('Invalid start byte, please verify device connectivity.')
        print('Note that this error may occur if the device is already plugged in during script runtime')
        print('Terminating...')
        sys.exit(1)
    return serial_output

def press_escape():
    return chr(27).encode()

def press_enter():
    return chr(10).encode()

def convert_to_bin(dump):
    bin_file = hexdump.restore(dump)
    return bin_file

def main(args):
    _UBOOT_FLAG = args.uboot_flag
    _UBOOT_PROMPT = args.uboot_prompt
    _FLASH_READ_CMD = args.flash_read_command
    _DUMP_CMD = args.dump_command
    _SED_CMD = args.sed_command
    _SED_CMD.append("{}/{}".format(args.destination_folder, args.file_name))
    _CONVERT2BIN_CMD = args.conversion_command
    print('Opening serial port {}...'.format(args.serial_device))
    try:
        ser = serial.Serial(args.serial_device, args.baud_rate, timeout=1, write_timeout=0)
        print('You may now power on your device\nWaiting to recieve data...')
    except (FileNotFoundError, serial.serialutil.SerialException):
        print('{} does not exist, program terminating...'.format(args.serial_device))
        sys.exit(2)
    while True:
        output = read_serial(ser)
        if output:
            print(output, end='')
        if _UBOOT_FLAG in output:
            print('Entering U-Boot prompt...')
            ser.write(press_escape())
        if _UBOOT_PROMPT in output:
            print('The program is about to dump the entire device firmware, this may take a while.')
            ser.write(_FLASH_READ_CMD)
            ser.write(press_enter())
            time.sleep(1)
            ser.write(_DUMP_CMD)
            ser.write(press_enter())
            break
        else:
            continue
    with open('{}/{}'.format(args.destination_folder, args.file_name), 'w') as dump_file:
        output = read_serial(ser)
        while len(output) > 10:
            output = read_serial(ser)
            print(output, end='')
            dump_file.write(output)
    print('Closing serial port...')
    ser.close()
    print('Removing all non 8-bits hex characters')
    try:
        subprocess.call(_SED_CMD)
    except (KeyError, ValueError):
        print('Unexpected character in sed command, terminating...')
        sys.exit(1)
    print('Converting dumped hex data to binary...')
    try:
        os.system(_CONVERT2BIN_CMD.format(args.destination_folder, args.file_name))
    except (ValueError, KeyError):
        print('Unexpected character in conversion command, terminating...')
        sys.exit(1)
    print('Removing temporary text dump file...')
    os.system('rm {}/{}'.format(args.destination_folder, args.file_name))
    print('Done.')

if __name__ == '__main__':
    args = parse_args()
    main(args)
