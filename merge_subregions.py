import argparse, sys, difflib

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



