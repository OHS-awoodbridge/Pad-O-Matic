import random
import time
from circular_buffer import *

working_rand_int = 0
bit_counter = 0
pad_size = 64

pad_rand_array = CircularBuffer(1000)

def add_bit(true_rand:bool):
    """adds random digits to pad_array using random bits"""
    global working_rand_int
    global bit_counter
    if not true_rand:
        bit = random.randint(0,1)
    working_rand_int = (working_rand_int << 1) | bit
    bit_counter += 1

    if bit_counter == 8:
        bit_counter = 0
        if working_rand_int <= 250:
            if pad_rand_array.is_full():
                pad_rand_array.dequeue()
            pad_rand_array.enqueue(working_rand_int % 10)
        working_rand_int = 0

def print_pad(length:int) -> str:
    pad_output = "Length =" + str(length)+ "\n----PAD BEGIN----"
    for i in range(length):
        if i % 25 == 0:
            pad_output += "\n"
        elif i % 5 == 0:
            pad_output += " "
        pad_output += str(pad_rand_array.dequeue())
    pad_output += "\n-----PAD END----- \n\n--Conversion Table--\nCode-0  B-70  P-80  FIG-90\n   A-1  C-71  Q-81  (.)-91\n   E-2  D-72  R-82  (:)-92\n   I-3  F-73  S-83  (')-93\n   N-4  G-74  U-84  ( )-94\n   O-5  H-75  V-85  (+)-95\n   T-6  J-76  W-86  (-)-96\n        K-77  X-87  (=)-97\n        L-78  Y-88  (?)-98\n        M-79  Z-89  SPC-99 "
    return pad_output

prev_time = time.monotonic()

while True:
    add_bit(False)
    now = time.monotonic()
    if now > prev_time + 20:
        print(print_pad(70))
        prev_time = now




