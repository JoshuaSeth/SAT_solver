from SAT_helper_functions import flatten, print_assignments_as_sudoku, read_cnf_from_dimac
from generate_16x16_rule import parse_and_pad
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" #these are the digits you will use for conversion back and forth


with open("hexa-2.txt", "r") as sudoku:
    with open("easy_sudoku_dimac.txt", "w") as write_sdk:
        index_1 = 0
        for line in sudoku.readlines():
            index_1+=1
            index_2 = 0
            line = line.replace(".", "").replace(" ", "").replace("\n", "")
            print(line)

            for char in line:

                index_2+=1
                string = parse_and_pad(index_1) 
                string+= parse_and_pad(index_2)
                print(char)
                string+= parse_and_pad(chars.index(char.upper())+ 1)
                print(string)
                write_sdk.write(string + " \n")

sudoku = read_cnf_from_dimac("easy_sudoku_dimac.txt")
print_assignments_as_sudoku(flatten(sudoku), size=16, header="Extreme easy sudoku.txt", flush=False)



