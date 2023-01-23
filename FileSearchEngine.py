# Created by Alan Mai

import pickle  # used to serialize index object
import os  # used for walk function
import PySimpleGUI as psg


class FileSearchEngine:
    def __init__(self) -> None:
        self.file_index = [] # used to store (root, dir, file) tuples returned by os.walk
        self.returned_files = []  # file list returned by search method
        self.num_matches = 0  # how many files match the search key
        self.num_files_searched = 0  # how many files were searched

    '''Creates an index to search files/folders upon later
       Creates a pickle file'''
    def create_index(self, values):
        root_path = values["PATH"] #values is a dictionary of events
        # store all of the traversed tuples(root, dir, files) in file_index
        self.file_index = [(root, dirs, files) for root, dirs, files in os.walk(root_path) if files]

        # write the data into a pickle file
        with open("index_data.pickle", "wb") as file:
            pickle.dump(self.file_index, file)

    '''If there is already an index made(a pickle file exists), than we can just load that up instead of calling os.walk()
       If pickle file does not exist, set file_index to empty'''
    def load_index(self) -> None:  # with an existing index we do not need a root path in
        try:  # could try to load in index that does not exist
            with open("index_data.pickle", "rb") as file:
                # loading the searlized data from previous index
                self.file_index = pickle.load(file)
        except FileNotFoundError:
            self.file_index = []

    '''Searches through file_index to get all the files that matches
       Returns returned_files which contains all the files that have matched'''
    def search(self, values):
        # must clear matches, num_files_searched and returend files             
        self.num_matches = 0
        self.num_files_searched = 0
        self.returned_files.clear()

        # load search term from dictionary event
        search_term = values["TERM"]

        # performing the search
        # iterate through file_index which contains tuples (root, [dir1, dir2], [file1, file2, file3])
        for root, dirs, files in self.file_index:
            # determine whether to iterate through folders or files
            file_folder = dirs if values["FOLDER"] else files
            for file in file_folder:  # iterate through the file/folder list in tuple
                self.num_files_searched += 1  # increment counter
                if (search_term.lower() in file.lower() and values["CONTAINS"] or  # if the file contains search term
                    file.lower().endswith(search_term.lower()) and values["ENDSWITH"] or # if the file ends with search term
                    file.lower().startswith(search_term.lower()) and values["STARTSWITH"]):  # if the file starts with search term
                    self.num_matches += 1  # successful match
                    self.returned_files.append("{}\{}".format(root, file))
                else:
                    pass

        # we need to store the data in a text file
        with open("matched_files.txt", "w") as file:
            for matched_file in self.returned_files:
                try:
                    file.write(matched_file + "\n")
                except: pass

    '''Opens a file using the FILE_NUM key in events'''
    def open_returned_files(self, values):
        try:
            user_selected_file = self.returned_files[int(values["FILE_NUM"])] #indexs returned list to get the correct file
            os.startfile(user_selected_file)
            print("********** FILE OPENED SUCCESSFULLY **********\n")
        except:
            print("********** AN ERROR HAS OCCURED **********\n")


class GUI:
    def __init__(self) -> None:
        psg.ChangeLookAndFeel('LightGrey1') #changes theme

        self.layout = [
            # row1
            [psg.Text("Search Term:"),
             psg.Input(focus=True, key="TERM")],
            # row2
            [psg.Text("Filter:"),
             psg.Radio("Contains", group_id="filter_choice",
                       default=True, key="CONTAINS"),
             psg.Radio("Ends With", group_id="filter_choice", key="ENDSWITH"),
             psg.Radio("Starts With", group_id="filter_choice", key="STARTSWITH")],
            # row3
            [psg.Text("Type:"),
             psg.Radio("File", group_id="type_choice",
                       default=True, key="FILE"),
             psg.Radio("Folder", group_id="type_choice", key="FOLDER")],
            # row4
            [psg.Text("Root:"),
             psg.Input("C:/", key="PATH"),
             psg.FolderBrowse("Browse", size=(10, 1)),
             psg.Button("Re-Index", size=(10, 1), key="RE_INDEX"),
             psg.Button("Search", size=(10, 1), bind_return_key=True, key="SEARCH")],
            # row5
            [psg.Output(size=(150, 30))],
            # row6
            [psg.Text("Select File/Folder Number:"),
             psg.Input(size=(10, 1), key="FILE_NUM"),
             psg.Button("Open", size=(5, 1), key="OPEN")]
        ]
        #set window
        self.window = psg.Window(
            "Alan's File Search Engine", self.layout, default_element_size=(100, 100))


if __name__ == "__main__":
    my_gui = GUI()
    engine = FileSearchEngine()
    engine.load_index()  # load index if there is one, else than empty list
    while True:
        # values is now a dictionary with key terms {Path: "", Term: ""}
        event, value = my_gui.window.read()

        if event == None:
            break

        if event == "SEARCH":
            engine.search(value) #calls search and prints out to gui
            for i in range(len(engine.returned_files)):
                print("{}) {}".format(i, engine.returned_files[i]))
            print("\n********** MATCHED {} of {} **********\n".format(
                engine.num_matches, engine.num_files_searched))

        if event == "RE_INDEX": #calls create_index and prints to gui
            engine.create_index(value)
            print("********** NEW INDEX CREATED **********\n")

        if event == "OPEN": #calls open function
            engine.open_returned_files(value)
