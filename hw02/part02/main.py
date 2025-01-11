# from model.specs import *
# from model.symbol_table import SymbolTable
# from model.utils import classify_token
#
# if __name__ == "__main__":
#     symbol_table = SymbolTable()
#     fip = []
#
#     try:
#         with open("code.txt", "r") as file:
#             line_num = 0
#             for line in file:
#                 line_num += 1
#                 token = ""
#                 i = 0
#
#                 stripped_line = line.strip()
#
#                 if stripped_line \
#                         and not stripped_line.endswith("{") \
#                         and not stripped_line.startswith("}") \
#                         and not stripped_line.endswith(";"):
#                     raise Exception(f"Syntax error at line {line_num}: missing semicolon at the end of the line")
#
#                 while i < len(line):
#                     char = line[i]
#
#                     if char.isspace() or char in separators or any(line[i:i + 2] in operators for _ in range(2)):
#                         if token:
#                             atom_type = classify_token(token, keywords, operators, separators)
#
#                             if atom_type != "error":
#                                 atom_dict[atom_type].add(token)
#
#                                 if atom_type in ["ID", "CONST"]:
#                                     symbol_table.insert(token)
#
#                                 atom_code = atom_codes.get(atom_type, atom_codes.get(token, "-"))
#
#                                 fip.append(
#                                     (token, atom_code,
#                                      symbol_table.find(token) if atom_type in ["ID", "CONST"] else "-"))
#
#                             else:
#                                 raise Exception(f"Lexical error at line {line_num}: invalid token '{token}'")
#
#                         token = ""
#
#                         if char in separators or any(line[i:i + 2] in operators for _ in range(2)):
#                             if i + 1 < len(line) and line[i:i + 2] in operators:
#                                 operator = line[i:i + 2]
#                                 atom_dict["operators"].add(operator)
#                                 atom_code = atom_codes.get(operator, "-")
#                                 fip.append((operator, atom_code, "-"))
#                                 i += 1
#                             else:
#                                 separator = char
#                                 atom_dict[classify_token(separator, keywords, operators, separators)].add(separator)
#                                 atom_code = atom_codes.get(separator, "-")
#                                 fip.append((separator, atom_code, "-"))
#
#                         i += 1
#                     else:
#                         token += char
#                         i += 1
#
#     except Exception as e:
#         print(e)
#
#     with open("results/atoms.txt", "w") as f:
#         for category, atoms in atom_dict.items():
#             f.write(f"{category}: ")
#             for atom in atoms:
#                 f.write(f"{atom}    ")
#             f.write("\n")
#
#     with open("results/fip.txt", "w") as f:
#         for name, token, index in fip:
#             if 3 < len(name) < 7:
#                 f.write(f"{name}\t\t\t{token}\t\t{index}\n")
#             elif len(name) >= 7:
#                 f.write(f"{name}\t\t{token}\t\t{index}\n")
#             else:
#                 f.write(f"{name}\t\t\t\t{token}\t\t{index}\n")
#
#     sorted_symbol_table = sorted(symbol_table.to_list(), key=lambda x: x[1])
#
#     with open("results/ts.txt", "w") as f:
#         for symbol, index, left, right in sorted_symbol_table:
#             if len(symbol) > 3:
#                 f.write(f"{symbol}\t\t\t{index}\t\t{left}\t\t{right}\n")
#             else:
#                 f.write(f"{symbol}\t\t\t\t{index}\t\t{left}\t\t{right}\n")

from model.specs import *
from model.symbol_table import SymbolTable
from model.utils import classify_token, is_integer_fa, is_real_fa, is_identifier_fa
from fa.finite_automaton import FiniteAutomaton

integer_fa = FiniteAutomaton.from_file("fa/files/integer.txt")
real_fa = FiniteAutomaton.from_file("fa/files/real.txt")
identifier_fa = FiniteAutomaton.from_file("fa/files/identifier.txt")

if __name__ == "__main__":
    symbol_table = SymbolTable()
    fip = []

    try:
        with open("code.txt", "r") as file:
            line_num = 0
            for line in file:
                line_num += 1
                i = 0
                stripped_line = line.strip()

                while i < len(line):
                    char = line[i]

                    if line[i].isspace():
                        i += 1
                        continue

                    remaining_sequence = line[i:]
                    prefix = ""

                    if identifier_fa.longest_accepted_prefix(remaining_sequence):
                        prefix = identifier_fa.longest_accepted_prefix(remaining_sequence)

                    elif integer_fa.longest_accepted_prefix(remaining_sequence):
                        prefix = integer_fa.longest_accepted_prefix(remaining_sequence)

                    elif real_fa.longest_accepted_prefix(remaining_sequence):
                        prefix = real_fa.longest_accepted_prefix(remaining_sequence)

                    if prefix:
                        atom_type = classify_token(prefix, keywords, operators, separators)
                        if atom_type != "error":
                            atom_dict[atom_type].add(prefix)
                            if atom_type in ["ID", "CONST"]:
                                symbol_table.insert(prefix)
                            atom_code = atom_codes.get(atom_type, atom_codes.get(prefix, "-"))
                            fip.append(
                                (prefix, atom_code, symbol_table.find(prefix) if atom_type in ["ID", "CONST"] else "-"))
                        else:
                            raise Exception(f"Lexical error at line {line_num}: invalid token '{prefix}'")
                        i += len(prefix)

                    else:
                        if i + 1 < len(line):
                            two_char_op = line[i:i + 2]
                            if two_char_op in operators or two_char_op in separators:
                                atom_type = classify_token(two_char_op, keywords, operators, separators)
                                if atom_type != "error":
                                    atom_dict[atom_type].add(two_char_op)
                                    atom_code = atom_codes.get(two_char_op, "-")
                                    fip.append((two_char_op, atom_code, "-"))
                                    i += 2
                                    continue
                                else:
                                    raise Exception(f"Lexical error at line {line_num}: invalid token '{prefix}'")

                        if char in operators or char in separators:
                            atom_type = classify_token(char, keywords, operators, separators)
                            if atom_type != "error":
                                atom_dict[atom_type].add(char)
                                atom_code = atom_codes.get(char, "-")
                                fip.append((char, atom_code, "-"))
                                i += 1
                                continue
                            else:
                                raise Exception(f"Lexical error at line {line_num}: invalid token '{prefix}'")
                        else:
                            atom_type = classify_token(char, keywords, operators, separators)
                            if atom_type == "error":
                                raise Exception(f"Lexical error at line {line_num}: invalid token '{char}'")

                        i += 1

    except Exception as e:
        print(e)

    with open("results/atoms.txt", "w") as f:
        for category, atoms in atom_dict.items():
            f.write(f"{category}: ")
            for atom in atoms:
                f.write(f"{atom}    ")
            f.write("\n")

    with open("results/fip.txt", "w") as f:
        for name, token, index in fip:
            if 3 < len(name) < 7:
                f.write(f"{name}\t\t\t{token}\t\t{index}\n")
            elif len(name) >= 7:
                f.write(f"{name}\t\t{token}\t\t{index}\n")
            else:
                f.write(f"{name}\t\t\t\t{token}\t\t{index}\n")

    sorted_symbol_table = sorted(symbol_table.to_list(), key=lambda x: x[1])

    with open("results/ts.txt", "w") as f:
        for symbol, index, left, right in sorted_symbol_table:
            if len(symbol) > 3:
                f.write(f"{symbol}\t\t\t{index}\t\t{left}\t\t{right}\n")
            else:
                f.write(f"{symbol}\t\t\t\t{index}\t\t{left}\t\t{right}\n")
