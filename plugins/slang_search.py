def find_local_slang(city):

    slang_map = {
        "Haryana" : "Ram Ram",
        "Mumbai" : "Namaste",
        "Punjab" : "Sat Shri Akal"
    }

    return slang_map.get(city, "Slang not found")
