#%%
# connect to the CH340 serial port
import serial
import serial.tools.list_ports
from adafruit_pn532.uart import PN532_UART
import time
from pynput import keyboard


ports = serial.tools.list_ports.comports()
for port in ports:
    if "CH340" in port.description:
        print("Found CH340 port:", port.device)
        print("Selected port description:",port.description)
        selected_port = port.device
        
        break
        
    else:
        print("No suitable port found.")

baudrate = 115200
try:
    uart = serial.Serial(port=selected_port, baudrate=baudrate, timeout=1)
    print("reader:",uart)
except serial.SerialException as e:
    print(f"Failed to open serial port {selected_port} at baudrate {baudrate}: {e}")

pn532 = PN532_UART(uart, debug=False)

#%%
# tag information
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    print("Waiting for a card...")
    if uid is None:
        continue
    print("Found card with UID:", [hex(i) for i in uid])
    break
#%% 
#Writing data to the card
keyA = bytes.fromhex('FFFFFFFFFFFF')  # Default key A for MIFARE Classic
block_number = 4 
text_to_write = "0710690Lz!!"
data = text_to_write.encode('utf-8')
if len(data) > 16:
    print("Data is too long for a single block. Please use 16 bytes or less.")

data = data.ljust(16, b'\x00')
pn532.mifare_classic_authenticate_block(uid, block_number,0x60, keyA)
pn532.mifare_classic_write_block(block_number, data)

#%%
#Reading data from the card
from pynput import keyboard
import time
def on_activate():
    while True: 
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:   
            continue
        block_number = 4    
        keyA = bytes.fromhex('FFFFFFFFFFFF')  # Default key A for MIFARE Classic
        authenticated = pn532.mifare_classic_authenticate_block(uid, block_number, 0x60, keyA)
        if not authenticated:
            print("Failed to authenticate block {0}.".format(block_number))
            continue
        data = pn532.mifare_classic_read_block(block_number)
        print("Data read from block {0}: {1}".format(block_number, data))
        data = data.rstrip(b'\x00').decode('utf-8')
        print(data)
        break
    text_inout = keyboard.Controller()
    time.sleep(1)
    text_inout.type(data)
    print("Hotkey activated! Typed 'data'.")

keyboard.GlobalHotKeys({
    '<ctrl>+<alt>': on_activate
}).start()