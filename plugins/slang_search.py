"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here
import csv 

def find_local_slang(city):
    slang_map_filename = 'example.csv' 
    slang_map = {}
    try:
        with open(slang_map_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    c, slang = row
                    slang_map[c] = slang
    except FileNotFoundError:
        pass

    return slang_map.get(city, "Slang not found")