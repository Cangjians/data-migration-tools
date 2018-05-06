#!/usr/bin/python3


from collections import OrderedDict
import itertools
import sys


def get_lines(tablepath):
    with open(tablepath, 'r') as table:
        for line in table:
            line = line.strip(' \n')

            if not line or line.startswith('#'):
                yield line
                continue

            (char, sc, zh, b5, hk, tw, kj, hira, kata, punc, symb, cj3, cj5, short, freq) = line.split(' ')

            yield {
                'char': char, 'sc': sc, 'zh': zh, 'b5': b5, 'hk': hk, 'tw': tw, 'kj': kj, 'hira': hira, 'kata': kata,
                'punc': punc, 'symb': symb, 'cj3': cj3, 'cj5': cj5, 'short': short, 'freq': freq,
            }


###################################################################
#                                                                 #
#                                                                 #
# TODO: Do we need the xorder at all? or just the canonical code? #
#                                                                 #
#                                                                 #
###################################################################
def get_xorder(code, all_codes, *, cj=5):
    if (cj == 3 and not code.endswith('x')) or (cj == 5 and not code.startswith('x')):
        # This is already a canonical code
        return 0, code

    # This is a special case
    if code == 'xxxxx':
        return 0, code

    if all_codes == [code]:
        return 0, code

    canonical_code = code
    xorder = 0

    if cj == 3:
        while canonical_code.endswith('x'):
            canonical_code = canonical_code[:-1]
            xorder += 1

        # Get the real canonical code, if longer than 5; e.g 'abcde' suffixed with an 'x' becomes 'abcdx'
        for c in all_codes:
            if c !=  code and c.startswith(canonical_code):
                return xorder, c

    elif cj == 5:
        while canonical_code.startswith('x'):
            canonical_code = canonical_code[1:]
            xorder += 1

        # Get the real canonical code, if longer than 5; e.g 'abcde' prefixed with an 'x' becomes 'xabcd'
        for c in all_codes:
            if c !=  code and c.startswith(canonical_code):
                return xorder, c

    return 0, code


def group_codes(codes, *, cj=5):
    grouped = OrderedDict()
    codes =  [c for c in codes.split(',') if c != 'NA']

    for code in codes:
        _, canonical_code = get_xorder(code, codes, cj=cj)

        if canonical_code not in grouped:
            grouped[canonical_code] = []

        if code == canonical_code:
            grouped[canonical_code].insert(0, code)

        else:
            grouped[canonical_code].append(code)

    grouped = list(grouped.values())

    # We really want only two groups: the one which gets the non-zero frequency, and then the rest
    if len(grouped) > 2:
        grouped = [grouped[0]] + [list(itertools.chain(*grouped[1:]))]

    return grouped


new_table = []

for line in get_lines('data/table.txt'):
    if isinstance(line, str):
        # This is a comment, or an empty line
        new_table.append(line)
        continue

    if line['freq'] == '0':
        new_table.append(' '.join((
            line['char'], line['sc'], line['zh'], line['b5'], line['hk'], line['tw'], line['kj'], line['hira'],
            line['kata'], line['punc'], line['symb'], line['cj3'], line['cj5'], line['short'], line['freq'],
        )))
        continue

    grouped_cj3 = group_codes(line['cj3'], cj=3)
    grouped_cj5 = group_codes(line['cj5'], cj=5)

    if len(grouped_cj3) == 1 and grouped_cj3 == grouped_cj5:
        new_table.append(' '.join((
            line['char'], line['sc'], line['zh'], line['b5'], line['hk'], line['tw'], line['kj'], line['hira'],
            line['kata'], line['punc'], line['symb'], line['cj3'], line['cj5'], line['short'], line['freq'],
        )))
        continue

    short = line['short']
    freq = line['freq']
    num = max(len(grouped_cj3), len(grouped_cj5))

    for i in range(num):
        try:
            cj3 = grouped_cj3[i]
        except IndexError:
            cj3 = ['NA']

        try:
            cj5 = grouped_cj5[i]
        except IndexError:
            cj5 = ['NA']

        new_table.append(' '.join((
            line['char'], line['sc'], line['zh'], line['b5'], line['hk'], line['tw'], line['kj'], line['hira'],
            line['kata'], line['punc'], line['symb'], ','.join(cj3), ','.join(cj5), short, freq,
        )))

        freq = '0'
        short = 'NA'

with open('data/table.txt', 'w') as f:
    for line in new_table:
        f.write(f'{line}\n')
