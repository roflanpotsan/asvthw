import pandas as pd
from itertools import product
from copy import deepcopy


def get_pdnf(vector):
    if len(vector) == 0 or (len(vector) & (len(vector) - 1)) != 0:
        return
    return [(len(bin(len(vector))[2:]) - 1 - len(bin(i)[2:])) * "0" + bin(i)[2:] for i in range(len(vector)) if vector[i] == '1']


def hamming_dist(first, second):
    return sum(-(len(first) ** 2) if '~' in (x1, x2) and x1 != x2 else x1 != x2 for x1, x2 in zip(first, second)), [idx for idx, (x1, x2) in enumerate(zip(first, second)) if x1 != x2]


def group(perfect_dnf):
    return {key: [implicant for implicant in perfect_dnf if implicant.count('1') == key] for key in set(implicant.count('1') for implicant in perfect_dnf)}


def get_core_implicant(vector):
    return ''.join([f"{'!' if vector[i] == '0' else ''}x{len(vector) - i - 1}" if vector[i] != '~' else '' for i in range(len(vector))])


def find_primaries(perfect_dnf):
    primary_implicants = []
    current_groups = group(perfect_dnf)

    while True:
        used_implicants = set()
        new_groups = {}
        for group_id in sorted(current_groups.keys()):
            if group_id + 1 in current_groups:
                for k1, k2 in product(current_groups[group_id], current_groups[group_id + 1]):
                    result = hamming_dist(k1, k2)
                    if result[0] == 1:
                        used_implicants.update([k1, k2])
                        new_groups.setdefault(group_id, set()).add(k1[:result[1][0]] + '~' + k1[result[1][0] + 1:])
            primary_implicants += [im for im in current_groups[group_id] if im not in used_implicants]
        if not used_implicants:
            break
        current_groups = deepcopy(new_groups)

    return primary_implicants

def minify(pdnf, primary_implicants):
    table = {}

    minimized_dnf = set()
    for implicant in pdnf:
        marks, last_prim = 0, None
        for p_index, prim in enumerate(primary_implicants):
            if sum([prim[i] in ('~', implicant[i]) for i in range(len(implicant))]) == len(implicant):
                table.setdefault(prim, {}).update({implicant: 'x'})
                marks += 1
                last_prim = prim
            else:
                table.setdefault(prim, {}).update({implicant: ''})
        if marks == 1:
            minimized_dnf.add(last_prim)
    remaining_primaries_covering, uncovered_implicants = {}, set(pdnf)

    for implicant in pdnf:
        marks = 0
        for primary_implicant in minimized_dnf:
            if table[primary_implicant][implicant] == 'x':
                uncovered_implicants.discard(implicant)
                marks += 1
        if marks == 0:
            for leftover_primary_implicants in set(primary_implicants) - minimized_dnf:
                if table[leftover_primary_implicants][implicant]:
                    remaining_primaries_covering.setdefault(leftover_primary_implicants, set()).add(implicant)

    while uncovered_implicants:
        new_primary_implicant = max(remaining_primaries_covering, key=lambda x: (len(remaining_primaries_covering[x]), x.count('~'),))
        minimized_dnf.add(new_primary_implicant)
        uncovered_implicants -= remaining_primaries_covering[new_primary_implicant]
        for primary_implicant in remaining_primaries_covering:
            if primary_implicant != new_primary_implicant:
                remaining_primaries_covering[primary_implicant] -= remaining_primaries_covering[new_primary_implicant]
        del remaining_primaries_covering[new_primary_implicant]

    indexes = sorted(primary_implicants)
    indexes = sorted(list(minimized_dnf))
    df = pd.DataFrame([table[primary_implicant].values() for primary_implicant in indexes], columns=pdnf, index=indexes)
    df.to_excel('pre_min.xlsx')
    df = pd.DataFrame([table[primary_implicant].values() for primary_implicant in indexes], columns=pdnf, index=indexes)
    df.to_excel('min.xlsx')

    return minimized_dnf


f_vector = '0100001111011100001001101101110101000011000011011010111011010100'
perfect_dnf = get_pdnf(f_vector)


def print_implicants(implicant_list, title):
    print(title)
    for i, imp in enumerate(implicant_list):
        print(f'{get_core_implicant(imp):<18}\t{imp}')

primary_implicant_list = find_primaries(perfect_dnf)
minimized = minify(perfect_dnf, primary_implicant_list)

print_implicants(perfect_dnf, 'Miniterms:')
print_implicants(primary_implicant_list, 'Primary implicants:')
print_implicants(minimized, 'Minimized DNF:')
print('Minimized DNF: ', end='')
for i, imp in enumerate(minimized):
    print((i != 0) * ' + ' + get_core_implicant(imp).replace(' ', ''), end='')
