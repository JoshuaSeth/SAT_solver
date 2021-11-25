with open("16x16_gen_rules.txt", 'r') as rules:
    for line in rules.readlines():
        line = line[:-2]
        if len(line) != 14:
            print(line)
            print(len(line))