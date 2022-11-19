"""
This example acts as a BLE HID keyboard to peer devices.
Attach five buttons with pullup resistors to Feather nRF52840
  each button will send a configurable keycode to mobile device or computer
"""
import time
import board
from digitalio import DigitalInOut, Direction, Pull

import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
import analogio
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
# Language specific
#from adafruit_hid.keyboard_layout_us import KeyboardLayout
#from adafruit_hid.keycode import Keycode
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode


# Setup IO
button_8 = DigitalInOut(board.D13)
button_5 = DigitalInOut(board.D12)
button_3 = DigitalInOut(board.D11)
button_6 = DigitalInOut(board.D10)
button_9 = DigitalInOut(board.D9)

button_1 = DigitalInOut(board.A0)
button_2 = DigitalInOut(board.A1)
button_4 = DigitalInOut(board.A2)
button_7 = DigitalInOut(board.A3)

buttons = [button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8, button_9]
for button in buttons:
    button.direction = Direction.INPUT
    button.switch_to_input(pull=Pull.UP)

led = neopixel.NeoPixel(board.NEOPIXEL, 1)

# Define functions
def get_voltage(pin):
    return (pin.value * 3.7) / 65536 * 2

def calculateBatteryPercentage(voltage):
    minVoltage = 4
    maxVoltage = 4.5
    percentage =  (voltage- minVoltage) / (maxVoltage - minVoltage)*100
    return max(0, min(100, percentage))
    

def showCharge(charge:int):
    hue = int(charge/100/3*255)
    # print(f"hue: {hue} gives: RGB{fancy.CRGB(fancy.CHSV(hue,255,255))}")
    led[0] = fancy.CHSV(hue,255,255).pack()
    
pressed = [False for i in range(9)]
commands = [None for i in range(9)]

def func1():
    kl.write("1")
def func2():
    kl.write("2")
def func3():
    kl.write("3")
def func4():
    kl.write("4")
def func5():
    kl.write("5")
def func6():
    kl.write("6")
def func7():
    kl.write("7")
def func8():
    kl.write("8")
def func9():
    kl.write("9")

commands[0] = func1
commands[1] = func2
commands[2] = func3
commands[3] = func4
commands[4] = func5
commands[5] = func6
commands[6] = func7
commands[7] = func8
commands[8] = lambda: kl.write("9")

# Setup BLE
vbat_voltage = analogio.AnalogIn(board.VOLTAGE_MONITOR)
led.brightness = 1  

hid = HIDService()
device_info = DeviceInfoService(software_revision=adafruit_ble.__version__, manufacturer="Adafruit Industries")
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "Mateo Macropad"

ble = adafruit_ble.BLERadio()

if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)

k = Keyboard(hid.devices)
kl = KeyboardLayout(k)
while True:
    while not ble.connected:
        #Show charge
        batteryPercentage = calculateBatteryPercentage(get_voltage(vbat_voltage))
        showCharge(batteryPercentage)
        #print(f"{get_voltage(vbat_voltage)}v gives {batteryPercentage}% battery left" )
        
    print("BLE connected:")
    while ble.connected:
        #Show charge
        batteryPercentage = calculateBatteryPercentage(get_voltage(vbat_voltage))
        showCharge(batteryPercentage)
        # print(f"{get_voltage(vbat_voltage)}v gives {batteryPercentage}% battery left" )

        for i in range(9):
            # pull up logic means button low when pressed
            if not buttons[i].value: 
                if pressed[i] == False:
                    pressed[i] = True
                    if commands[i] != None:
                        commands[i]()
            else: pressed[i] = False


    print("BLE connection ended:")
    ble.start_advertising(advertisement)
