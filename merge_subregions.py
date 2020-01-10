import argparse

# Function to take care of parsing arguments.
def get_args():
    parser = argparse.ArgumentParser(description='Merge subregions from first cha file to the second')
    parser.add_argument('sub_file', help='the input cha file that contains the correct subregions')
    parser.add_argument('input_file', help='the cha file that will have its subregions updated')
    parser.add_argument('--output_file', help='the optional output file to which the merged result will be outputted.')
    return parser.parse_args()



if __name__ == '__main__':

    # Get parsed arguments.
    args = get_args()

    print vars(args)







