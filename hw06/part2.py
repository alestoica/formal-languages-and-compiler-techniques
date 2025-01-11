import pandas as pd
import re

variable_regex = r"^[a-z_][a-z0-9_]*$"
binary_regex = r"^0b[01]+$"
octal_regex = r"^0[0-7]+$"
hexa_regex = r"^0x[0-9A-Fa-f]+$"

keywords = ["int", "float", "main", "return", "if", "else", "while", "cin", "cout", "endl", "include", "iostream",
            "using", "namespace", "std"]
operators = ["+", "-", "*", "/", "%", "!=", "==", ">", "<", "=", "++", "--", "+=", "-=", "/=", "%=", "&&", "||"]
separators = ["(", ")", "{", "}", ";", ",", "<<", ">>", "<", ">", "#"]

def is_terminal(token):
    if token in keywords:
        return True
    elif token in operators:
        return True
    elif token in separators:
        return True
    elif token == "ID":
        return True
    elif token == "CONST":
        return True
    else:
        return False

def is_variable(token):
    if re.match(variable_regex, token) and token not in keywords and token not in operators and token not in separators:
        return True
    return False

def is_constant(token):
    try:
        float(token)
        return True
    except ValueError:
        if token.startswith('"') and token.endswith('"'):
            return True
        return False

def parse_code(file_name):
    try:
        with open(file_name, "r") as file:
            code = []
            for line in file:
                token = ""
                i = 0
                while i < len(line):
                    char = line[i]

                    if char.isspace() or char in separators or any(line[i:i + 2] in separators for _ in range(2)) or any(line[i:i + 2] in operators for _ in range(2)):
                        if token:
                            if is_constant(token):
                                code.append("CONST")
                            elif is_variable(token):
                                code.append("ID")
                            else:
                                code.append(token)

                        token = ""

                        if char in separators or any(line[i:i + 2] in separators for _ in range(2)) or any(line[i:i + 2] in operators for _ in range(2)):
                            if i + 1 < len(line) and line[i:i + 2] in operators:
                                operator = line[i:i + 2]
                                code.append(operator)
                                i += 1
                            elif i + 1 < len(line) and line[i:i + 2] in separators:
                                separator = line[i:i + 2]
                                code.append(separator)
                                i += 1
                            else:
                                separator = char
                                code.append(separator)

                        i += 1
                    else:
                        token += char
                        i += 1
            return code

    except Exception as e:
        print(e)

