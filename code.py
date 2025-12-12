"""
Pad-O-Matic Geiger Counter Edition

Micro: Teensy 4.0
Pinout:
  -I2C SSD1306 128x64 Display
      GND -> GND
      VCC -> 5v
      SCL -> D19
      SDA -> D18
  -Push Button with LED Indicator
      Switch -> D17 & GND
      LED -> D16 & GND





"""






import board
import busio
import displayio
import time
import random
import digitalio
import terminalio
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import rotaryio
import adafruit_displayio_ssd1306
import adafruit_thermal_printer
#from circular_buffer import *

#variables to handle the random number generations
use_true_random = True
working_rand_int = 0
click_count = 0
click_values = [0,0,0]
bit_counter = 0

#variables to handle the pad generation
pad_rand_array = []
pad_size = 250
print_checkerboard = False
print_checkerboard = False


#setup encoder
encoder = rotaryio.IncrementalEncoder(board.D21, board.D20)
button = digitalio.DigitalInOut(board.D22)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_state = None
last_position = encoder.position

print_button = digitalio.DigitalInOut(board.D17)
print_button.direction = digitalio.Direction.INPUT
print_button.pull = digitalio.Pull.UP
print_button_state = None
print_light = digitalio.DigitalInOut(board.D16)
print_light.direction = digitalio.Direction.OUTPUT

#setup trigger from geiger counter
geiger = digitalio.DigitalInOut(board.D14)
geiger.direction = digitalio.Direction.INPUT

#setup printer
uart = busio.UART(board.TX1, board.RX1, baudrate=19200)
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)

printer = ThermalPrinter(uart)
#printer.print('Hello from CircuitPython!')
#printer.feed(3)

