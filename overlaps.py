import csv

import audiowords

class Overlaps:

    def __init__(self, lena_file, top_n):
        self.dataset = None
        self.top_n = top_n

        self.meaningful_regions = None
        self.awc_actual_regions = None
        self.ctc_actual_regions = None
        self.cvc_actual_regions = None

        self.meaningful_map = None
        self.awc_actual_map = None
        self.ctc_actual_map = None
        self.cvc_actual_map = None

        self.ranked_meaningful = None
        self.ranked_awc_actual = None
        self.ranked_ctc_actual = None
        self.ranked_cvc_actual = None

        self.load_data(lena_file)

    def load_data(self, file):

        visit_date = None
        with open(file, "rU") as file:
            reader = csv.reader(file)
            reader.next() # skip past the header row
            for line in reader:
                timestamp_split = line[10].split()
                date = timestamp_split[0].split("-")
                time = timestamp_split[1].split(":")

                if visit_date is None:
                    visit_date = (date[0], date[1], date[2])
                elif visit_date != (date[0], date[1], date[2]):
                    print "Your file contains multiple different visits within the same file"

                # we represent date/time as a 5d tuple
                # i.e. 02-13-2015 3:35 = (2, 13, 2015, 3, 35)

                # first line of iteration, dataset not instantiated yet
                if self.dataset is None:
                    # instantiate
                    self.dataset = WordDensitySet((date[0],
                                                   date[1],
                                                   date[2],
                                                   time[0],
                                                   time[1]))

                    # add first region magnitude value.
                    # meaningful is represented in seconds.
                    duration_split = line[11].split(":")
                    meaningful_split = line[12].split(":")

                    duration = int(duration_split[0]) * 3600 +\
                               int(duration_split[1]) * 60 +\
                               int(duration_split[2])

                    # meaningful is redefined as ratio between "meaningful" and duration
                    meaningful = float((int(meaningful_split[0]) * 3600 +
                                 int(meaningful_split[1]) * 60 +
                                 int(meaningful_split[2]))) / duration

                    awc_actual = int(line[18])
                    ctc_actual = int(line[21])
                    cvc_actual = int(line[24])

                    self.dataset.data.append((meaningful, awc_actual, ctc_actual, cvc_actual))

                else:
                    # just add to the end of the current dataset

                    duration_split = line[11].split(":")
                    meaningful_split = line[12].split(":")

                    duration = int(duration_split[0]) * 3600 +\
                               int(duration_split[1]) * 60 +\
                               int(duration_split[2])

                    meaningful = float((int(meaningful_split[0]) * 3600 +
                                 int(meaningful_split[1]) * 60 +
                                 int(meaningful_split[2]))) / duration

                    awc_actual = int(line[18])
                    ctc_actual = int(line[21])
                    cvc_actual = int(line[24])

                    print "meaningful: " + str(meaningful) + " awc: " + str(awc_actual) +  " cvc: " + str(ctc_actual) + "    cvc: " + str(cvc_actual)

                    self.dataset.data.append((meaningful, awc_actual, ctc_actual, cvc_actual))


                    #self.dataset.hours()


                print
                print "timestamp: " + line[10]

            print
            print
            print self.dataset
            #self.dataset.hours()
            print "size of dataset:  " + str(len(self.dataset.data))

            self.find_dense_regions()

    def find_dense_regions(self):

        # we define region in terms of offsets from the beginning
        # so.... regions[n]:
        #
        #           t-begin -> t0 + n*5min
        #
        #           t-end   -> t-begin + 60min (12 x 5)

        regions = [] # each region has an associated tuple (avg-meaningful,
        #                                                   avg-AWC-actual,
        #                                                   avg-CTC-actual,
        #                                                   avg-CVC-actual)

        rank = [] # each rank corresponds to an region (ranked by hour_region average)
        results = []

        x = 0
        y = 12
        buffer = self.dataset.data[x:y]

        while y <= len(self.dataset.data):
            meaningful_sum = 0
            awc_actual_sum = 0
            ctc_actual_sum = 0
            cvc_actual_sum = 0

            for count in buffer:
                meaningful_sum = meaningful_sum + count[0]
                awc_actual_sum = awc_actual_sum + count[1]
                ctc_actual_sum = ctc_actual_sum + count[2]
                cvc_actual_sum = cvc_actual_sum + count[3]

            meaningful_ratio = float(meaningful_sum)/12
            awc_actual_ratio = float(awc_actual_sum)/12
            ctc_actual_ratio = float(ctc_actual_sum)/12
            cvc_actual_ratio = float(cvc_actual_sum)/12

            print
            print
            print "--------------------------------------------------------------------------"
            print "region: " + str(len(regions))
            print "\n   meaningful: " + str(meaningful_ratio)
            print "   awc: " + str(awc_actual_ratio)
            print "   ctc: " + str(ctc_actual_ratio)
            print "   cvc: " + str(cvc_actual_ratio)

            regions.append((meaningful_ratio,
                            awc_actual_ratio,
                            ctc_actual_ratio,
                            cvc_actual_ratio))

            # push the buffer slice over to the right by one element
            # and re-slice
            # e.g.:
            #
            #       1 5 4 2 7 5 3 8 0 6 4 3 7 1 6 4 2 9 5 7
            #             \     \
            #              -----
            #               \     \-->
            #                -----

            x = x + 1 # bump
            y = y + 1 # bump
            buffer = self.dataset.data[x:y] # re-slice


        self.meaningful_regions = [average[0] for average in regions]
        print self.meaningful_regions
        self.awc_actual_regions = [average[1] for average in regions]
        print self.awc_actual_regions
        self.ctc_actual_regions = [average[2] for average in regions]
        print self.ctc_actual_regions
        self.cvc_actual_regions = [average[3] for average in regions]
        print self.cvc_actual_regions


        self.meaningful_map, self.ranked_meaningful = self.rank_list(self.meaningful_regions, self.top_n)
        self.awc_actual_map, self.ranked_awc_actual = self.rank_list(self.awc_actual_regions, self.top_n)
        self.ctc_actual_map, self.ranked_ctc_actual = self.rank_list(self.ctc_actual_regions, self.top_n)
        self.cvc_actual_map, self.ranked_cvc_actual = self.rank_list(self.cvc_actual_regions, self.top_n)

        print "ranked_meaningful: " + str(self.ranked_meaningful)
        print "ranked awc: " + str(self.ranked_awc_actual)
        print "ranked ctc: " + str(self.ranked_ctc_actual)
        print "ranked cvc: " + str(self.ranked_cvc_actual)


        print
        print
        print



    def rank_list(self, list, top_n):

        region_map = {}
        ranked_list = []

        list = self.set_precision(list, 7)

        # build the map
        for index, region_average in enumerate(list):
            region_map[index] = region_average
        print "region map: " + str(region_map)
        print "top_n : " + str(top_n)
        #while len(ranked_list) < top_n:
        max = 0
        sorted_list = sorted(list, reverse=True)

        #print "entire list ranked: " + str(sorted(list))
        filtered_list = self.filter_overlaps(sorted_list, region_map, top_n)
        return (region_map, filtered_list)


    def filter_overlaps(self, list, map, top_n):
        offset_list = [] # this is a list of interval offsets

        last_interval = None

        for index, x in enumerate(list):
            for key, value in map.items():
                if value == x:
                    last_interval = key
                    offset_list.append(last_interval)
        print "offset list: " + str(offset_list)
        result = []
        result.append(offset_list[0]) # add the densest hour
        last_result = result[len(result)-1]

        for index, x in enumerate(offset_list):
            if len(result) >= top_n:
                break
            if self.overlaping(result, x):
                continue
            else:
                result.append(x)
                last_result = result[len(result)-1]


        # convert back to averages

        for index, x in enumerate(result):
            result[index] = map[x]

        return result

    def overlaping(self, previous_regions, this_start):

        for x in previous_regions:
            if (x > (this_start-12)) and (x < (this_start+12)):
                return True
        return False

    def set_precision(self, list, digits):

        factor = 10**digits
        for index, x in enumerate(list):
            temp = int(x * factor)
            temp = float(temp)/factor
            list[index] = temp
        print "presicion reset list: " + str(list)
        return list

    def density_to_time(self, region_map, ranked_list):
        """
        :param region_map: hashtable with index/average as key/value for out of order interval reference
        :param ranked_list: list with top N densest regions in descending order
        :return: list containing the corresponding time intervals
        """

        interval_rank = []

        #for key, value in region_map:
            #for x in ranked_list:
                #interval =
        for x in ranked_list:
            interval_rank.append(region_map[x])


class WordDensitySet:

    def __init__(self, time):
        """
        WordDensitySet models the adult word distribution as
        a function of time.
        """
        self.time = time # start time

        # We're going to store tuples of (meaningful, awc.Actual, ctc.Actual, cvc.Actual)
        self.data = []

    def __str__(self):
        return str(self.time) + str(self.data)

    def get(self, time):
        # TODO: fix this. return Unix time conversion
        """

        :param time: 3d tuple representing time (mm, dd, yyyy)
        :return: DensityRegions for that visit
        """

        return self.data[time]

#    def hours(self):
 #       """

  #      :return: tuple containing number of full hours and remaining 5 minute chunks
   #                 e.g: (4, 6) = 4 hours + 6*5 minutes
    #    """
     #   hours = len(self.data) / 12
      #  remainder = len(self.data) % 12
       # print "hours(): " + str(hours) + " " + str(remainder)
        #return (hours, remainder)


