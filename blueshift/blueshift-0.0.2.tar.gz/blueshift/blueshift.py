#!/usr/bin/env python3

import os
import logging
from string import *
from random import shuffle

def generate(number_of_serials, length_of_serial, use_numbers="y", use_uppercase="y", use_lowercase="y", use_symbols="y"):
    if use_numbers == False:
        use_numbers = ""
    if use_uppercase == False:
        use_uppercase = ""
    if use_lowercase == False:
        use_lowercase = ""
    if use_symbols == False:
        use_symbols = ""

    list_of_character_lists = create_list_of_character_lists(length_of_serial, use_numbers, use_uppercase, use_lowercase, use_symbols)
    total_possible_serials = len(list_of_character_lists[0]) ** length_of_serial

    if total_possible_serials < number_of_serials:
        logging.error("Total possible serial numbers is less than the requested amount!")
        return

    generateSerialNumbers(number_of_serials, length_of_serial, list_of_character_lists, total_possible_serials)

def create_list_of_character_lists(length_of_serial, use_numbers, use_uppercase, use_lowercase, use_symbols):
    characterList = create_character_list(use_numbers, use_uppercase, use_lowercase, use_symbols)
    list_of_character_lists = []

    for i in range(length_of_serial):
        shuffle(characterList)
        list_of_character_lists.append(characterList.copy())

    return list_of_character_lists

def create_character_list(use_numbers, use_uppercase, use_lowercase, use_symbols):
    character_list = []

    if use_numbers:
        character_list += digits

    if use_uppercase:
        character_list += ascii_uppercase

    if use_lowercase:
        character_list += ascii_lowercase

    if use_symbols:
        character_list += punctuation

    return character_list

def generateSerialNumbers(number_of_serials, length_of_serial, list_of_character_lists, total_possible_serials):
    add_serials_to_array(number_of_serials, length_of_serial, list_of_character_lists, total_possible_serials)

def add_serials_to_array(number_of_serials, length_of_serial, list_of_character_lists, total_possible_serials):
    global serial_array
    serial_array = []

    single_serial_string = ""
    index_list = [0] * length_of_serial
    distance_between_serials = int(total_possible_serials / number_of_serials)

    for i in range(number_of_serials):
        for i in range(length_of_serial):
            single_serial_string += list_of_character_lists[i][index_list[i]]

        serial_array.append(single_serial_string)
        single_serial_string = ""

        incerase_index_vector(index_list, len(list_of_character_lists[0]), distance_between_serials)

def incerase_index_vector(index_vector, rollover_number, distance_between_serials):
    increase_value = 0

    for x in reversed(range(len(index_vector))):
        increase_value = distance_between_serials % rollover_number
        index_vector[x] += increase_value

        if (index_vector[x] >= rollover_number):
            index_vector[x] -= rollover_number

            if (x > 0):
                index_vector[x - 1] += 1

        distance_between_serials = int(distance_between_serials / rollover_number)

def get_serials():
    return serial_array