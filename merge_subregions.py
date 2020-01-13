import argparse, sys, difflib

# Color output for the terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Function to take care of parsing arguments.
def get_args():
    parser = argparse.ArgumentParser(description='Merge subregions from first cha file to the second')
    parser.add_argument('sub_file', help='the input cha file that contains the correct subregions')
    parser.add_argument('input_file', help='the cha file that will have its subregions updated')
    parser.add_argument('--output_file', help='the optional output file to which the merged result will be outputted.')
    return parser.parse_args()

# Quick function to check for correct subregion line (subregion starts or ends)
def check_sub_line(line):
    return 'subregion' in line and ('starts' in line or 'ends' in line)

# Pretty print the options list
def pretty_print(l):
    for i, val in enumerate(l):
        print '{} ===== {}'.format(i, val)


# Function to get user input (an integer) from a range of choices between 0 and m (not included)
def get_user_input(m):
    cond = True
    while cond:
        inp = raw_input('---> ')
        try:
            choice = int(inp)
            if choice < 0 or choice >= m:
                print('Please pick a number within the range!!')
                continue
            cond = False

        except ValueError:
            print('That is not an integer, please choose again!')
    return choice



if __name__ == '__main__':

    # Get parsed arguments.
    args = get_args()
    print 'Arguments that the script has received:'
    print vars(args)

    with open(args.sub_file) as f1:
        sublines = f1.readlines()

    with open(args.input_file) as f2:
        mergelines = f2.readlines()

    for line in sublines:
        if check_sub_line(line):
            print line

            similars = difflib.get_close_matches(line, mergelines)
            print 'Please select from the option below the subregion comment you wish to replace'
            pretty_print(similars)
            choice = get_user_input(len(similars))
            print choice
            







