import argparse, sys, difflib, heapq

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

def get_match_and_indices(word, possibilities, n=3, cutoff=0.6):
    if not n >  0:
        raise ValueError("n must be > 0: %r" % (n,))
    if not 0.0 <= cutoff <= 1.0:
        raise ValueError("cutoff must be in [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = difflib.SequenceMatcher()
    s.set_seq2(word)
    for i, x in enumerate(possibilities):
        s.set_seq1(x)
        if s.real_quick_ratio() >= cutoff and \
           s.quick_ratio() >= cutoff and \
           s.ratio() >= cutoff:
            result.append((s.ratio(), x, i))

    # Move the best scorers to head of list
    result = heapq.nlargest(n, result)
    # Strip scores for the best n matches
    return [(x, i) for score, x, i in result]

def write_output(lines, filename='temp.txt'):
    with open(filename, 'w') as outf:
        outf.writelines(lines)



if __name__ == '__main__':

    # Get parsed arguments.
    args = get_args()
    print 'Arguments that the script has received:'
    print vars(args)
    print

    with open(args.sub_file) as f1:
        sublines = f1.readlines()

    with open(args.input_file) as f2:
        mergelines = f2.readlines()
        # we make a copy of the mergelines (the lines from the file that we are replacing the comments with)
        # to prevent the possibility of any nasty side effects.
        resultlines = mergelines[:]

    # Iterate through the lines of the newly created ranked subregion file.
    for line in sublines:
        if check_sub_line(line):
            print 'the replacement line:\n{}\n'.format(line)
            similars = get_match_and_indices(line, mergelines, cutoff=0.8)

            # If the similars list is empty, which means that it couldn't find a close match, abort, and manually check!
            # IMPORTANT: This part will be modified to handle complications for files that don't have 5 subregions:
            # an insert anyway option will try to find the appropriate place to insert the line!
            if not similars:
                sys.exit()

                
            print 'Please select from the option below the subregion comment you wish to replace with the replacement line above'
            pretty_print(similars)
            choice = get_user_input(len(similars))
            print
            replacement_line, index = similars[choice]

            #garble the line so that it won't be matched for anything else the next round!
            mergelines[index] = '========================================'

            # actually replacing the line with the ranked line.
            resultlines[index] = line

    write_output(resultlines)

