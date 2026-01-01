import os
import busio
import digitalio
import board
import storage
import adafruit_sdcard
import bitbangio
import random
import time

# Connect to the card and mount the filesystem.
spi = bitbangio.SPI(board.CLK, board.CMD, board.DAT0)
cs = digitalio.DigitalInOut(board.DAT3)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


#variables to handle the random number generations
working_rand_int = 0
click_count = 0
click_values = [0,0,0]
bit_counter = 0

#variables to handle the pad generation
pad_rand_array = []

#setup trigger from geiger counter
geiger = digitalio.DigitalInOut(board.D14)
geiger.direction = digitalio.Direction.INPUT

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
        if working_rand_int <= 29:
            if len(pad_rand_array) < 10000:
                pad_rand_array.append(working_rand_int % 10)
            #print(working_rand_int % 10)
        working_rand_int = 0


# Use the filesystem as normal! Our files are under /sd

# This helper function will print the contents of the SD
def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print("{0:<40} Size: {1:>10}".format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)
while True:
    #set the number of thousands of digits to collect
    counter = 10
    #create random file name
    file_name = "/sd/log"+str(random.randint(1111,9999))+".txt"
    print(file_name + " opened")
    while counter > 0:
        #collect 1000 digits, print an update every hundred
        while len(pad_rand_array) <= 1000:
            if geiger.value:
                    add_bit(True)
                    time.sleep(.004)
                    #if len(pad_rand_array) % 100 == 0 :
                    #    print(str(len(pad_rand_array)))



        print("dumping batch " + str(counter) + " of ")
        counter -= 1

        #write the digits out the file
        with open(file_name, "a") as sdc:
            for n in pad_rand_array:
                sdc.write(str(n)+"\n")
                #print(str(n))
                pad_rand_array = []
    #show the files on the sd card when finished
    #print_directory("/sd")
    print(file_name + " finshed")
