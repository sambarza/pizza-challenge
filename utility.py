from cat.looking_glass.cheshire_cat import CheshireCat

def split_long_strings(input_list, max_length=79):
    result_list = []
    
    for string in input_list:
        if len(string) <= max_length:
            result_list.append(string)
        else:
            # Suddivide la stringa in sottostringhe di massimo max_length caratteri
            for i in range(0, len(string), max_length):
                result_list.append(string[i:i + max_length])
    
    return result_list