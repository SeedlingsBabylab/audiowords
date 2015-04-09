import re
from collections import deque

class ClanFileParser:

    def __init__(self, input_path, output_path):
        self.clan_file = input_path
        self.export_clan_file = output_path

        self.silences_inserted = False
        self.overlaps_inserted = False




    def insert_silences(self, silences):

        # we initialize a queue of silences using the
        # list passed as argument to this function. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        silence_queue = deque(silences)

        # open the export clan file
        output = open(self.export_clan_file, "w")


        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\d+_\d+)")

            # pop the first silence off the queue
            curr_silence = silence_queue.popleft()

            #initialize the start/end written flags
            start_written = False
            end_written = False

            # We iterate over the clan file line by line
            for raw_line in file:
                # get rid of preceding and trailing whitespace from the line
                line = raw_line.strip()


                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and curr_silence:
                    # parse out the part of the line with the interval in it
                    interval_string = interval_regx.search(line).group()
                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    if current_clan_interval[1] < current_clan_interval[0]:
                        raise Exception("timestamp interval is malformed: {}_{}".format(interval[0],
                                                                                        interval[1]))

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if curr_silence.start <= current_clan_interval[1]\
                            and not start_written:

                        # alter the ending timestamp to correspond to the beginning
                        # of the silence, and write the new line to the output file
                        output.write(line.replace(interval_string,
                                                  str(current_clan_interval[0]) + "_" +\
                                                  str(int(curr_silence.start))) + "\n")

                        # insert the comment immediately after the altered clan entry
                        output.write("%com:  silence {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.start,
                                             current_clan_interval[1]))

                        start_written = True
                        end_written = False

                        # stop progressing though the conditions and
                        # head to next line in the file
                        continue

                    # If the end of the currently queued silence is less than
                    # the end of the current clan time interval...
                    if curr_silence.end <= current_clan_interval[1]\
                            and start_written\
                            and not end_written:

                        # We first alter the clan time interval to match the end of the
                        # silence we are about to insert, and write it to the output file
                        output.write(line.replace(interval_string,
                                                  str(current_clan_interval[0]) + "_" +\
                                                  str(int(curr_silence.end))) + "\n")

                        # then we write the end silence comment right afterwards
                        output.write("%com:  silence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))

                        end_written = True
                        start_written = False

                        # make sure queue contains items
                        # and pop the next silence off of it
                        if silence_queue:
                            curr_silence = silence_queue.popleft()
                        else:
                            # if silence_queue is empty, we set curr_silence to None
                            # so that the top level check fails
                            # (if line.startswith("*") and curr_silence:)
                            # this ensures that after all the silences have been handled,
                            # we just write all subsequent lines to output without any
                            # further processing
                            curr_silence = None
                        continue

                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written:

                    output.write("%com:  silence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))
                    output.write(line)

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line + "\n")

        output.close()


    def insert_overlaps(self, region_values, region_map, silences):

        region_number = 1

        # open the export clan file
        output = open(self.export_clan_file, "w")


        offset_list = region_values # this is a list of interval offsets



        # for index, x in enumerate(region_values):
        #     for key, value in region_map.items():
        #         if value == x:
        #             offset_list.append(key)
        sorted_offsets = sorted(offset_list)

        # we initialize a queue of regions using the
        # list built from the region_map lookup. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        # We also build a queue for the silence regions
        region_queue = deque(sorted_offsets)
        silence_queue = deque(silences)

        print
        print
        print
        print
        print
        print
        print
        print
        print
        print
        print
        print
        print

        print "region values: " + str(region_values)
        print "sorted_offsets: " + str(sorted_offsets)
        print "region queue: " + str(region_queue)


        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\d+_\d+)")

            # pop the first silence and region off the queue
            curr_region = region_queue.popleft()
            curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
            curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
            curr_silence = silence_queue.popleft()

            print "curr_region: " + str(curr_region)
            print "curr_region_start: " + str(curr_region_start)
            print "curr_region_end: " + str(curr_region_end)

            # initialize the start/end written flags
            start_written = False
            end_written = False

            # initialize the silence/subregion overlap flags
            region_start_in_silence = False
            region_end_in_silence = False

            # We iterate over the clan file line by line
            for raw_line in file:
                # get rid of preceding and trailing whitespace from the line
                line = raw_line.strip()


                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and (curr_region is not None):
                    # parse out the part of the line with the interval in it
                    interval_string = interval_regx.search(line).group()
                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    #print "clan[0]: " + str(current_clan_interval[0]) + "clan[1]: " + str(current_clan_interval[1]) + "    curr_region_start: " + str(curr_region_start)


                    # Handle special case for 0 offset
                    if curr_region_start == 0:
                        curr_region_start = 1 # avoid 0 millisecond. start at 1 millisecond.
                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    if current_clan_interval[1] < current_clan_interval[0]:
                        raise Exception("timestamp interval is malformed: {}_{}".format(interval[0],
                                                                                        interval[1]))
                    if (curr_region_start > curr_silence.start) and\
                            (curr_region_start < curr_silence.end):
                        region_start_in_silence = True

                    if (curr_region_end < curr_silence.end) and\
                            (curr_region_end > curr_silence.start):
                        region_end_in_silence = True

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if curr_region_start <= current_clan_interval[1]\
                            and not start_written:
                        if region_start_in_silence or region_end_in_silence:

                            # alter the ending timestamp to correspond to the beginning
                            # of the silence, and write the new line to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" + \
                                                      str(int(curr_region_start))) + "\n")

                            # insert the comment immediately after the altered clan entry
                            output.write("%com:  subregion {} of {} starts at {} -- previous timestamp adjusted: was {} [inside silent region: [{}, {}] ]\n"\
                                         .format(region_number,
                                                 len(region_values),
                                                 curr_region_start,
                                                 current_clan_interval[1],
                                                 curr_silence.start,
                                                 curr_silence.end))

                            start_written = True
                            end_written = False

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue
                        else:
                            # alter the ending timestamp to correspond to the beginning
                            # of the silence, and write the new line to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" +\
                                                      str(int(curr_region_start))) + "\n")

                            # insert the comment immediately after the altered clan entry
                            output.write("%com:  subregion {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                         .format(region_number,
                                                 len(region_values),
                                                 curr_region_start,
                                                 current_clan_interval[1]))

                            start_written = True
                            end_written = False

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue

                    # If the end of the currently queued subregion is less than
                    # the end of the current clan time interval...
                    if curr_region_end <= current_clan_interval[1]\
                            and start_written\
                            and not end_written:
                        if region_start_in_silence or region_end_in_silence:
                            # We first alter the clan time interval to match the end of the
                            # subregion we are about to insert, and write it to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" + \
                                                      str(int(curr_region_end))) + "\n")

                            # then we write the end subregion comment right afterwards
                            output.write("%com:  subregion {} of {} ends at {} -- previous timestamp adjusted: was {} [inside silent region: [{}, {}] ]\n"
                                         .format(region_number,
                                                 len(region_values),
                                                 curr_region_end,
                                                 current_clan_interval[1],
                                                 curr_silence.start,
                                                 curr_silence.end))

                            end_written = True
                            start_written = False



                            # make sure queue contains items
                            # and pop the next silence off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                print "curr_region: " + str(curr_region)
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                print "curr_region_start: " + str(curr_region_start)
                                print "curr_region_end: " + str(curr_region_end)
                                region_number = region_number + 1
                            else:
                                # if region_queue is empty, we set curr_region to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the subregions have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue
                        else:
                            # We first alter the clan time interval to match the end of the
                            # silence we are about to insert, and write it to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" +\
                                                      str(int(curr_region_end))) + "\n")

                            # then we write the end subbregion comment right afterwards
                            output.write("%com:  subregion {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                         .format(region_number,
                                                 len(region_values),
                                                 curr_region_end,
                                                 current_clan_interval[1]))

                            end_written = True
                            start_written = False



                            # make sure queue contains items
                            # and pop the next subregion off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                region_number = region_number + 1
                            else:
                                # if silence_queue is empty, we set curr_silence to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the silences have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue

                if current_clan_interval[1] >= curr_silence.end:
                    curr_silence = silence_queue.popleft()
                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written:

                    output.write("%com:  subregion {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(region_number,
                                             len(region_values),
                                             curr_region_end,
                                             current_clan_interval[1]))
                    output.write(line)
                    region_number = region_number + 1

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line + "\n")

        output.close()

