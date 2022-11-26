import time
import board
import alarm
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
# For us
#from adafruit_hid.keyboard_layout_us import KeyboardLayout
#from adafruit_hid.keycode import Keycode
# For azerty
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode

# Setup IO
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 1  

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

# Define functions
def get_voltage(pin):
    return (pin.value * 3.7) / 65536 * 2

def calculateBatteryPercentage(voltage):
    minVoltage = 4
    maxVoltage = 4.5
    percentage = (voltage- minVoltage) / (maxVoltage - minVoltage)*100
    return max(0, min(100, percentage))

def showCharge(charge:int):
    hue = int(charge/100/3*255)
    # print(f"hue: {hue} gives: RGB{fancy.CRGB(fancy.CHSV(hue,255,255))}")
    led[0] = fancy.CHSV(hue,255,255).pack()
    
pressed = [False for i in range(9)]
commands = [None for i in range(9)]

# Setup BLE
vbat_voltage = analogio.AnalogIn(board.VOLTAGE_MONITOR)

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

#Setup key actions
def funcDisconnect():
    print("Disconnecting")
    connection = ble.connections[0]
    connection.disconnect()
    led[0] = (255,0,0)
    time.sleep(2)

def funcDeepSleep():
    button_1.deinit()
    pin_alarm = alarm.pin.PinAlarm(pin=board.A0, value=False, pull=True)
    print("Shutting down")
    # Exit the program, and then deep sleep until the alarm wakes us.
    led[0] = (0,0,0)
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
    # Does not return, so we never get here.

    
commands[0] = lambda: kl.write("button brokie :(")
commands[1] = funcDeepSleep
commands[2] = lambda: k.send(Keycode.CONTROL, Keycode.L)
commands[3] = lambda: k.send(Keycode.CONTROL, Keycode.X)
commands[4] = lambda: k.send(Keycode.CONTROL, Keycode.C)
commands[5] = lambda: k.send(Keycode.CONTROL, Keycode.V)
commands[6] = lambda: k.send(Keycode.LEFT_ARROW)
commands[7] = lambda: k.send(Keycode.RIGHT_ARROW)
commands[8] = lambda: k.send(Keycode.BACKSPACE)

# commands[0] = func1
# commands[1] = lambda: k.send(Keycode.CONTROL, Keycode.L)
# commands[2] = lambda: k.send(Keycode.BACKSPACE)
# commands[3] = lambda: k.send(Keycode.LEFT_ARROW)
# commands[4] = lambda: k.send(Keycode.RIGHT_ARROW)
# commands[5] = lambda: k.send(Keycode.SPACE)
# commands[6] = lambda: k.send(Keycode.CONTROL, Keycode.X)
# commands[7] = lambda: k.send(Keycode.CONTROL, Keycode.C)
# commands[8] = lambda: k.send(Keycode.CONTROL, Keycode.V)

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

        for i in range(9):
            # pull up logic means button down when pressed
            if not buttons[i].value: 
                if pressed[i] == False:
                    pressed[i] = True
                    commands[i]()
            else: pressed[i] = False

    print("BLE connection ended.")
    ble.start_advertising(advertisement)

