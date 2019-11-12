#!/bin/python
import random

ROWS_FLOOR = 6
ROWS_CEIL = 100
COLS_FLOOR = 21
COLS_CEIL = 100
VAR_COUNT_FLOOR = 20
VAR_COUNT_CEIL = 1000


def generate_input():
    output_list = []
    rows = random.randint(ROWS_FLOOR, ROWS_CEIL)
    cols = random.randint(COLS_FLOOR, COLS_CEIL)
    var_count = random.randint(VAR_COUNT_FLOOR, VAR_COUNT_CEIL)
    output_list.append((rows, cols, var_count,))
    append_rand_val(output_list, rows, cols, var_count)
    return output_list


def append_rand_val(output_list, rows, cols, var_count):
    iter_list = [(random.randint(ROWS_FLOOR, rows), random.randint(COLS_FLOOR, cols), random.randint(1, 100),) for i in
                 range(var_count)]
    output_list.extend(iter_list)
    print(output_list)


def write_out(output_list):
    with open("input.txt", "w") as f:
        for v_tuple in output_list:
            f.write("{}\n".format(" ".join(map(str, v_tuple))))


if __name__ == "__main__":
    output = generate_input()
    write_out(output)