class SLRParser:
    def __init__(self, grammar_file, input_sequence):
        self.grammar = []
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
        self.follow_cache = {}
        self.first_cache = {}
        self.parse_table = None
        self.states = []
        self.input_sequence = input_sequence + ['$']  # Append end marker
        self.stack = [0]  # Start with initial state
        self.load_grammar(grammar_file)
        self.augment_grammar()
        self.first_cache = self.first()
        self.follow_cache = self.compute_follow()

    def load_grammar(self, grammar_file):
        """Load grammar from a file."""
        with open(grammar_file, 'r') as file:
            for line in file:
                if ' -> ' in line:
                    lhs, rhs = line.split(' -> ')
                    lhs = lhs.strip()
                    productions = [p.strip('\n') for p in rhs.split(' | ')]
                    for production in productions:
                        if production == 'epsilon':
                            production = ''
                        self.grammar.append((lhs, production))
                        self.non_terminals.add(lhs)
                        production_elements = production.split(' ')
                        for element in production_elements:
                            if is_terminal(element) and element != ".":
                                self.terminals.add(element)
        self.start_symbol = self.grammar[0][0]

        print("Loaded Grammar:", self.grammar)
        print("Terminals:", self.terminals)
        print("Non-Terminals:", self.non_terminals)
        print("Start Symbol:", self.start_symbol)
        print()

    def augment_grammar(self):
        """Augment the grammar with a new start production."""
        augmented_start = self.start_symbol + "'"
        self.grammar.insert(0, (augmented_start, self.start_symbol))
        self.start_symbol = augmented_start
        self.non_terminals.add(augmented_start)

        # Debug print
        print("Augmented Grammar:", self.grammar)
        print()

    def compute_lr0_items(self):
        """Compute LR(0) items and states."""

        def closure(items):
            """Compute closure for a set of items."""
            closure_set = set(items)
            # print("closure set:", closure_set)
            while True:
                new_items = set()
                for lhs, rhs, dot_pos in closure_set:
                    new_rhs = rhs.split(' ')
                    if dot_pos < len(new_rhs) and new_rhs[dot_pos] in self.non_terminals:
                        non_terminal = new_rhs[dot_pos]
                        for prod_lhs, prod_rhs in self.grammar:
                            if prod_lhs == non_terminal:
                                new_items.add((prod_lhs, prod_rhs, 0))
                if not new_items.difference(closure_set):
                    break
                closure_set.update(new_items)
            return closure_set

        def goto(items, symbol):
            """Compute GOTO for a set of items and a symbol."""
            next_items = set()
            for lhs, rhs, dot_pos in items:
                new_rhs = rhs.split(' ')
                if dot_pos < len(new_rhs) and new_rhs[dot_pos] == symbol:
                    next_items.add((lhs, rhs, dot_pos + 1))
            return closure(next_items)

        initial_item = closure([(self.start_symbol, self.grammar[0][1], 0)])
        self.states = [initial_item]
        transitions = {}

        while True:
            new_states = []
            for state in self.states:
                # print("state: ", state)
                for symbol in self.terminals.union(self.non_terminals):
                    next_state = goto(state, symbol)
                    # print("next_state: ", next_state)
                    if next_state and next_state not in self.states:
                        transitions[(self.states.index(state), symbol)] = len(self.states) + len(new_states)
                        new_states.append(next_state)
                    elif next_state:
                        transitions[(self.states.index(state), symbol)] = self.states.index(next_state)
            if not new_states:
                break
            self.states.extend(new_states)

        # Debug print
        print("LR(0) States:")
        for i, state in enumerate(self.states):
            print(f"State {i}: {state}")
        print()
        print("Transitions:", transitions)
        print()

        return transitions

    def construct_parsing_table(self, transitions):
        """Construct the SLR parsing table."""
        symbols = list(self.terminals) + ['$'] + list(self.non_terminals)
        table = pd.DataFrame(index=range(len(self.states)), columns=symbols).fillna('')

        # Compute FOLLOW sets iteratively once
        if not self.follow_cache:
            self.follow_cache = self.compute_follow()

        # Fill in action and goto parts
        for (state, symbol), next_state in transitions.items():
            if symbol in self.terminals or symbol == '$':
                existing_action = table.loc[state, symbol]
                if existing_action:  # If there is already an action
                    table.loc[state, symbol] = f"{existing_action};S{next_state}"  # Add shift action
                else:
                    table.loc[state, symbol] = f"S{next_state}"
            else:
                table.loc[state, symbol] = str(next_state)

        # Fill in reductions
        for i, state in enumerate(self.states):
            for lhs, rhs, dot_pos in state:
                rhs_split = rhs.split(' ') if rhs else ['']
                if dot_pos == len(rhs_split):  # At the end of production
                    if lhs == self.start_symbol and rhs == self.grammar[0][1]:
                        table.loc[i, '$'] = 'ACC'  # Accept
                    else:
                        for terminal in self.follow_cache[lhs]:
                            if rhs == '':
                                action = f"R{self.grammar.index((lhs, ''))}"
                            else:
                                action = f"R{self.grammar.index((lhs, rhs))}"

                            existing_action = table.loc[i, terminal]
                            if existing_action:
                                table.loc[i, terminal] = f"{existing_action};{action}"  # Handle conflicts
                            else:
                                table.loc[i, terminal] = action

        self.parse_table = table

        print("Parsing Table:")
        print(self.parse_table)
        print()

    def compute_follow(self):
        """Compute FOLLOW sets for all non-terminals iteratively."""
        follow_sets = {non_terminal: set() for non_terminal in self.non_terminals}
        follow_sets[self.start_symbol].add('$')  # Add end marker to FOLLOW of start symbol

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.grammar:
                rhs = rhs.split(' ') if rhs else ['']
                for i, symbol in enumerate(rhs):
                    if symbol in self.non_terminals:
                        old_size = len(follow_sets[symbol])
                        if i + 1 < len(rhs):
                            next_symbol = rhs[i + 1]
                            follow_sets[symbol].update(self.first_cache[next_symbol] - {''})
                            if '' in self.first_cache[next_symbol]:
                                follow_sets[symbol].update(follow_sets[lhs])
                        else:
                            follow_sets[symbol].update(follow_sets[lhs])

                        if len(follow_sets[symbol]) > old_size:
                            changed = True

        print("FOLLOW Sets:", follow_sets)
        print()
        return follow_sets

    def first(self):
        """Compute FIRST sets for all symbols iteratively."""
        first_sets = {symbol: set() for symbol in self.terminals}
        for non_terminal in self.non_terminals:
            first_sets[non_terminal] = set()

        for terminal in self.terminals:
            first_sets[terminal].add(terminal)

        # print("FIRST Sets:", first_sets)

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.grammar:
                # print("lhs: ", lhs)
                # print("rhs: ", rhs)
                current_first = first_sets[lhs]
                # print("current_first: ", current_first)
                old_size = len(current_first)
                if rhs == '':
                    current_first.add('')  # Add epsilon
                else:
                    elements = rhs.split(' ')
                    for element in elements:
                        current_first.update(first_sets[element] - {''})
                        if '' not in first_sets[element]:
                            break
                    else:
                        current_first.add('')  # If all elements can derive epsilon

                if len(current_first) > old_size:
                    changed = True

        # Debug print
        print("FIRST Sets:", first_sets)
        print()
        return first_sets

    def check_for_conflicts(self):
        """Check if there are any shift/reduce or reduce/reduce conflicts in the parsing table."""
        for state in range(len(self.parse_table)):
            for symbol in self.parse_table.columns:
                actions = self.parse_table.loc[state, symbol]
                if actions:
                    # If there are multiple actions for a given symbol and state, there is a conflict
                    if ';' in actions:  # Multiple actions separated by a semicolon
                        print(f"Conflict at state {state}, symbol {symbol}: {actions}")
                        return True
        return False

    def parse(self):
        """Parse the input sequence."""
        index = 0
        while True:
            state = self.stack[-1]
            symbol = self.input_sequence[index]

            print(f"State: {state}, Symbol: {symbol}, Stack: {self.stack}")

            if symbol not in self.parse_table.columns:
                print()
                print(f"Error: Symbol '{symbol}' is not in the grammar's set of terminals.")
                return

            action = self.parse_table.loc[state, symbol]
            print(f"Action: {action}")

            if action.startswith('S'):
                self.stack.append(int(action[1:]))
                index += 1
            elif action.startswith('R'):
                production = self.grammar[int(action[1:])]
                lhs, rhs = production
                if rhs == 'epsilon':  # Special case for epsilon
                    # Do not pop any symbols; simply push the LHS
                    print(f"Apply epsilon production: {lhs} -> {rhs}")
                else:
                    new_rhs = rhs.split(' ')
                    for _ in range(len(new_rhs)):
                        self.stack.pop()
                self.stack.append(int(self.parse_table.loc[self.stack[-1], lhs]))
                print(f"Apply production: {lhs} -> {rhs}")
            elif action == 'ACC':
                print()
                print("Input sequence accepted.")
                return
            else:
                print()
                print("Error: Input sequence not accepted.")
                return
            print()

input_sequence = parse_code("code.txt")
print(input_sequence)
parser = SLRParser("minilanguage_grammar.txt", input_sequence)
transitions = parser.compute_lr0_items()
parser.construct_parsing_table(transitions)
if parser.check_for_conflicts():
    print("The SLR parser cannot be applied.")
    print()
else:
    print("No conflicts found. The SLR parser can be applied.")
    print()
    parser.parse()
