import ast
import re

def get_rows(vector):
    if len(vector) == 0 or (len(vector) & (len(vector) - 1)) != 0:
        return
    return [(len(bin(len(vector))[2:]) - 1 - len(bin(i)[2:])) * "0" + bin(i)[2:] for i in range(len(vector))]

def generate_boolean_permutations(n, row_vector):
    variables = [f'x{i + 1}' for i in range(n)]
    all_combinations = []

    for i in range(1, 2 ** n):
        combination = ''
        combination_vals = ''
        for j in range(n):
            if i & (1 << j):

                combination += variables[j]
                combination_vals += row_vector[j]
        all_combinations.append([combination, combination_vals])

    # Sort by length and then lexically
    all_combinations.sort(key=lambda x: (len(x[0]), x))
    return all_combinations


f_vector = '0100001111011100001001101101110101000011000011011010111011010100'
rows = get_rows(f_vector)
permutations = [generate_boolean_permutations(len(rows[_]), rows[_]) for _ in range(len(f_vector))]
zeros = set()

system_lines = []
system_lines_for_excel = []
print('--------BEFORE CLEANUP--------')
for _ in range(len(f_vector)):
    system_line = []
    for x in permutations[_]:
        if f_vector[_] == '0':
            zeros.add(tuple(x))
        system_line.append(f'{x[0]}({x[1]})')
    # system_line = system_line[:-2]
    system_line.append(f'{f_vector[_]}')
    system_lines.append(system_line)
    system_lines_for_excel.append(system_line)
for line_ in system_lines:
    print(' V '.join(line_)[:-3] + f'= {line_[-1]}')

system_lines = []
system_lines_for_excel = []
print('--------AFTER CLEANUP--------')
for _ in range(len(f_vector)):
    system_line = []
    for x in permutations[_]:
        if tuple(x) not in zeros:
            system_line.append(f'{x[0]}({x[1]})')
    # system_line = system_line[:-2]
    if len(system_line) == 0:
        continue
    system_line.append(f'{f_vector[_]}')
    system_lines.append(system_line)
for line_ in system_lines:
    print(' V '.join(line_)[:-3] + '= 1')


def getImplicants(lines):
    print('--------AFTER LOWEST RANK SELECTION--------')
    function_variables = [f'x{i + 1}' for i in range(len(rows[0]))]
    implicant_set_ = set()
    simple_implicants_ = set()
    for _line in lines:
        used_variables = set()
        new_line = []
        for item in _line:
            for variable in function_variables:
                skip = False
                for used_variable in used_variables:
                    if item.count(used_variable) > 0:
                        skip = True
                if skip:
                    break
                if item.count(variable) > 0:
                    if variable not in used_variables:
                        new_line.append(f'{item}')
                        used_variables.add(variable)
                        break
                else:
                    break
        if _line[-1] == '1':
            new_line.append(_line[-1])
        if len(new_line) == 2 and new_line[-1] == '1':
            simple_implicants_.add(new_line[0])
        elif len(new_line) == 1:
            simple_implicants_.add(new_line[0])
        else:
            implicant_set_.add(str(new_line))

    rest_implicants_set_ = set()
    for _line in implicant_set_:
        split_line = ast.literal_eval(_line)
        for item in split_line:
            if item in simple_implicants_:
                split_line.remove(item)
        if '1' in split_line:
            split_line.remove('1')
        rest_implicants_set_.add(tuple(split_line))

    return implicant_set_, simple_implicants_, rest_implicants_set_


# for line in system_lines:
#     print(line)
totalSimple = set()
while len(system_lines) > 0:
    print('------------A STEP------------')
    implicant_set, simple_implicants, rest_implicants_set = getImplicants(system_lines)
    print('----SIMPLE----')
    for simple in simple_implicants:
        totalSimple.add(simple)
        print(f'{simple} = 1')
    print('----REST----')
    for line_ in implicant_set:
        line_ = ast.literal_eval(line_)
        print(' V '.join(line_) + f'= {line_[-1]}')
    print('----REST AFTER REMOVAL----')
    keepLoop = 0
    for line_ in rest_implicants_set:
        print(' V '.join(line_) + f' = 1')
        keepLoop = keepLoop or (len(line_) > 1)
    if not keepLoop:
        break
    system_lines = [[str(item) for item in tpl] for tpl in rest_implicants_set]
    break

ans = ''
for simple in totalSimple:
    output_list = re.findall(r'\d+|\D', simple)
    output_list.remove(')')
    output_list.remove('(')
    output_list = list(filter(lambda item: item != 'x', output_list))
    # print(output_list)
    temp = ''
    for j in range(len(output_list[-1])):
        if output_list[-1][j] == '0':
            temp += '!'
        temp += 'X'
        temp += str(6 - int(output_list[j]))
    ans += temp + ' + '
ans = ans[:-3]
print('----ANSWER----')
print(ans)

# zeros_line = ''
# for zero in sorted(zeros):
#     zeros_line += f'{zero[0]}({zero[1]}) = '
# zeros_line += '0'
# print('--------ZEROS--------')
# print(zeros_line)

