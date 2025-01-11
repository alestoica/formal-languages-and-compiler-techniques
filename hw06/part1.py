import pandas as pd

class SLRParser:
    def __init__(self, grammar_file, input_sequence):
        self.grammar = []
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None

        self.follow_cache = {}
        self.first_cache = {}

        self.input_sequence = input_sequence + '$'
        self.parse_table = None
        self.states = []
        self.stack = [0]

        self.load_grammar(grammar_file)
        self.augment_grammar()
        self.first_cache = self.first()
        self.follow_cache = self.compute_follow()

    def load_grammar(self, grammar_file):
        with open(grammar_file, 'r') as file:
            for line in file:
                if '->' in line:
                    lhs, rhs = line.strip().split('->')
                    lhs = lhs.strip()
                    productions = [p.strip() for p in rhs.split('|')]
                    for production in productions:
                        self.grammar.append((lhs, production))
                        self.non_terminals.add(lhs)
                        for symbol in production:
                            if not symbol.isupper() and symbol != ".":
                                self.terminals.add(symbol)
        self.start_symbol = self.grammar[0][0]

        print("Loaded Grammar:", self.grammar)
        print("Terminals:", self.terminals)
        print("Non-Terminals:", self.non_terminals)
        print("Start Symbol:", self.start_symbol)
        print()

    def augment_grammar(self):
        augmented_start = self.start_symbol + "'"
        self.grammar.insert(0, (augmented_start, self.start_symbol))
        self.start_symbol = augmented_start
        self.non_terminals.add(augmented_start)

        # Debug print
        print("Augmented Grammar:", self.grammar)
        print()

    def compute_lr0_items(self):
        def closure(items):
            closure_set = set(items)
            while True:
                new_items = set()
                for lhs, rhs, dot_pos in closure_set:
                    if dot_pos < len(rhs) and rhs[dot_pos] in self.non_terminals:
                        non_terminal = rhs[dot_pos]
                        for prod_lhs, prod_rhs in self.grammar:
                            if prod_lhs == non_terminal:
                                new_items.add((prod_lhs, prod_rhs, 0))
                if not new_items.difference(closure_set):
                    break
                closure_set.update(new_items)
            return closure_set

        def goto(items, symbol):
            next_items = set()
            for lhs, rhs, dot_pos in items:
                if dot_pos < len(rhs) and rhs[dot_pos] == symbol:
                    next_items.add((lhs, rhs, dot_pos + 1))
            return closure(next_items)

        initial_item = closure([(self.start_symbol, self.grammar[0][1], 0)])
        self.states = [initial_item]
        transitions = {}

        while True:
            new_states = []
            for state in self.states:
                for symbol in self.terminals.union(self.non_terminals):
                    next_state = goto(state, symbol)
                    if next_state and next_state not in self.states:
                        transitions[(self.states.index(state), symbol)] = len(self.states) + len(new_states)
                        new_states.append(next_state)
                    elif next_state:
                        transitions[(self.states.index(state), symbol)] = self.states.index(next_state)
            if not new_states:
                break
            self.states.extend(new_states)

        print("LR(0) States:")
        for i, state in enumerate(self.states):
            print(f"State {i}: {state}")
        print()
        print("Transitions:", transitions)
        print()

        return transitions

    def construct_parsing_table(self, transitions):
        symbols = list(self.terminals) + ['$'] + list(self.non_terminals)
        table = pd.DataFrame(index=range(len(self.states)), columns=symbols).fillna('')

        if not self.follow_cache:
            self.follow_cache = self.compute_follow()

        # Fill in action and goto parts
        for (state, symbol), next_state in transitions.items():
            if symbol in self.terminals or symbol == '$':
                existing_action = table.loc[state, symbol]
                if existing_action:
                    table.loc[state, symbol] = f"{existing_action};S{next_state}"
                else:
                    table.loc[state, symbol] = f"S{next_state}"
            else:
                table.loc[state, symbol] = str(next_state)

        # Fill in reductions
        for i, state in enumerate(self.states):
            for lhs, rhs, dot_pos in state:
                if dot_pos == len(rhs):
                    if lhs == self.start_symbol and rhs == self.grammar[0][1]:
                        table.loc[i, '$'] = 'ACC'
                    else:
                        for terminal in self.follow_cache[lhs]:
                            existing_action = table.loc[i, terminal]
                            if existing_action:
                                table.loc[
                                    i, terminal] = f"{existing_action};R{self.grammar.index((lhs, rhs))}"
                            else:
                                table.loc[i, terminal] = f"R{self.grammar.index((lhs, rhs))}"

        self.parse_table = table

        print("Parsing Table:")
        print(self.parse_table)
        print()

    def compute_follow(self):
        follow_sets = {non_terminal: set() for non_terminal in self.non_terminals}
        follow_sets[self.start_symbol].add('$')

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.grammar:
                for i, symbol in enumerate(rhs):
                    if symbol in self.non_terminals:
                        if i + 1 < len(rhs):
                            next_symbol = rhs[i + 1]
                            old_size = len(follow_sets[symbol])
                            follow_sets[symbol].update(self.first_cache[next_symbol] - {''})
                            if len(follow_sets[symbol]) > old_size:
                                changed = True
                        if i + 1 == len(rhs) or '' in self.first_cache.get(rhs[i + 1], set()):
                            old_size = len(follow_sets[symbol])
                            follow_sets[symbol].update(follow_sets[lhs])
                            if len(follow_sets[symbol]) > old_size:
                                changed = True

        print("FOLLOW Sets:", follow_sets)
        print()
        return follow_sets

    def first(self):
        first_sets = {symbol: set() for symbol in self.terminals}
        for non_terminal in self.non_terminals:
            first_sets[non_terminal] = set()

        for terminal in self.terminals:
            first_sets[terminal].add(terminal)

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.grammar:
                current_first = first_sets[lhs]
                old_size = len(current_first)

                if rhs == '':
                    current_first.add('')
                else:
                    for symbol in rhs:
                        current_first.update(first_sets[symbol] - {''})
                        if '' not in first_sets[symbol]:
                            break
                    else:
                        current_first.add('')

                if len(current_first) > old_size:
                    changed = True

        print("FIRST Sets:", first_sets)
        print()
        return first_sets

    def check_for_conflicts(self):
        for state in range(len(self.parse_table)):
            for symbol in self.parse_table.columns:
                actions = self.parse_table.loc[state, symbol]
                if actions:
                    # If there are multiple actions for a given symbol and state, there is a conflict
                    if ';' in actions:
                        print(f"Conflict at state {state}, symbol {symbol}: {actions}")
                        return True
        return False

    def parse(self):
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
                if rhs != '':
                    for _ in range(len(rhs)):
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

parser = SLRParser("grammar.txt", "bipip")
transitions = parser.compute_lr0_items()
parser.construct_parsing_table(transitions)
if parser.check_for_conflicts():
    print("The SLR parser cannot be applied.")
    print()
else:
    print("No conflicts found. The SLR parser can be applied.")
    print()
    parser.parse()
