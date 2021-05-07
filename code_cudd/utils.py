def get_bit_value(num, bit):
    if ((num >> bit) & 1) == 1:
        return True
    else:
        return False

def num_to_map(num, vars):
    return {v: get_bit_value(num, i) for i, v in enumerate(vars)}