#eetup display
displayio.release_displays()
i2c = board.I2C()  # uses board.SCL and board.SDA
display_bus = I2CDisplayBus(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.root_group = splash

# Draw a label
text_upper = label.Label(terminalio.FONT, text="Pad-O-Matic", color=0xFFFFFF, x=0, y=4)
splash.append(text_upper)


text_lower= label.Label(terminalio.FONT, text="Qty = " + str(pad_size), color=0xFFFFFF, x=0, y=20)
splash.append(text_lower)







def add_bit(true_rand:bool):
    """adds random digits to pad_array using random bits"""
    global working_rand_int
    global bit_counter
    global click_count
    global click_values
    #just generate a random bit and add push it into the working random number
    if not true_rand:
        bit = random.randint(0,1)
        working_rand_int = (working_rand_int << 1) | bit
        bit_counter += 1

    #collect three clicks, and push it into the working random number
    else:
        #store the time the click occured
        click_values[click_count] = time.monotonic()
        click_count += 1
        if click_count == 3:
            click_count = 0
            #if the time between the first two clicks was larger add a 0
            if click_values[1] - click_values[0] > click_values[2] - click_values[1]:
                working_rand_int = (working_rand_int << 1) | 0
            #otherwise add a 1
            else:
                working_rand_int = (working_rand_int << 1) | 1
            bit_counter += 1

    if bit_counter == 5:
        bit_counter = 0
        if working_rand_int <= 30:
            if len(pad_rand_array) < 10000:
                pad_rand_array.append(working_rand_int % 10)
            #print(working_rand_int % 10)
        working_rand_int = 0

def print_pad(length:int) -> str:
    """prints the output to the thermal printer"""
    pad_body = ""
    for i in range(length):
        if i % 25 == 0:
            pad_body += "\n"
        elif i % 5 == 0:
            pad_body += " "
        pad_body += str(pad_rand_array.pop(0))


    pad_output = "Length =" + str(length)+ "\n----IN PAD BEGIN----"
    pad_output += pad_body
    pad_output += "\n-----IN PAD END----- "
    if print_checkerboard:
        pad_output +="\n\n--Conversion Table--\nCode-0  B-70  P-80  FIG-90\n   A-1  C-71  Q-81  (.)-91\n   E-2  D-72  R-82  (:)-92\n   I-3  F-73  S-83  (')-93\n   N-4  G-74  U-84  ( )-94\n   O-5  H-75  V-85  (+)-95\n   T-6  J-76  W-86  (-)-96\n        K-77  X-87  (=)-97\n        L-78  Y-88  (?)-98\n        M-79  Z-89  SPC-99 "
    pad_output += "\n\n=========================\n\n----OUT PAD BEGIN----"
    pad_output += pad_body
    pad_output += "\n-----OUT PAD END----- "
    if print_checkerboard:
        pad_output +="\n\n--Conversion Table--\nCode-0  B-70  P-80  FIG-90\n   A-1  C-71  Q-81  (.)-91\n   E-2  D-72  R-82  (:)-92\n   I-3  F-73  S-83  (')-93\n   N-4  G-74  U-84  ( )-94\n   O-5  H-75  V-85  (+)-95\n   T-6  J-76  W-86  (-)-96\n        K-77  X-87  (=)-97\n        L-78  Y-88  (?)-98\n        M-79  Z-89  SPC-99 "
        pad_output +="\n\n--Conversion Table--\nCode-0  B-70  P-80  FIG-90\n   A-1  C-71  Q-81  (.)-91\n   E-2  D-72  R-82  (:)-92\n   I-3  F-73  S-83  (')-93\n   N-4  G-74  U-84  ( )-94\n   O-5  H-75  V-85  (+)-95\n   T-6  J-76  W-86  (-)-96\n        K-77  X-87  (=)-97\n        L-78  Y-88  (?)-98\n        M-79  Z-89  SPC-99 "
    return pad_output


menu_mode = "Choose"
menu_modes = ["Pad Size", "Tr-Ps","Choose","Print"]
menu_item = "Pad Size"

def menu(code:str):
    """translates encoder operations to select and update options"""
    global menu_mode
    global menu_item
    global pad_size
    global use_true_random

    if menu_mode == "Choose":
        if code == "e+":
            if menu_item == "Pad Size":
                menu_item = "Tr-Ps"
            else:
                menu_item == "Pad Size"
        elif code == "e-":
            if menu_item == "Tr-Ps":
                menu_item = "Pad Size"
            else:
                menu_item == "Tr-Ps"
        elif code == "button":
            print(menu_item)
            menu_mode = menu_item
    elif menu_mode == "Pad Size":
        if code == "e+":
            pad_size += 5
        elif code == "e-":
            pad_size -= 5
            if pad_size < 10:
                pad_size = 10
        elif code == "button":
            menu_mode = "Choose"
    elif menu_mode == "Tr-Ps":
        if code == "e+":
            use_true_random = not use_true_random
        elif code == "e-":
            use_true_random = not use_true_random
        elif code == "button":
            menu_mode = "Choose"
    #update the screen
    draw_screen()


def draw_screen():
    global menu_mode
    global menu_item
    global pad_size
    global use_true_random

    menu_screen = "Buffer = " + str(len(pad_rand_array)) + "\n"
    if menu_mode == "Choose":
        if menu_item == "Pad Size":
            menu_screen += "- Pad Size = " + str(pad_size)
        else:
            menu_screen += "  Pad Size = " + str(pad_size)
        if menu_item == "Tr-Ps":
            menu_screen += "\n- Random = " + str(use_true_random)
        else:
            menu_screen += "\n  Random = " + str(use_true_random)
    elif menu_mode == "Pad Size":
        menu_screen += "> Pad Size = " + str(pad_size)
        menu_screen += "\n  Random = " + str(use_true_random)
    elif menu_mode == "Tr-Ps":
        menu_screen += "  Pad Size = " + str(pad_size)
        menu_screen += "\n> Random = " + str(use_true_random)

    text_lower.text = menu_screen




prev_time = time.monotonic()
draw_screen()

while True:
    now = time.monotonic()
    if now > prev_time + 5:
        prev_time = now
        draw_screen()
    #handler for encoder
    position = encoder.position
    if position != last_position:
        if position < last_position:
           menu("e-")
        elif position > last_position:
           menu("e+")
        last_position = position

    #handle the button
    if not button.value and button_state is None:
        button_state = "pressed"
    if button.value and button_state == "pressed":
        menu("button")
        button_state = None
        time.sleep(.2)


    if len(pad_rand_array) > pad_size:
        print_light.value = True
    else:
        print_light.value = True


    if not print_button.value and print_button_state is None:
        print_button_state = "pressed"
    if print_button.value and print_button_state == "pressed":
        if len(pad_rand_array) > pad_size:
            out = print_pad(250)
            #printer.print(out)
            print(out)


        else:
            print("Insufficient Buffer Size")
        print_button_state = None
        time.sleep(.2)

    #add random values to the buffer
    if use_true_random:
        if geiger.value:
            add_bit(True)
            time.sleep(.001)
    else:
        add_bit(False)

