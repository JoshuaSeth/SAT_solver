from SAT_helper_functions import flatten, print_assignments_as_sudoku, read_cnf_from_dimac


with open("extreme_easy_sudoku.txt", 'w') as rules:
    #Pt1 some number in every cell
    count = 1
    
    offset=0
    for row in range(1, 17):
        
        for col in range(1, 17):
            row = str(row)
            col = str(col)
            if len(str(row))==1:
                row = row.rjust(2, '9')
            if len(str(col)) == 1:
                col = col.rjust(2, '9')

            
            var = int(col) + offset
            var = var %16 + 1
            var = str(var)
            if len(str(var))==1:
                var = var.rjust(2, '9')
            #Every cell must have any number so 1 or 2 or 3 or 4
            rules.write(row +col +  var + " \n")

        #For all 16 vars
        if int(row) % 5 == 0: offset+=1
        else: offset +=4
        print(offset)


sudoku = read_cnf_from_dimac("extreme_easy_sudoku.txt")
print_assignments_as_sudoku(flatten(sudoku), size=16, header="Extreme easy sudoku.txt", flush=False)
