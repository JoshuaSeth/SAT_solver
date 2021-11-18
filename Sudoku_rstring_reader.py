import numpy as np
import math

sudoku_file = '1000 sudokus.txt'
thousand_sudokus = open(sudoku_file, 'r')
sudoku_lines = thousand_sudokus.readlines()
sudoku_1 = sudoku_lines[8]

sudokus = sudoku_lines[0:3]
print(sudokus)

def generate_matrix(string):
    size = math.floor(math.sqrt(len(sudoku_lines[0])))
    matrix = [[0 for x in range(size)] for x in range(size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] = string[i * 9 + j]
    return np.array(matrix)


def sudoku_to_DIMACS(sudokus):
    """Prints set of clauses given a sudoku as a string"""  # code needs to be cleaned up after it is finished
    count = 0
    list = []

    for sudoku in sudokus:
        for element in sudoku:
            count = count + 1
            if count > 9:
                count = 0
            if element != ".":
                row = math.ceil(count / 9)
                column = count - (row - 1) * 9
                variable = str(row) + str(column) + str(element) + str(' ') + str('0')
                list.append(variable)
    return list

def all_sudokus_at_once(sudokus):
    sudoku_file = sudokus
    thousand_sudokus = open(sudoku_file, 'r')
    sudoku_lines = thousand_sudokus.readlines()

    sudoku_matrices = []
    for i in range(len(sudoku_lines)):
        matrices = generate_matrix(sudoku_lines[i])
        sudoku_matrices.append(matrices)
    
    rows = []
    cols = []
    for i in range(len(sudoku_matrices)):
        row, col = np.where(sudoku_matrices[i] != '.')
        row, col = [int(i) for i in row], [int(i) for i in col]
        rows.append(row)
        cols.append(col)

    return rows, cols, sudoku_matrices, sudoku_lines

rows, cols, sudoku_matrices, sudoku_lines = all_sudokus_at_once('1000 sudokus.txt')

def make_row__col_strings(rows, cols):
    all_rows_plus_one = []
    all_cols_plus_one = []
    for i in range(len(rows)):
        row_test = [element + 1 for element in rows[i]]
        all_rows_plus_one.append(row_test)
    for i in range(len(cols)):
        row_cols = [element + 1 for element in cols[i]]
        all_cols_plus_one.append(row_cols)

    sudoku_values = []
    for j in range(len(sudoku_matrices)):
        for i in range(len(rows[j])):
            matrix_values = sudoku_matrices[j][rows[j][i]][cols[j][i]]
            sudoku_values.append(matrix_values)
    sudoku_values = ''.join(sudoku_values)

    row_and_col = []
    for j in range(len(rows)):
        for i in range(len(all_rows_plus_one[j])):
            individual_strings = str(all_rows_plus_one[j][i]) + str(all_cols_plus_one[j][i])
            row_and_col.append(individual_strings)

    all_coords_and_values = []
    all_dimac = []
    for i in range(len(row_and_col)):
        test = row_and_col[i] + sudoku_values[i]
        all_coords_and_values.append(test)
        test = all_coords_and_values[i] + str(' ') + str('0')
        all_dimac.append(test)
    return all_dimac

all_dimac_clauses = make_row__col_strings(rows, cols)

def get_new_line_location(sudoku_lines):
    count_non_dots = []
    for i in range(len(sudoku_lines)):
        non_dots = len(sudoku_lines[i]) - 1 - sudoku_lines[i].count('.')
        count_non_dots.append(non_dots)
    return count_non_dots

location_list = get_new_line_location(sudoku_lines)

def cumsum_list(list):
    cumsum_list = []
    cumsum = 0
    for element in list:
        cumsum += element
        cumsum_list.append(cumsum)
    return cumsum_list

cumsum_list = cumsum_list(location_list)

real_list = []
for i in range(len(cumsum_list)):
    new_elements = cumsum_list[i] + 1 * i
    real_list.append(new_elements)

for j in range(len(real_list)):
    all_dimac_clauses.insert(real_list[j], 'XXXXXXXX')
