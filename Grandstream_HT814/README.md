*usage: hexdump2bin.py [-h] [-n FILE_NAME] [-f DESTINATION_FOLDER]*
                      *[-d SERIAL_DEVICE] [-r BAUD_RATE]*
                      *[--uboot-flag UBOOT_FLAG] [--uboot-prompt UBOOT_PROMPT]*
                      *[--flash-read-command FLASH_READ_COMMAND]*
                      *[--dump-command DUMP_COMMAND]*
                      *[--sed-command SED_COMMAND]*
                      *[--conversion-command CONVERSION_COMMAND]*

This script is compatible with Debial based Linux systems, it has been written to extract the firmware of a Grandstream HT814 via serial console.

Once the script has been executed, the device can be plugged in and everything is done automatically from there. It uses U-Boot `md` to dump the firmware once it has been read into memory  with `qspi`. Once the firmware has been dumped in a text file, a subprocess executes a `sed` command to strip off the memory addresses and ASCII data from the file, leaving only 8 bits hex characters. Finally the file is converted to binary with the reverse option of `xdd`.

It may be compatible with other HT### models, it may also be compatible with other embedded devices using U-Boot and the same type of RAM and flash memory if the global variables are changed accordingly, the global variables can be passed as arguments.

<ins>**Here is a description of each global variables:**</ins>

`UBOOT_FLAG`: The string to be detected when it's time to press a specific key to enter the U-Boot prompt (Note that this script presses ESC to enter the promt and function `press_escape()` may have to be changed for other devices).

`UBOOT_PROMPT`: The U-Boot prompt text, in order to detect when serial commands may be sent.

`FLASH_READ_CMD`: The U-Boot command to load the kernel into memory.

`DUMP_CMD`: The U-Boot command to display the data from the load address to a specific offset.

`SED_CMD`: The sed command to get a file with hex data only. ## Should be edited to fit in a re.sub() method in order to remove the subprocess library.

`CONVERT2BIN_CMD`: The Linux command to convert the text hex data to a binary file.
