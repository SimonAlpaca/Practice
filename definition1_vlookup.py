#definition
# create a vlookup definition


dict_1 = {"A1":"20%", "A2":"18%", "P":"16%"}


print(dict_1)

def vlookup(lookup_value, dict_no):
    list_keys = list(dict_no.keys())
    list_values = list(dict_no.values())
    for i in range(len(list_keys)):
        if lookup_value == list_keys[i]:
            return list_values[i]
        
print(vlookup("A1",dict_1))
print(dict_1["A1"])
