import argparse

def process_input_file(input_file):
    print(f"Processing input file: {[input_file]}")

def process_output_file(output_file):
    print(f"Using output file: {[output_file]}")

def main():
    parser = argparse.ArgumentParser(description='Sample CLI Program')
    parser.add_argument('--input-file', '-i', '-ooo', type=str, required=True, help='Path to the input file')
    parser.add_argument('--output-file', type=str, default='output.txt', help='Path to the output file (default: output.txt)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--count', action='count', help='Count the number of occurrences')
    parser.add_argument('--flag', action='store_const', const=42, help='Store a constant value')
    parser.add_argument('--choices', type=str, choices=['option1', 'option2'], help='Choose from predefined options')
    parser.add_argument('--custom', type=int, help='Use a custom type converter')

    args = parser.parse_args()

    # Process input file
    process_input_file(args.input_file)

    # Process output file
    process_output_file(args.output_file)

    # Enable verbose mode
    if args.verbose:
        print("Verbose mode is enabled.")

    # Count the number of occurrences
    if args.count:
        print(f"Count is {args.count}")

    # Print the value of the constant flag
    if args.flag:
        print(f"Flag is set to {[args.flag]}")

    # Process choices
    if args.choices:
        print(f"Chosen option: {[args.choices]}")

    # Process custom argument
    if args.custom:
        print(f"Custom argument: {[args.custom]}")

if __name__ == '__main__':
    main()
