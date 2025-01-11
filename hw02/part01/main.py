from finite_automaton import FiniteAutomaton


def print_read_commands():
    print("   0 - Exit")
    print("   1 - Read from file")
    print("   2 - Read from cmd\n")


def print_commands():
    print("Options:")
    print("   0 - Exit")
    print("   1 - States")
    print("   2 - Alphabet")
    print("   3 - Transitions")
    print("   4 - Final states")
    print("   5 - Check if sequence is accepted")
    print("   6 - Find longest accepted prefix")


if __name__ == "__main__":
    # filename = "r_constants.txt"
    # filename = "z_constants.txt"
    # filename = "in_class_1.txt"
    filename = "in_class_2.txt"
    print_read_commands()
    command = int(input("Enter your choice: "))
    if command == 0:
        exit(0)
    elif command == 1:
        finite_automaton = FiniteAutomaton.from_file(filename)
    elif command == 2:
        finite_automaton = FiniteAutomaton.from_input()
    else:
        print("Invalid command!")
        exit(0)

    while True:
        print_commands()
        command = int(input("Enter your choice: "))
        if command == 0:
            exit(0)
        elif command == 1:
            print("States: " + ", ".join(finite_automaton.get_states()))
        elif command == 2:
            print("Alphabet: " + ", ".join(finite_automaton.get_alphabet()))
        elif command == 3:
            print("Transitions: " + ", ".join(t.to_string() for t in finite_automaton.get_transitions()))
        elif command == 4:
            print("Final states: " + ", ".join(finite_automaton.get_final_states()))
        elif command == 5:
            if not finite_automaton.is_deterministic():
                print("The finite automaton is not deterministic. Cannot check if the sequence is accepted.")
            else:
                sequence = input("Enter the sequence: ")
                if finite_automaton.is_sequence_accepted(sequence):
                    print("Accepted sequence!")
                else:
                    print("Invalid sequence!")
        elif command == 6:
            if not finite_automaton.is_deterministic():
                print("The finite automaton is not deterministic. Cannot find the longest accepted prefix.")
            else:
                sequence = input("Enter the sequence: ")
                prefix = finite_automaton.longest_accepted_prefix(sequence)
        else:
            print("Invalid command!")
            exit(0)
        print("\n")
