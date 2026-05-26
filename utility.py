
def str_num(string):
    return ord(string)-48

def char_num(string):
    return ord(string)-97

def upper_char_num(string):
    return ord(string)-65

def get_direction_vector(source, dest):
    drow = abs(source[0] - dest[0])
    dcol = abs(source[1] - dest[1])
    if drow > dcol:
        if dest[1] > source[1]:
            return 'down'
        else:
            return 'up'
    else:
        if dest[0] > source[0]:
            return 'right'
        else:
            return 'left'
