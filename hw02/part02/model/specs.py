keywords = ["int", "float", "main", "return", "typedef", "struct", "if", "else", "while", "cin", "cout",
            "endl"]

operators = ["+", "-", "*", "/", "%", "!=", "==", ">", "<", "=", "++", "--", "+=", "-=", "/=", "%="]

separators = ["(", ")", "{", "}", ";", ",", "<<", ">>"]

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
    "==": 33
}
