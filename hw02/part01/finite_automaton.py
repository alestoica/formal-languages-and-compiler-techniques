from transition import Transition


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.final_states = final_states
        self.initial_state = states[0]  # Assuming the first state is the initial state

    def get_states(self):
        return self.states

    def get_alphabet(self):
        return self.alphabet

    def get_transitions(self):
        return self.transitions

    def get_final_states(self):
        return self.final_states

    def get_initial_state(self):
        return self.initial_state

    def is_deterministic(self):
        transition_map = {}

        for transition in self.transitions:
            key = (transition.get_source_state(), transition.get_value())

            if key in transition_map:
                return False

            transition_map[key] = transition.get_destination_state()

        return True

    def is_sequence_accepted(self, sequence):
        current_state = self.initial_state

        while sequence:
            found = False
            for transition in self.transitions:
                if transition.get_source_state() == current_state and \
                        transition.get_value() == sequence[: len(transition.get_value())]:
                    sequence = sequence[len(transition.get_value()):]
                    current_state = transition.get_destination_state()
                    found = True
                    break

            if not found:
                return False

        return current_state in self.final_states

    def longest_accepted_prefix(self, sequence):
        prefix = ""
        current_state = self.initial_state
        is_epsilon_accepted = current_state in self.final_states

        if self.is_sequence_accepted(sequence):
            print("Longest accepted prefix: " + sequence)
            return

        while (len(sequence) - 1) > 0:
            found = False

            for transition in self.transitions:
                if (
                        transition.get_source_state() == current_state
                        and transition.get_value() == sequence[: len(transition.get_value())]
                ):
                    prefix += transition.get_value()
                    sequence = sequence[len(transition.get_value()):]
                    current_state = transition.get_destination_state()
                    found = True
                    break

            if not found:
                break

        if prefix == "":
            if is_epsilon_accepted:
                print("Epsilon (empty string) is accepted.")
            else:
                print("No accepted prefix found.")
        else:
            if current_state in self.final_states:
                print("Longest accepted prefix: " + prefix)
            else:
                if is_epsilon_accepted:
                    print("Epsilon (empty string) is accepted.")
                else:
                    print("No accepted prefix found.")

        return prefix

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        states = lines[0].strip().split(": ")[1].split(",")
        alphabet = lines[1].strip().split(": ")[1].split(",")
        transitions = []
        final_states = []

        reading_transitions = False
        for line in lines[2:]:
            if line.startswith("Transitions:"):
                reading_transitions = True
                continue
            if line.startswith("Final States:"):
                final_states = line.strip().split(": ")[1].split(",")
                break
            if reading_transitions:
                line_transitions = line.strip().split(", ")
                for tr in line_transitions:
                    src, symbol, dest = tr.split("->")
                    transitions.append(Transition(src.strip(), dest.strip(), symbol.strip()))

        return FiniteAutomaton(states, alphabet, transitions, final_states)

    @staticmethod
    def from_input():
        states = input("Enter states (comma separated): ").split(",")
        alphabet = input("Enter alphabet (comma separated): ").split(",")
        transitions = []
        print("Enter transitions (state -> symbol -> state, one per line). Type 'done' when finished:")

        while True:
            tr = input().strip()
            if tr.lower() == "done":
                break
            if tr:
                src, symbol, dest = tr.split("->")
                transitions.append(Transition(src.strip(), dest.strip(), symbol.strip()))

        final_states = input("Enter final states (comma separated): ").split(",")

        return FiniteAutomaton(states, alphabet, transitions, final_states)
