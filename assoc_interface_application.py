from tkinter import filedialog
from tkinter import ttk
import tkinter as tk

import threading

from assoc_results import Assoc
from GWAS_toolkit_functions import *
from graph_page import GraphPage
from table_page import TablePage

class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        self.set_styles()
                
        self.assoc_results = Assoc()
        
        self.pack(expand = True)
        self.create_widgets()
        
    def set_styles(self):
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("greyframe.TFrame", background = "darkslategrey")
        
        self["style"] = "greyframe.TFrame"
        
        self.style.configure("wbutton.TButton", background = "white")

        self.style.configure("greynote.TNotebook", background = "darkslategrey")
        
        self.style.map("TNotebook.Tab", background=[("selected", "white")])
        
        self.style.configure("TNotebook.Tab", background = "white")
        
        self.style.configure("TCombobox",
                            background = "white",
                            foreground = "black")
        
        self.style.map("TCombobox", fieldbackground=[("readonly", "white")],
                        foreground=[("focus","black"),("disabled", "grey")],
                        bordercolor=[("disabled", "white")])
        
        self.style.configure("wframe.TFrame", background = "white")
        
        self.style.configure("wlframe.TLabelframe",
                            background = "white")
        
        self.style.configure("wlabel.TLabel",
                            background = "white", foreground = "black")
        
        self.style.map("TLabel", background=[("disabled", "white")],
                        foreground=[("disabled","grey")])
        
        self.style.configure("wradio.TRadiobutton", background = "white")
        
        self.style.map("wradio.TRadiobutton",
                        background=[("disabled", "white")])
                        
        self.style.configure("Run.TButton", font = ("bold", 12),
                            background = "white")
                            
        self.style.configure("teallabel.TLabel", background = "teal",
                            foreground = "white", font = ("bold", 11))
                            
        self.style.configure("fancy.Vertical.TScrollbar",
                            background = "white",
                            troughcolor = "white")
                            
        self.style.configure("fancy.Horizontal.TScrollbar",
                            background = "white",
                            troughcolor = "white")
                            
        self.style.configure("Optpane.TLabelframe",
                            background = "white")
        
        self.style.configure("Optlabel.TLabel",
                            background = "white", foreground = "black")
        
        self.style.configure("Optheadlabel.TLabel",
                            background = "white", foreground = "teal")
        
        self.style.configure("Optscrol.Horizontal.TScale",
                            background = "teal",
                            troughcolor = "white")
                            
        self.style.configure("green.Horizontal.TProgressbar",
                        troughcolor ='white', background='green')

    def create_widgets(self):
        
        self.quit = ttk.Button(self, text="QUIT",
                              command=self.master.destroy,
                              style = "wbutton.TButton")
        self.quit.grid(column = 0, row = 10, pady = 5, columnspan = 2)
        self.make_input_frame()
        
    def make_input_frame(self):
        
        self.assocnotebook = ttk.Notebook(self, style = "greynote.TNotebook")
        self.assocnotebook.grid(column = 0, row = 1, sticky = tk.NSEW)
        
        self.input_frame = ttk.Frame(self, padding = 10,
                                    style = "wframe.TFrame")
        self.input_frame.grid(column = 0, row = 1, sticky = tk.NSEW)
        
        self.assocnotebook.add(self.input_frame, text = "Input")
        
        #self.title_img = tk.PhotoImage(file = "title.gif")
        
        #self.title_label = ttk.Label(self.input_frame, image = self.title_img,
        #                            style = "wlabel.TLabel")
        #self.title_label.grid(column = 0, row = 0, columnspan = 2, pady = 20)

        self.logo_canvas = tk.Canvas(self.input_frame, bg = "white", height = 150, width = 350,
                                        borderwidth = 0, highlightthickness = 0)
        self.logo_canvas.grid(column = 0, row = 0, columnspan = 2)
        self.logo_outer = self.logo_canvas.create_oval(30,30,320,130, fill = "light blue", outline = "white")
        self.logo_text = self.logo_canvas.create_text(175, 75, anchor = tk.CENTER)
        self.logo_canvas.itemconfig(self.logo_text, text = "GWAS Toolkit v3", font = ("courier", 25, "bold", "underline"))
        self.logo_canvas.update_idletasks()

        self.enter_text = ttk.Entry(self.input_frame, width = 75)
        self.enter_text.insert(0, "")
        self.enter_text.grid(column = 0, row = 2, padx = 5, sticky = tk.W)
        self.enter_text.state(["!disabled", "readonly"])
        
        self.entertextlabel = ttk.Label(self.input_frame,
                                        style = "wlabel.TLabel")
        self.entertextlabel["text"] = ("Enter your file name and location"
                                    ", click browse to pick file:")
        self.entertextlabel.grid(column = 0, row = 1, padx = 5, sticky = tk.W)
        
        self.browse = ttk.Button(self.input_frame, style = "wbutton.TButton")
        self.browse["text"] = "Browse Files"
        self.browse["command"] = self.pick_file
        self.browse.grid(column = 1, row = 2, padx = 5)
        
        self.go_button = ttk.Button(self.input_frame, style = "wbutton.TButton")
        self.go_button["text"] = "Continue"
        self.go_button["command"] = self.get_file_info
        self.go_button.grid(column = 0, row = 3, padx = 5)
        self.go_button.state(["disabled"])
        
    def check_if_empty(self):
        if self.enter_text.get() == "":
            self.go_button.state(["disabled"])
        elif self.enter_text.get() != "":
            self.go_button.state(["!disabled"])
        
    def pick_file(self):
        filename = tk.filedialog.askopenfilename(defaultextension = ".assoc",
                                        filetypes=[("ASSOC", ".assoc"),
                                                    ("TEXT", ".txt")],
                                        title = "Choose Data File")
        self.enter_text.state(["!readonly"])
        self.enter_text.delete(0, "end")
        self.enter_text.insert(0, filename)
        self.enter_text.state(["readonly"])
        self.check_if_empty()
    
    def get_file_info(self):
        file_location = self.enter_text.get()
        self.header_dict, self.data = get_data(file_location)
        self.filename = ""
        self.filename = get_simple_filename(file_location)
        file_format_query, self.filetype = find_file_type(self.header_dict)
        self.assoc_check_frame(self.filename, file_format_query)
        
    def assoc_check_frame(self, name, file_format_query):
        self.browse.grid_remove()
        self.go_button.grid_remove()
        
        check_labeltitle = ttk.Label(self.input_frame, text = "Data Check",
                                    style = "wlabel.TLabel")
        self.checkframe = ttk.LabelFrame(self.input_frame, text = "Data Check",
                                        style = "wlframe.TLabelframe",
                                        labelwidget = check_labeltitle)
        self.checkframe.grid(column = 0, row = 3, sticky = tk.N + tk.W + tk.E,
                            padx = 10, pady = 10)
        self.checkframe["padding"] = 10
        self.checkframe.configure(borderwidth = 2)
        
        self.data_info = ttk.Label(self.checkframe, style = "wlabel.TLabel")
        self.data_info["text"] = f"There are {len(self.data)} rows in {name}"
        self.data_info.grid(column = 0, row = 0, sticky = tk.N + tk.S + tk.E + tk.W)
        
        self.format_query_message = ttk.Label(self.checkframe,
                                            style = "wlabel.TLabel")
        self.format_query_message["text"] = "\n" + file_format_query
        self.format_query_message.grid(column = 0, row = 1, sticky = tk.W)
        
        if self.filetype != "unknown":
            self.check_yes_no = tk.IntVar()
        
            self.yes_check = ttk.Radiobutton(self.checkframe, text = "Yes",
                                            style = "wradio.TRadiobutton")
            self.yes_check.grid(column = 0, row = 2, sticky = tk.W, pady = 5)
            self.yes_check["variable"] = self.check_yes_no
            self.yes_check["value"] = 1
        
            self.no_check = ttk.Radiobutton(self.checkframe, text = "No",
                                            style = "wradio.TRadiobutton")
            self.no_check.grid(column = 0, row = 2, pady = 5)
            self.no_check["variable"] = self.check_yes_no
            self.no_check["value"] = 0
        
            self.check_go = ttk.Button(self.checkframe, text = "Continue",
                                        style = "wbutton.TButton")
            self.check_go.grid(column = 0, row = 3, pady = 10, padx = 5,
                                sticky = tk.W)
            self.check_go["command"] = self.check_input
        elif self.filetype == "unknown":
            self.user_manual_input()
        
    def check_input(self):
        if self.check_yes_no.get() == 0:
            self.user_manual_input()
        elif self.check_yes_no.get() == 1:
            self.prep_to_run()
            
    def user_manual_input(self):
        if self.filetype != "unknown":
            self.yes_check.state(["disabled"])
            self.no_check.state(["disabled"])
            self.check_go.grid_remove()
        
        user_input_titlelabel = ttk.Label(self.input_frame,
                                        style = "wlabel.TLabel",
                                        text = "Manual Data Column Input")
        self.user_input_col_frame = ttk.LabelFrame(self.input_frame,
                                        style = "wlframe.TLabelframe",
                                        labelwidget = user_input_titlelabel)
        self.user_input_col_frame.grid(column = 0, row = 3, rowspan = 2,
                                    sticky = tk.N + tk.W + tk.E + tk.S, 
                                    padx = 10, pady = 10)
        self.user_input_col_frame["padding"] = 10
                                    
        self.user_input_message = ttk.Label(self.user_input_col_frame,
                                            style = "wlabel.TLabel")
        self.user_input_message["text"] = ("Please input the header of the "
                                        "column that contains the following:")
        self.user_input_message.grid(column = 0, row = 0, sticky = tk.W)
        
        self.optionlist = []
        for key, value in self.header_dict.items():
            self.optionlist.append(f"Column {int(value) + 1}: '{key}'")
        
        self.firstlabel = ttk.Label(self.user_input_col_frame,
                                    text = "The chromosome number:",
                                    style = "wlabel.TLabel")
        self.firstlabel.grid(column = 0, row = 1, sticky = tk.W, pady = 5,
                            padx = 5)
        self.first_drop_value = tk.StringVar()
        self.first_drop_value.set(self.optionlist[0])
        self.firstoptions = ttk.Combobox(self.user_input_col_frame,
                                        textvariable = self.first_drop_value,
                                        values = self.optionlist)
        self.firstoptions.state(["!disabled", "readonly"])
        self.firstoptions.grid(column = 1, row = 1, sticky = tk.E, pady = 5)

        self.secondlabel = ttk.Label(self.user_input_col_frame,
                                    text = "The SNP name / ID:",
                                    style = "wlabel.TLabel")
        self.secondlabel.grid(column = 0, row = 2, sticky = tk.W, pady = 5,
                            padx = 5)
        self.second_drop_value = tk.StringVar()
        self.second_drop_value.set(self.optionlist[1])
        self.secondoptions = ttk.Combobox(self.user_input_col_frame,
                                        textvariable = self.second_drop_value,
                                        values = self.optionlist)
        self.secondoptions.state(["!disabled", "readonly"])
        self.secondoptions.grid(column = 1, row = 2, sticky = tk.E, pady = 5)
        
        self.thirdlabel = ttk.Label(self.user_input_col_frame,
                                    text = "The bp position:",
                                    style = "wlabel.TLabel")
        self.thirdlabel.grid(column = 0, row = 3, sticky = tk.W, pady = 5,
                            padx = 5)
        self.third_drop_value = tk.StringVar()
        self.third_drop_value.set(self.optionlist[2])
        self.thirdoptions = ttk.Combobox(self.user_input_col_frame,
                                        textvariable = self.third_drop_value,
                                        values = self.optionlist)
        self.thirdoptions.state(["!disabled", "readonly"])
        self.thirdoptions.grid(column = 1, row = 3, sticky = tk.E, pady = 5)
        
        self.fourthlabel = ttk.Label(self.user_input_col_frame,
                                    text = "The p-value from the association"
                                            " analysis:",
                                    style = "wlabel.TLabel")
        self.fourthlabel.grid(column = 0, row = 4, sticky = tk.W, pady = 5,
                            padx = 5)
        self.fourth_drop_value = tk.StringVar()
        self.fourth_drop_value.set(self.optionlist[3])
        self.fourthoptions = ttk.Combobox(self.user_input_col_frame,
                                        textvariable = self.fourth_drop_value,
                                        values = self.optionlist)
        self.fourthoptions.state(["!disabled", "readonly"])
        self.fourthoptions.grid(column = 1, row = 4, sticky = tk.E, pady = 5)
        
        self.input_go = ttk.Button(self.user_input_col_frame,
                                        text = "Continue",
                                        style = "wbutton.TButton")
        self.input_go.grid(column = 0, row = 5, sticky = tk.W, pady = 5,
                            padx = 5)
        self.input_go["command"] = self.prep_to_run
        
    def prep_to_run(self):
        if self.check_yes_no.get() == 0 or self.filetype == "unknown":
            self.input_go.grid_remove()
            self.firstoptions.state(["disabled"])
            self.secondoptions.state(["disabled"])
            self.thirdoptions.state(["disabled"])
            self.fourthoptions.state(["disabled"])

        elif self.check_yes_no.get() == 1:
            self.yes_check.state(["disabled"])
            self.no_check.state(["disabled"])
            self.check_go.grid_remove()
        
        
        self.run_assoc_button = ttk.Button(self, style = "Run.TButton")
        self.run_assoc_button["text"] = "Plot Graph"
        self.run_assoc_button.grid(column = 0, row = 4, columnspan = 2,
                                    pady = 10)
        self.run_assoc_button["command"] = self.plot_graph

    def plot_graph(self):
        self.run_assoc_button.grid_remove()
        
        self.progresslabel = ttk.Label(self, style = "wlabel.TLabel")
        self.progresslabel.grid(column = 0, row = 4, columnspan = 2, pady = 5)
        
        self.progress = ttk.Progressbar(self, mode = "determinate",
                                        style = "green.Horizontal.TProgressbar")
        self.progress.grid(column = 0, row = 5, pady = 5,
                            padx = 10, sticky = tk.W + tk.E)
                            
        self.quit.grid(column = 0, row = 4, pady = (5,0), columnspan = 1,
                        sticky = tk.E, padx = 10)
        
        self.progress.update_idletasks()

        if self.check_yes_no.get() == 0 or self.filetype == "unknown":
            self.item_indexs = {}
            self.item_indexs["p"] = self.optionlist.index(
                                                    self.fourth_drop_value.get()
                                                        )
            self.item_indexs["snp"] = self.optionlist.index(
                                                    self.second_drop_value.get()
                                                        )
            self.item_indexs["chr"] = self.optionlist.index(
                                                    self.first_drop_value.get()
                                                        )
            self.item_indexs["bp"] = self.optionlist.index(
                                                    self.third_drop_value.get()
                                                        )

        elif self.check_yes_no.get() == 1:
            self.item_indexs = {}
            self.item_indexs = get_assoc_columns(self.header_dict,
                                                self.filetype, plot = "assoc")
            print(self.item_indexs)
        
        self.assoc_results.data = self.data
        self.assoc_results.item_indexs = self.item_indexs
        
        self.assoc_results = prep_assoc_data(self.assoc_results)
        
        self.progress["maximum"] = len(self.assoc_results.chromset) + 0.001
        

        x = threading.Thread(target=self.threaded_plot, daemon = True)
        x.start()
        
        self.assoc_page = GraphPage(master = self,
                                    results = self.assoc_results,
                                    plot_type = "all_chr")
        self.assoc_page.grid(column = 0, row = 1)
        
        self.table_page = TablePage(self, self.assoc_results,
                                    self.assoc_page.canvas, self.filename)
        self.table_page.grid(column = 0, row = 1, sticky = tk.NSEW)
        
        self.assocnotebook.add(self.assoc_page, text = "Association Plot")
        self.assocnotebook.add(self.table_page, text = "Data")
        
        self.assocnotebook.select(self.assoc_page)
        
    def threaded_plot(self):
        for chrom in self.assoc_results.chromset:
            chrom_snpcount = len(self.assoc_results.chrom_snpnum[chrom])
            self.progresslabel["text"] = (f"Plotting: chr{chrom} "
                                        f"({chrom_snpcount} SNPs)")
            self.progresslabel.update_idletasks()
            self.assoc_results = plot_assoc_chr(self.assoc_results, chrom)
            self.progress.step()
            self.progress.update_idletasks()
            
        self.progress.grid_remove()
        self.progresslabel.grid_remove()
        
        self.quit.grid(column = 0, row = 6, pady = 5, columnspan = 2,
                        sticky = tk.N)
        
        self.assoc_results = plot_assoc_graph(self.assoc_results)
        
        self.assoc_results.fig.subplots_adjust(left = 0.07, right = 0.98,
                                                top = 0.92)
        self.assoc_page.canvas.draw_idle()
        self.assoc_page.graph_option_pane.update_text_options()
        self.assoc_page.graph_option_pane.update_y_axis_option()
        self.table_page.make_results_table(50)
        self.table_page.make_option_and_info_panel()
