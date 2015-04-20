from Tkinter import *
import tkFileDialog

from silences import *
from clanfile import *
from overlaps import *

class MainWindow:

    def __init__(self, master):

        self.root = master                  # main GUI context
        self.root.title("AudioWords")       # title of window
        self.root.geometry("1300x400")       # size of GUI window
        self.main_frame = Frame(root)       # main frame into which all the Gui components will be placed
        self.main_frame.pack()              # pack() basically sets up/inserts the element (turns it on)

        self.silences = []

        self.sound_regions_file = None

        self.silence_export_file = None
        self.silence_parser = None

        self.clan_file = None
        self.clan__export_file = None

        self.lena_file = None
        self.overlaps = None

        # declare all the GUI buttons and labels
        self.load_sound_button = Button(self.main_frame,
                                        text = "Load Sound Regions",
                                        command = self.load_regions)

        self.export_sound_button = Button(self.main_frame,
                                          text = "Export New Regions",
                                          command = self.export_regions)

        self.load_clan_button = Button(self.main_frame,
                                       text = "Load Clan File",
                                       command=self.load_clan)

        self.load_lena_button = Button(self.main_frame,
                                       text="Load Lena",
                                       command=self.load_lena)

        self.export_overlaps_button = Button(self.main_frame,
                                             text="Export Overlaps",
                                             command=self.export_overlaps)

        self.clear_lena_button = Button(self.main_frame,
                                        text="Clear",
                                        command=self.clear_lena)

        self.export_clan_button = Button(self.main_frame,
                                         text = "Export Clan File",
                                         command = self.export_clan)


        self.clear_clan_button = Button(self.main_frame,
                                        text = "clear",
                                        command = self.clear_clan)

        # this is for the box where you enter the minimum interval of sound
        self.minimum_sound_entry = Entry(self.main_frame, width=10)
        self.minimum_sound_label = Label(self.main_frame, text="minimum sound interval\n(in milliseconds)")
        self.minimum_sound_missing = Label(self.main_frame, text="missing minimum sound interval", fg="red")

        # this is for selecting how many lena overlap regions to find

        self.top_n_region_entry = Entry(self.main_frame, width=10)
        self.top_n_region_label = Label(self.main_frame, text="# of regions")
        self.top_n_missing_label = Label(self.main_frame, text="enter n", fg="red")

        # warning label if you try to export regions without
        # loading initial sound regions file
        self.sound_file_missing = Label(self.main_frame, text="load sound regions first", fg="red")

        self.clan_loaded_label = Label(self.main_frame, text="Clan file loaded", fg="green")
        self.clan_formatting_error = Label(self.main_frame, text="Clan file was malformed", fg="red")

        # load all the buttons onto the GUI
        self.load_sound_button.grid(row=2, column=0)
        self.export_sound_button.grid(row=3, column=0)
        self.load_clan_button.grid(row=2, column=1)
        self.export_clan_button.grid(row=3, column=1)
        self.clear_clan_button.grid(row=4, column=1)
        self.load_lena_button.grid(row=2, column=2)
        self.export_overlaps_button.grid(row=3, column=2)
        self.clear_lena_button.grid(row=4, column=2)


        # load minimum sound box to GUI
        self.minimum_sound_entry.grid(row=4, column=0)
        self.minimum_sound_label.grid(row=5, column=0, rowspan=2)

        # load # of region box onto the GUI
        self.top_n_region_entry.grid(row=5, column=2)
        self.top_n_region_label.grid(row=6, column=2)


        # declare and load the box where parsed silences will be previewed
        self.silence_list_box = Listbox(self.main_frame, width=26, height = 12)
        self.silence_list_box.grid(row=1, column=0)

        # declare and load the box for the word density overlap functions
        self.meaningful_region_box = Listbox(self.main_frame, width=32, height=12)
        self.meaningful_region_box.grid(row= 1, column=2)

        self.awc_region_box = Listbox(self.main_frame, width=32, height=12)
        self.awc_region_box.grid(row=1, column=3)

        self.ctc_region_box = Listbox(self.main_frame, width=32, height=12)
        self.ctc_region_box.grid(row=1, column=4)

        self.cvc_region_box = Listbox(self.main_frame, width=32, height=12)
        self.cvc_region_box.grid(row=1, column=5)

        self.ctc_cvc_box = Listbox(self.main_frame, width=32, height=12)
        self.ctc_cvc_box.grid(row=1, column=6)

        # declare and grid all the labels for the density boxes

        self.meaningful_label = Label(self.main_frame, text="Meaningful")
        self.meaningful_label.grid(row=0, column=2)

        self.awc_label = Label(self.main_frame, text="AWC")
        self.awc_label.grid(row=0, column=3)

        self.ctc_label = Label(self.main_frame, text="CTC")
        self.ctc_label.grid(row=0, column=4)

        self.cvc_label = Label(self.main_frame, text="CVC")
        self.cvc_label.grid(row=0, column=5)

        self.ctc_cvc_label = Label(self.main_frame, text="CTC/CVC")
        self.ctc_cvc_label.grid(row=0, column=6)

    def load_regions(self):

        # check for empty minimum sound box
        if not self.minimum_sound_entry.get():
            self.sound_file_missing.grid_remove()
            self.minimum_sound_missing.grid(row=7, column=0)
            raise Exception("You need to enter a minimum interval of sound to ignore")

        self.minimum_sound_missing.grid_remove()

        # set the path to the audacity regions with a popup directory widget
        self.sound_regions_file = tkFileDialog.askopenfilename()
        self.sound_file_missing.grid_remove()

        # extract the value provided as the minimum sound length
        minimum_sound = float(self.minimum_sound_entry.get())

        # construct the SilenceParser with the regions file and minimum sound.
        # this object extracts the sound regions (ignoring those shorter than minimum_sound
        # and calculates the silences in between them.
        self.silence_parser = SilenceParser(self.sound_regions_file, minimum_sound)

        # load the preview box with all the silences
        self.silence_list_box.delete(0, END)
        for index, item in enumerate(self.silence_parser.silences):
            self.silence_list_box.insert(index, str(item) + " [{}] ".format(index + 1))

    def export_regions(self):

        # check to make sure the initial regions have been loaded
        # and a SilenceParser object has been constructed, otherwise
        # printing warnings and throw an exception
        if self.silence_parser is None:
            self.minimum_sound_missing.grid_remove()
            self.sound_file_missing.grid(row=7, column=0)
            raise Exception("You need to load the audacity sound regions first")

        self.sound_file_missing.grid_remove()

        # get path to new regions export file with a popup directory widget
        self.silence_export_file = tkFileDialog.asksaveasfilename()

        # run the silence parsing anew for each export_silence(),
        # so that the user doesn't have to reload the initial
        # regions every time they need different result
        minimum_sound = float(self.minimum_sound_entry.get())
        self.silence_parser = SilenceParser(self.sound_regions_file, minimum_sound)

        # update the silence preview box
        self.silence_list_box.delete(0, END)
        for index, item in enumerate(self.silence_parser.silences):
            self.silence_list_box.insert(index, str(item) + " [{}] ".format(index + 1))

        # write out each region to a new file (silence_export_file)
        with open(self.silence_export_file, "w") as export_file:

            for index, entry in enumerate(self.silence_parser.sounds):

                # handle the [End] region as a special case
                if (index + 1) == len(self.silence_parser.sounds)\
                    and entry[0] == entry[1]:

                    export_file.write("{0:.6f}\t{1:.6f}\t[End]\n".format(entry[0]/1000,
                                                                         entry[1]/1000))
                else:
                    export_file.write("{0:.6f}\t{1:.6f}\t{2}\n".format(entry[0]/1000,
                                                                       entry[1]/1000,
                                                                       index + 1))


    def load_clan(self):
        # get path for initial clan file to be processed,
        # and print a success label to the GUI
        self.clan_formatting_error.grid_remove()
        self.clan_file = tkFileDialog.askopenfilename()
        if self.clan_file != "":
            self.clan_loaded_label.grid(row=1, column=1)

    def export_clan(self):
        # get path for new/modified clan file
        self.export_clan_file = tkFileDialog.asksaveasfilename()

        # We surround the ClanFileParser operations
        # in a try: except: block because in some unlikely
        # circumstances the clan file can be formatted incorrectly,
        # requiring that we stop all operations and report the error.
        try:
            ClanFileParser(self.clan_file, self.export_clan_file)\
                .insert_silences(self.silence_parser.silences)
        except Exception, e:
            self.clan_loaded_label.grid_remove()
            self.clan_formatting_error.grid(row=1, column=1)
            print e.args

    def clear_clan(self):

        self.clan_file = None
        self.clan_loaded_label.grid_remove()

    def clear_silences(self):

        self.silences = None
        self.sound_regions_file = None

        self.silence_list_box.delete(0, END)

    def load_lena(self):
        self.clear_lena()
        self.lena_file = tkFileDialog.askopenfilename()


        if not self.top_n_region_entry.get():
            print "we're inside the top_n missing check"
            self.top_n_missing_label.grid(row=7, column=2)
            #raise Exception("You're missing the top_n entry")
            return
        else:
            print "we're still in load_lena()"
            self.top_n_missing_label.grid_remove()
            self.overlaps = Overlaps(self.lena_file, int(self.top_n_region_entry.get()))

            for index, x in enumerate(self.overlaps.ranked_meaningful):
                self.meaningful_region_box.insert(index,
                                                  str(x) + " - " + str(self.overlaps.meaningful_map[x])+ " - " +\
                                                  self.offset_to_hour(x) + " - " + \
                                                  str(self.offset_to_millisecond(x)) + "ms ")

            for index, x in enumerate(self.overlaps.ranked_awc_actual):
                self.awc_region_box.insert(index,
                                           str(x) + " - " + str(self.overlaps.awc_actual_map[x])+ " - " +\
                                           self.offset_to_hour(x) + " - " + \
                                           str(self.offset_to_millisecond(x)) + "ms ")

            for index, x in enumerate(self.overlaps.ranked_ctc_actual):
                self.ctc_region_box.insert(index,
                                           str(x) + " - " + str(self.overlaps.ctc_actual_map[x])+ " - " +\
                                           self.offset_to_hour(x) + " - " + \
                                           str(self.offset_to_millisecond(x)) + "ms ")

            for index, x in enumerate(self.overlaps.ranked_cvc_actual):
                self.cvc_region_box.insert(index,
                                           str(x) + " - " + str(self.overlaps.awc_actual_map[x])+ " - " +\
                                           self.offset_to_hour(x) + " - " + \
                                           str(self.offset_to_millisecond(x)) + "ms ")

            for index, x in enumerate(self.overlaps.ranked_ctc_cvc):
                self.ctc_cvc_box.insert(index,
                                        str(x) + " - " +str(self.overlaps.ctc_cvc_map[x])+ " - " +\
                                        self.offset_to_hour(x) + " - " +\
                                        str(self.offset_to_millisecond(x)) + "ms ")

    def clear_lena(self):
        self.lena_file = None
        self.overlaps = None
        self.overlaps_export_file = None

        self.meaningful_region_box.delete(0, END)
        self.awc_region_box.delete(0, END)
        self.ctc_region_box.delete(0, END)
        self.cvc_region_box.delete(0, END)
        self.ctc_cvc_box.delete(0, END)


    def export_overlaps(self):
        """
        This gets called after the silences have been processed and
        inserted into the clan file. The loaded clan file should be
        this new one with the silences inserted. This function constructs
        a ClanFileParser object, and immediately calls its insert_overlaps()
        method (passing the ranked ctc_cvc offsets, their map, and the
         silence regions from the previous silence inserting step.
        :return:
        """
        overlaps_export_file = tkFileDialog.asksaveasfilename()

        ClanFileParser(self.clan_file, overlaps_export_file).\
                        insert_overlaps(self.overlaps.ranked_ctc_cvc,
                                        self.overlaps.ctc_cvc_map, self.silence_parser.silences)

    def offset_to_hour(self, offset):

        hours = offset / 12
        minutes = 5 * (offset % 12)

        if minutes < 10:
            return "{}:0{}".format(hours, minutes)
        else:
            return "{}:{}".format(hours, minutes)

    def offset_to_millisecond(self, offset):

        return 5 * offset * 60 * 1000

    def offset_lookup(self, average, map):
        """
        Returns a list of all offsets which have a particular
        average.

        :param average: some value for offset average
        :param map: offset-average mapping
        :return: all the offsets which have "average" as their average
        """
        offsets = []

        for key, value in map.iteritems():
            if value == average:
                offsets.append(key)
        print "offsets for " + str(average) + "  " + str(offsets)
        milliseconds = [self.offset_to_millisecond(offsets[i]) for i, item in enumerate(offsets)]
        print "milliseconds: " + str(milliseconds)
        return offsets

if __name__ == "__main__":

    root = Tk()
    MainWindow(root)
    root.mainloop()