
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" #these are the digits you will use for conversion back and forth

def parse_and_pad(input):
    result = str(input)
    if len(result) == 1:
        result = result.rjust(2, '9')
    return result


with open("16x16_gen_rules.txt", 'w') as rules:
    #Pt1 some number in every cell
    for col in range(1, 17):
        for row in range(1, 17):
            row = str(row)
            col = str(col)
            if len(str(row))==1:
                row = row.rjust(2, '9')
            if len(str(col)) == 1:
                col = col.rjust(2, '9')

            #For all 16 vars
            for var in range(1, 17):
                var = str(var)
                if len(str(var))==1:
                    var = var.rjust(2, '9')
                #Every cell must have any number so 1 or 2 or 3 or 4
                rules.write(row +col +  var + " ")

                
                    
            
            rules.write("0\n")

    #Pt 2 only 1 number per cell
    for col in range(1, 17):
        for row in range(1, 17):
            row = str(row)
            col = str(col)
            if len(str(row))==1:
                row = row.rjust(2, '9')
            if len(str(col)) == 1:
                col = col.rjust(2, '9')
            #For all 16 vars
            for var in range(1, 17):
                var = str(var)
                if len(str(var))==1:
                    var = var.rjust(2, '9')

                    
                #Only 1 number per cell
                for var_2 in range(1, 17):
                    var_2 = str(var_2)
                    if len(str(var_2))==1:
                        var_2 = var_2.rjust(2, '9')
                    if var != var_2:
                        var_2_str =  "-"+ row +col +  var_2
                        var_1_str =  "-"+ row +col +  var
                        rules.write(var_1_str + " " + var_2_str + " 0\n")
    
    #Pt 3 every number once per column
    for col in range(1, 17):
        for row in range(1, 17):
            row = str(row)
            col = str(col)
            if len(str(row))==1:
                row = row.rjust(2, '9')
            if len(str(col)) == 1:
                col = col.rjust(2, '9')
            for row_2 in range(1, 17):
                row_2 = str(row_2)
                if len(row_2)==1:
                    row_2 = row_2.rjust(2, '9')
                #For all 16 vars
                for var in range(1, 17):
                    var = str(var)
                    if len(str(var))==1:
                        var = var.rjust(2, '9')
                    if row != row_2:
                        row_2_str =  "-"+ row_2 +col+ var
                        row_1_str =  "-" + row + col+ var
                        rules.write(row_1_str + " " + row_2_str + " 0\n")

    #Pt 4 every number once per row
    for col in range(1, 17):
        for row in range(1, 17):
            row = str(row)
            col = str(col)
            if len(str(row))==1:
                row = row.rjust(2, '9')
            if len(str(col)) == 1:
                col = col.rjust(2, '9')
            for col_2 in range(1, 17):
                col_2 = str(col_2)
                if len(col_2)==1:
                    col_2 = col_2.rjust(2, '9')
                #For all 16 vars
                for var in range(1, 17):
                    var = str(var)
                    if len(str(var))==1:
                        var = var.rjust(2, '9')
                    if col != col_2:
                        col_2_str =  "-"+  row +col_2 + var
                        col_1_str =  "-"+  row +col + var
                        rules.write(col_1_str + " " + col_2_str + " 0\n")

    #Now loop through areas of cells
    for col in range(1,5):
        for row in range(1,5):
            for var in range(1,17):
                for col_2 in range(1,5):
                    for row_2 in range(1,5):
                        if col != col_2 or row != row_2:
                            print(col, col_2, row, row_2)
                            col_str = parse_and_pad(col)
                            row_str = parse_and_pad(row)
                            var_str = parse_and_pad(var)
                            col_2_str = parse_and_pad(col_2)
                            row_2_str = parse_and_pad(row_2)

                            str_1 = "-"+row_str+col_str+var_str
                            str_2 = "-"+row_2_str+col_2_str+var_str

                            rules.write(str_1 + " " +str_2 + " 0\n")
    
    #Now loop through areas of cells
    for col in range(5,9):
        for row in range(5,9):
            for var in range(1,17):
                for col_2 in range(5,9):
                    for row_2 in range(5,9):
                        if col != col_2 or row != row_2:
                            print(col, col_2, row, row_2)
                            col_str = parse_and_pad(col)
                            row_str = parse_and_pad(row)
                            var_str = parse_and_pad(var)
                            col_2_str = parse_and_pad(col_2)
                            row_2_str = parse_and_pad(row_2)

                            str_1 = "-"+row_str+col_str+var_str
                            str_2 = "-"+row_2_str+col_2_str+var_str

                            rules.write(str_1 + " " +str_2 + " 0\n")

    #Now loop through areas of cells
    for col in range(9,13):
        for row in range(9,13):
            for var in range(1,17):
                for col_2 in range(9,13):
                    for row_2 in range(9,13):
                        if col != col_2 or row != row_2:
                            print(col, col_2, row, row_2)
                            col_str = parse_and_pad(col)
                            row_str = parse_and_pad(row)
                            var_str = parse_and_pad(var)
                            col_2_str = parse_and_pad(col_2)
                            row_2_str = parse_and_pad(row_2)

                            str_1 = "-"+row_str+col_str+var_str
                            str_2 = "-"+row_2_str+col_2_str+var_str

                            rules.write(str_1 + " " +str_2 + " 0\n")

    #Now loop through areas of cells
    for col in range(13,17):
        for row in range(13,17):
            for var in range(1,17):
                for col_2 in range(13,17):
                    for row_2 in range(13,17):
                        if col != col_2 or row != row_2:
                            print(col, col_2, row, row_2)
                            col_str = parse_and_pad(col)
                            row_str = parse_and_pad(row)
                            var_str = parse_and_pad(var)
                            col_2_str = parse_and_pad(col_2)
                            row_2_str = parse_and_pad(row_2)

                            str_1 = "-"+row_str+col_str+var_str
                            str_2 = "-"+row_2_str+col_2_str+var_str

                            rules.write(str_1 + " " +str_2 + " 0\n")
    


