import re

variable_regex = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
binary_regex = r"^0b[01]+$"
octal_regex = r"^0[0-7]+$"
hexa_regex = r"^0x[0-9A-Fa-f]+$"


class Node:
    def __init__(self, value, index):
        self.value = value
        self.index = index
        self.left = None
        self.right = None


class SymbolTable:
    def __init__(self):
        self.root = None
        self.current_index = 1
        self.symbols = {}

    def insert(self, value):
        if self.root is None:
            self.root = Node(value, self.current_index)
            self.symbols[value] = self.root
            self.current_index += 1
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value, self.current_index)
                self.symbols[value] = node.left
                self.current_index += 1
            else:
                self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = Node(value, self.current_index)
                self.symbols[value] = node.right
                self.current_index += 1
            else:
                self._insert_recursive(node.right, value)

    def find(self, value):
        return self._find_recursive(self.root, value)

    def _find_recursive(self, node, value):
        if node is None:
            return None
        if node.value == value:
            return node.index
        elif value < node.value:
            return self._find_recursive(node.left, value)
        else:
            return self._find_recursive(node.right, value)

    def to_list(self):
        result = []
        self._in_order_traversal(self.root, result)
        return sorted(result, key=lambda x: x[0])

    def _in_order_traversal(self, node, result):
        if node is not None:
            self._in_order_traversal(node.left, result)
            result.append((node.value, node.index,
                           node.left.index if node.left else "-1",
                           node.right.index if node.right else "-1"))
            self._in_order_traversal(node.right, result)


def classify_token(token, keywords, operators, separators):
    if token in keywords:
        return "keywords"
    elif token in operators:
        return "operators"
    elif token in separators:
        return "separators"
    elif is_constant(token) or re.match(binary_regex, token) or re.match(octal_regex, token) or re.match(hexa_regex,
                                                                                                         token):
        return "CONST"
    elif re.match(variable_regex, token):
        return "ID"
    else:
        return "error"


def is_constant(token):
    try:
        float(token)
        return True
    except ValueError:
        if token.startswith('"') and token.endswith('"'):
            return True
        return False


def main():
    keywords = ["int", "float", "main", "return", "typedef", "struct", "if", "else", "while", "cin", "cout",
                "endl", "include", "iostream", "using", "namespace", "std"]
    operators = ["+", "-", "*", "/", "%", "!=", "==", ">", "<", "=", "++", "--", "+=", "-=", "/=", "%="]
    separators = ["(", ")", "{", "}", ";", ",", "<<", ">>", "<", ">", "#"]

    atom_dict = {
        "keywords": set(),
        "operators": set(),
        "separators": set(),
        "ID": set(),
        "CONST": set()
    }

    atom_codes = {
        "ID": 0,
        "CONST": 1,
        "main": 2,
        "int": 3,
        "float": 4,
        "typedef": 5,
        "struct": 6,
        "(": 7,
        ")": 8,
        "{": 9,
        "}": 10,
        "return": 11,
        ",": 12,
        ";": 13,
        "=": 14,
        "++": 15,
        "--": 16,
        "+": 17,
        "-": 18,
        "*": 19,
        "/": 20,
        "%": 21,
        "if": 22,
        "else": 23,
        "cin": 24,
        "cout": 25,
        "endl": 26,
        ">>": 27,
        "<<": 28,
        "while": 29,
        ">": 30,
        "<": 31,
        "!=": 32,
        "==": 33,
        "#": 34,
        "include": 35,
        "iostream": 36,
        "using": 37,
        "namespace": 38,
        "std": 39
    }

    symbol_table = SymbolTable()
    fip = []

    try:
        with open("code.txt", "r") as file:
            line_num = 0
            for line in file:
                line_num += 1
                token = ""
                i = 0
                while i < len(line):
                    char = line[i]

                    if char.isspace() or char in separators or any(line[i:i + 2] in separators for _ in range(2)) or any(line[i:i + 2] in operators for _ in range(2)):
                        if token:
                            atom_type = classify_token(token, keywords, operators, separators)
                            if atom_type != "error":
                                atom_dict[atom_type].add(token)
                                if atom_type in ["ID", "CONST"]:
                                    symbol_table.insert(token)
                                atom_code = atom_codes.get(atom_type, atom_codes.get(token, "-"))
                                fip.append(
                                    (token, atom_code,
                                     symbol_table.find(token) if atom_type in ["ID", "CONST"] else "-"))
                            else:
                                raise Exception(f"Lexical error at line {line_num}: invalid token '{token}'")

                        token = ""

                        if char in separators or any(line[i:i + 2] in separators for _ in range(2)) or any(line[i:i + 2] in operators for _ in range(2)):
                            if i + 1 < len(line) and line[i:i + 2] in operators:
                                operator = line[i:i + 2]
                                atom_dict["operators"].add(operator)
                                atom_code = atom_codes.get(operator, "-")
                                fip.append((operator, atom_code, "-"))
                                i += 1
                            elif i + 1 < len(line) and line[i:i + 2] in separators:
                                operator = line[i:i + 2]
                                atom_dict["separators"].add(operator)
                                atom_code = atom_codes.get(operator, "-")
                                fip.append((operator, atom_code, "-"))
                                i += 1
                            else:
                                separator = char
                                atom_dict[classify_token(separator, keywords, operators, separators)].add(separator)
                                atom_code = atom_codes.get(separator, "-")
                                fip.append((separator, atom_code, "-"))

                        i += 1
                    else:
                        token += char
                        i += 1

    except Exception as e:
        print(e)

    with open("atoms.txt", "w") as f:
        for category, atoms in atom_dict.items():
            f.write(f"{category}: ")
            for atom in atoms:
                f.write(f"{atom}    ")
            f.write("\n")

    with open("fip.txt", "w") as f:
        for name, token, index in fip:
            if 3 < len(name) < 7:
                f.write(f"{name}\t\t\t{token}\t\t{index}\n")
            elif len(name) >= 7:
                f.write(f"{name}\t\t{token}\t\t{index}\n")
            else:
                f.write(f"{name}\t\t\t\t{token}\t\t{index}\n")

    sorted_symbol_table = sorted(symbol_table.to_list(), key=lambda x: x[1])

    with open("ts.txt", "w") as f:
        for symbol, index, left, right in sorted_symbol_table:
            if len(symbol) > 3:
                f.write(f"{symbol}\t\t\t{index}\t\t{left}\t\t{right}\n")
            else:
                f.write(f"{symbol}\t\t\t\t{index}\t\t{left}\t\t{right}\n")


if __name__ == "__main__":
    main()
