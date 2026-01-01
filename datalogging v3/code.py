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

    if bit_counter == 8:
        bit_counter = 0
        #if working_rand_int <= 29:
        if len(pad_rand_array) < 10000:
            mapped = adafruit_simplemath.map_range(working_rand_int, 0, 255, 0, 9)
            pad_rand_array.append(mapped)
            #print(working_rand_int % 10)
        working_rand_int = 0
