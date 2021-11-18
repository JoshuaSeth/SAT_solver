import numpy as np
import math

sudoku_file = '1000 sudokus.txt'
thousand_sudokus = open(sudoku_file, 'r')
sudoku_lines = thousand_sudokus.readlines()

def generate_matrix(string):
    size = math.floor(math.sqrt(len(sudoku_lines[0])))
    matrix = [[0 for x in range(size)] for x in range(size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] = string[i * 9 + j]
    return np.array(matrix)

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
        test = all_coords_and_values[i] #+ str(' ') + str('0')
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

cumsum_list_sudokus = cumsum_list(location_list)

def get_sudoku_int_lol(cumsum_list):
    real_list = []
    for i in range(len(cumsum_list)):
        new_elements = cumsum_list[i] + 1 * i
        real_list.append(new_elements)

    for j in range(len(real_list)):
        all_dimac_clauses.insert(real_list[j], 'XXXXXXXX')

    sudoku_list = []
    for i in range(len(real_list) -1):
        sudoku = all_dimac_clauses[real_list[i] + 1:real_list[i+1]]
        sudoku_list.append(sudoku)

    def list_to_list_of_lists(lst):
        return list(map(lambda el:[el], lst))

    sudoku_lol = []
    for i in range(len(sudoku_list)):
        sudoku_individual_lol = list_to_list_of_lists(sudoku_list[i])
        sudoku_lol.append(sudoku_individual_lol)

    int_sudokus_lol = []
    for i in range(len(sudoku_lol)):
        int_sudoku_lol = [[int(float(j)) for j in i] for i in sudoku_lol[i]]
        int_sudokus_lol.append(int_sudoku_lol)

    return int_sudokus_lol

int_sudokus_lol = get_sudoku_int_lol(cumsum_list_sudokus)
print(int_sudokus_lol)
