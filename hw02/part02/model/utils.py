from fa.finite_automaton import FiniteAutomaton


def classify_token(token, keywords, operators, separators):
    if token in keywords:
        return "keywords"

    elif token in operators:
        return "operators"

    elif token in separators:
        return "separators"

    elif is_integer_fa(token) or is_real_fa(token):
        return "CONST"

    elif is_identifier_fa(token):
        return "ID"

    else:
        return "error"


def is_integer_fa(token):
    finite_automaton = FiniteAutomaton.from_file("fa/files/integer.txt")
    return finite_automaton.is_sequence_accepted(token)


def is_real_fa(token):
    finite_automaton = FiniteAutomaton.from_file("fa/files/real.txt")
    return finite_automaton.is_sequence_accepted(token)


def is_identifier_fa(token):
    finite_automaton = FiniteAutomaton.from_file("fa/files/identifier.txt")
    return finite_automaton.is_sequence_accepted(token)
