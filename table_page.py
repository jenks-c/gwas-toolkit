from tkinter import ttk
import tkinter as tk
import ensembl_vep_info as vep
import threading

class TablePage(ttk.Frame):
    def __init__(self, parent, results, graph_canvas, filename):

        super().__init__(parent)

        ttk.Style().configure("tabheader.TLabel", background = "white",
                                font = ("bold", 11))

        ttk.Style().configure("tabcheck.TCheckbutton", background = "white")

        ttk.Style().configure("topsnp.TEntry")
        ttk.Style().map("topsnp.TEntry",
                        fieldbackground = [("readonly", "lightgreen")])

        ttk.Style().configure("sigsnp.TEntry")
        ttk.Style().map("sigsnp.TEntry",
                        fieldbackground = [("readonly", "lightyellow")])

        self["style"] = "wframe.TFrame"

        self.results = results
        self.graph_canvas = graph_canvas
        self.filename = filename
        self.app = parent
        self.vep = False

    def make_results_table(self, row_n):

        self._label = {}
        self._entry = {}
        self._variable = {}
        self._checkvar = {}
        self._checkbutton = {}
        self._canvas = {}
        self._data_frame = {}

        self.row_n = row_n

        self.data_dictionary = {}

        self.data_rows = self.results.assoclist[:]
        self.column_headers = self.results.assocheader

        self.data_rows.sort(key = lambda x : (x[self.column_headers["p"]]))

        row_count = 0

        self.columns = []

        cell_width = [15, 10, 15, 15, 15]

        self.table_frame = ttk.Frame(self, style = "wframe.TFrame")
        self.table_frame.grid(column = 0, row = 0, sticky = tk.NSEW)

        for key, value in self.column_headers.items():
            self.columns.append(key)

        self.scrollY = ttk.Scrollbar(self.table_frame,
                                    orient=tk.VERTICAL,
                                    command = self.scroll_all,
                                    style = "fancy.Vertical.TScrollbar")
        self.scrollY.grid(row=1, column=7, sticky=tk.NS)

        column_dictionary = {"p" : "P-value", "bp" : "Position (bp)",
                            "chrom" : "Chr", "logp" : "-Log P-value",
                            "snp" : "SNP ID"}

        self.column_n = len(self.columns)
        column_count = 0

        l = l = ttk.Label(self.table_frame, text = "Select",
                            style = "tabheader.TLabel")
        l.grid(row=row_count, column=column_count, sticky= tk.NSEW,
                    pady = 5, padx = 5)
        self._label[0] = l
        column_count += 1

        bonferonni = (0.05 / len(self.results.data))

        for column in self.columns[:-2]:
            #l = ttk.Label(self.data_frame, text = column_dictionary[column],
            #                style = "tabheader.TLabel")
            l = ttk.Label(self.table_frame, text = column_dictionary[column],
                            style = "tabheader.TLabel")
            l.grid(row=row_count, column=column_count, sticky= tk.NSEW,
                    pady = 5)
            self._label[column_count] = l

            column_count += 1

        # make a canvas for each column

        row_count += 1
        column_count = 0
        column_total = len(self._label)

        for column in range(0, column_total):
            canvas = tk.Canvas(self.table_frame, bg = "white", height = 500,
                                        borderwidth = 0, highlightthickness = 0)
            canvas['yscrollcommand'] = self.scrollY.set
            canvas.grid(column = column_count, row = row_count, sticky = tk.NS)

            data_frame = ttk.Frame(canvas, style = "wframe.TFrame")

            table_pane = canvas.create_window(0, 0, anchor = tk.NW,
                                            window = data_frame)

            self._canvas[column_count] = canvas
            self._data_frame[column_count] = data_frame

            column_count += 1

        # add the data to the columns

        row_count = 0
        for row in self.data_rows[:row_n]:

            x = row[self.column_headers["shiftpos"]]
            y = row[self.column_headers["logp"]]
            snp = row[self.column_headers["snp"]]
            chrom = row[self.column_headers["chrom"]]
            bp = row[self.column_headers["bp"]]
            data = []
            data = [x, y, snp, chrom, bp]

            self.data_dictionary[row[self.column_headers["snp"]]] = data

            column_count = 0
            cv = tk.IntVar()
            cv.set(0)
            c = ttk.Checkbutton(self._data_frame[column_count],
                                style = "tabcheck.TCheckbutton",
                                variable = cv)
            c.grid(row = row_count, column = 0, sticky= tk.N)
            self._checkbutton[row_count] = c
            self._checkvar[row_count] = cv
            column_count = 1

            for column in self.columns[:-2]:
                index = (row_count, column_count)
                if column_count == 5:
                    text = "{:.2f}".format(row[4])
                    text = str(text)
                else:
                    text = str(row[column_count - 1])
                v = tk.StringVar()
                v.set(text)
                e = ttk.Entry(self._data_frame[column_count], textvariable = v,
                            style = "tabentry.TEntry",
                            width = cell_width[column_count-1])
                if column_count == 1:
                    for item in self.results.highest_pvals:
                        if item[2] == text:
                            e["style"] = "topsnp.TEntry"
                            break
                if column_count == 4:
                    if float(text) < bonferonni:
                        e["style"] = "sigsnp.TEntry"
                e.grid(row = row_count, column = 0, sticky= tk.NSEW)
                e.state(["readonly"])
                self._entry[index] = e
                self._variable[index] = v
                column_count += 1

            row_count += 1

        for n in range(0, column_total):
            self._canvas[n].update_idletasks()
            contents = self._canvas[n].bbox("all")
            self._canvas[n].config(width = (contents[2]))
            self._canvas[n].config(scrollregion = contents)
            self._canvas[n].update_idletasks()

    def scroll_all(self, *args):
        column_total = len(self._label)
        for n in range(0, column_total):
            self._canvas[n].yview(*args)

    def make_option_and_info_panel(self):

        ttk.Style().configure("infotitle.TLabel", background = "teal",
                                foreground = "white", font = ("bold", 11))

        self.option_info_frame = ttk.Frame(self, style = "wframe.TFrame")
        self.option_info_frame.grid(column = 1, row = 0, sticky = tk.NSEW,
                                    rowspan = 2)

        # View options

        self.view_title = ttk.Label(self.option_info_frame,
                                    text = "View SNPs:",
                                    style = "infotitle.TLabel")
        self.view_title.grid(column = 0, row = 1, columnspan = 3,
                            sticky = tk.NSEW, padx = (10, 0), pady = (10, 0))

        self.view_frame = ttk.Frame(self.option_info_frame,
                                        style = "wframe.TFrame")
        self.view_frame.grid(column = 0, row = 2, sticky = tk.NSEW,
                                    columnspan = 2, padx = (10, 0))

        ttk.Style().configure("wbold.TLabel", background = "white",
                                foreground = "black", font = ("bold", 11))
        ttk.Style().configure("wlabel.TLabel", background = "white",
                                foreground = "black")

        self.showing = ttk.Label(self.view_frame, text = "Now Showing:",
                                        style = "wbold.TLabel")
        self.showing.grid(column = 0, row = 0, sticky = tk.W)

        self.current_view_message = ttk.Label(self.view_frame,
                                        text = f"Top {self.row_n}"
                                                " SNPs Across All Chromosomes",
                                        style = "wbold.TLabel")
        self.current_view_message.grid(column = 1, row = 0, sticky = tk.W,
                                columnspan = 3)

        self.viewoptions = ["All Chromosomes", "Single Chromosome",
                            "Chromosome Region"]

        self.chosen_view = tk.StringVar()
        self.chosen_view.set(self.viewoptions[0])
        self.current_view_selection = self.chosen_view.get()

        self.choice_label = ttk.Label(self.view_frame, text = "Show:",
                                    style = "wbold.TLabel")
        self.choice_label.grid(column = 0, row = 1, sticky = tk.W, pady = [5,0])

        self.view_choice = ttk.Combobox(self.view_frame,
                                        textvariable = self.chosen_view,
                                        values = self.viewoptions)
        self.view_choice.grid(column = 1, row = 1, sticky = tk.W, pady = [5,0])
        self.view_choice.state(["readonly"])
        self.view_choice.bind("<<ComboboxSelected>>", self.select_view_choice)

        self.chr_label = ttk.Label(self.view_frame, text = "Chromosome:",
                                    style = "wbold.TLabel")
        self.chr_label.grid(column = 0, row = 2, sticky = tk.W, pady = [5,0])
        self.chr_label.state(["disabled"])

        self.chroptions = list(self.results.chromset)

        self.chosen_chr = tk.StringVar()

        self.choose_chr = ttk.Combobox(self.view_frame,
                                        textvariable = self.chosen_chr,
                                        values = self.chroptions)
        self.choose_chr.grid(column = 1, row = 2, sticky = tk.W, pady = [5,0])
        self.choose_chr.state(["readonly", "disabled"])
        self.choose_chr.bind("<<ComboboxSelected>>", self.chr_selected)

        self.region_label = ttk.Label(self.view_frame, text = "Region (bp):",
                                        style = "wbold.TLabel")
        self.region_label.grid(column = 0, row = 3, sticky = tk.W, pady = [5,0])
        self.region_label.state(["disabled"])

        self.startbp = tk.StringVar()
        self.start_region = ttk.Entry(self.view_frame,
                                        textvariable = self.startbp)
        self.start_region.grid(column = 1, row = 3, sticky = tk.W, padx = 5,
                                pady = [5,0])
        self.start_region.state(["disabled"])

        self.to_label = ttk.Label(self.view_frame, text = "to",
                                    style = "wbold.TLabel")
        self.to_label.grid(column = 2, row = 3, sticky = tk.W, padx = 5,
                            pady = [5,0])
        self.to_label.state(["disabled"])

        self.endbp = tk.StringVar()

        self.end_region = ttk.Entry(self.view_frame,
                                    textvariable = self.endbp)
        self.end_region.grid(column = 3, row = 3, sticky = tk.W, padx = 5,
                                pady = [5,0])
        self.end_region.state(["disabled"])

        self.check_genome_message = ttk.Label(self.view_frame,
                                        text = "(please check genome build "
                                        "matches array data)",
                                        style = "wbold.TLabel")
        self.check_genome_message.grid(column = 1, row = 4, columnspan = 3)
        self.check_genome_message.state(["disabled"])
        self.region_go_button = ttk.Button(self.view_frame,
                                            text = "Go To Selection",
                                            style = "wbutton.TButton",
                                            command = self.update_data_table)
        self.region_go_button.grid(column = 3, row = 5, columnspan = 3,
                                    pady = [5,0])
        self.region_go_button.state(["disabled"])

        # Selection options

        self.select_title = ttk.Label(self.option_info_frame,
                                    text = "Selected SNPs:",
                                    style = "infotitle.TLabel")
        self.select_title.grid(column = 0, row = 3, columnspan = 2,
                            sticky = tk.NSEW, padx = (10, 0), pady = (10, 0))

        self.select_frame = ttk.Frame(self.option_info_frame,
                                        style = "wframe.TFrame")
        self.select_frame.grid(column = 0, row = 4, sticky = tk.NSEW,
                                    columnspan = 2)

        annotate_selected = ttk.Button(self.select_frame,
                                        command = self.label_selected_snps,
                                        text = "Annotate Selected SNPs",
                                        style = "wbutton.TButton")
        annotate_selected.grid(column = 0, row = 0, padx = 10, sticky = tk.W,
                                pady = (10, 0))

        clear_selection = ttk.Button(self.select_frame,
                                    command = self.clear_checkbuttons,
                                    text = "Clear Selection",
                                    style = "wbutton.TButton")
        clear_selection.grid(column = 1, row = 0, sticky = tk.W, pady = (10, 0),
                            padx = 10)

        # SNP Location Info (VEP)

        self.snp_vep_title = ttk.Label(self.option_info_frame,
                                    text = "SNP Location Info (VEP):",
                                    style = "infotitle.TLabel")
        self.snp_vep_title.grid(column = 0, row = 5, columnspan = 2,
                            sticky = tk.NSEW, padx = (10, 0), pady = (10, 0))

        self.snp_vep_label = ttk.Label(self.option_info_frame,
                                        text = ("Add a column containing "
                                                "details of the SNPs location,"
                                                "\nsuch as if it is intergenic"
                                                " or within a gene."
                                                "\nOnly use if SNP bp is"
                                                " CanFam3."
                                                "\nInformation from"
                                                " Ensembl VEP."),
                                        style = "wlabel.TLabel")
        self.snp_vep_label.grid(column = 0, row = 6, columnspan = 2,
                                sticky = tk.NSEW, padx = (10, 0), pady = (10, 0))

        self.snp_vep_button = ttk.Button(self.option_info_frame,
                                        text = "Add VEP Info",
                                        style = "wbutton.TButton",
                                        command = self.add_vep_column)
        self.snp_vep_button.grid(column = 0, row = 6, sticky = tk.E,
                                padx = (0, 10))

        # Data info

        ttk.Style().configure("datainfo.TLabel", background = "white",
                                foreground = "black")

        self.info_title = ttk.Label(self.option_info_frame,
                                    text = "Data Info:",
                                    style = "infotitle.TLabel")
        self.info_title.grid(column = 0, row = 8, columnspan = 2,
                            sticky = tk.NSEW, padx = (10, 0), pady = (10, 0))

        self.info_canvas = tk.Canvas(self.option_info_frame,
                                    background = "slategrey")
        self.info_canvas.grid(column = 0, row = 9, sticky = tk.W,
                            padx = (10, 0))

        self.infoscrollY = ttk.Scrollbar(self.option_info_frame,
                                    orient=tk.VERTICAL,
                                    command=self.info_canvas.yview,
                                    style = "fancy.Vertical.TScrollbar")
        self.infoscrollY.grid(column=1, row=9, sticky=tk.NS)

        self.info_canvas['yscrollcommand'] = self.infoscrollY.set

        self.info_box = ttk.Label(self.info_canvas,
                                style = "datainfo.TLabel")

        info_pane = self.info_canvas.create_window(
                                            0, 0, anchor = tk.NW,
                                            window = self.info_box)

        info = ""

        info += f"File used:\n{self.filename}\n\n"
        info += f"SNPs in dataset: {len(self.data_rows)}\n\n"
        info += f"Individual Chromosome SNP counts:\n"

        for chrom in self.results.chrom_snplogp:
            info += (f"Chr {chrom}: "
                    f"{len(self.results.chrom_snplogp[chrom])} SNPs\n")

        self.info_box["text"] = info

        self.info_canvas.update_idletasks()

        contents = self.info_canvas.bbox("all")

        self.info_canvas.config(width = (contents[2]), height = 150)
        self.info_canvas.config(scrollregion = contents)
        self.info_canvas.update_idletasks()

    def add_vep_column(self):

        if self.vep == False:
            column_count = 6
            row_count = 0

            l = ttk.Label(self.table_frame, text = "VEP Info",
                            style = "tabheader.TLabel")
            l.grid(row= 0, column=column_count, sticky= tk.NSEW,
                        pady = 5)
            self._label[column_count] = l

            canvas = tk.Canvas(self.table_frame, bg = "white", height = 500,
                                        borderwidth = 0, highlightthickness = 0)
            canvas['yscrollcommand'] = self.scrollY.set
            canvas.grid(column = column_count, row = 1, sticky = tk.NS)

            data_frame = ttk.Frame(canvas, style = "wframe.TFrame")

            table_pane = canvas.create_window(0, 0, anchor = tk.NW,
                                            window = data_frame)

            self._canvas[column_count] = canvas
            self._data_frame[column_count] = data_frame
            while row_count < self.row_n:
                index = (row_count, column_count)
                text = ""

                v = tk.StringVar()
                v.set(text)
                e = ttk.Entry(self._data_frame[column_count], textvariable = v,
                            style = "tabentry.TEntry", width = 50)
                e.grid(row = row_count, column = 0, sticky= tk.NSEW)
                e.state(["readonly"])
                self._entry[index] = e
                self._variable[index] = v
                row_count += 1

            self._canvas[column_count].update_idletasks()
            contents = self._canvas[column_count].bbox("all")
            self._canvas[column_count].config(width = (contents[2]))
            self._canvas[column_count].config(scrollregion = contents)
            self._canvas[column_count].update_idletasks()

        try:
            x = threading.Thread(target=self.get_vep_info)
            x.start()

            self.app.progress.grid(column = 0, row = 5, pady = 5,
                                padx = 10, sticky = tk.W + tk.E)
            self.app.progress["mode"] = "indeterminate"
            self.app.progress.start(200)

            self.app.progresslabel["text"] = ("Getting VEP info from Ensembl")
            self.app.progresslabel.grid(column = 0, row = 4, columnspan = 2, pady = 5)

            self.app.quit.grid(column = 0, row = 4, pady = (5,0), columnspan = 1,
                            sticky = tk.E, padx = 10)

            self.app.progress.update_idletasks()

        except:
            print("Could not get vep info")
    def get_vep_info(self):

        if self.vep == False:
            self.vep = True
            self.vep_info = {}

        snp_dictionary = {}

        for n in range(0, self.row_n):
            index = n
            snp = self._variable[(index, 1)].get()
            chrom = self._variable[(index, 2)].get()
            bp = self._variable[(index, 3)].get()

            alleles = self.results.snp_alleles[snp]

            info = [chrom, bp, alleles]
            snp_dictionary[snp] = info

        self.vep_info = vep.get_ensembl_vep_info(snp_dictionary, self.vep_info)

        for n in range(0, self.row_n):
            index = n
            snp = self._variable[(index, 1)].get()
            if snp in self.vep_info:
                self._variable[(index, 6)].set(self.vep_info[snp])

        self.app.progress.grid_remove()
        self.app.progresslabel.grid_remove()

        self.app.quit.grid(column = 0, row = 6, pady = 5, columnspan = 2,
                        sticky = tk.N)





    def select_view_choice(self, event):
        v = self.chosen_view.get()

        if v == "All Chromosomes":
            self.chr_label.state(["disabled"])
            self.choose_chr.state(["readonly", "disabled"])
            self.region_label.state(["disabled"])
            self.start_region.state(["disabled"])
            self.to_label.state(["disabled"])
            self.end_region.state(["disabled"])
            self.check_genome_message.state(["disabled"])
            self.region_go_button.state(["disabled"])
            self.update_data_table()
            self.chosen_chr.set("")
            self.startbp.set("")
            self.endbp.set("")

        elif v == "Single Chromosome":
            self.chr_label.state(["!disabled"])
            self.choose_chr.state(["readonly", "!disabled"])
            self.region_label.state(["disabled"])
            self.start_region.state(["disabled"])
            self.to_label.state(["disabled"])
            self.end_region.state(["disabled"])
            self.check_genome_message.state(["disabled"])
            self.region_go_button.state(["disabled"])
            self.startbp.set("")
            self.endbp.set("")

        elif v == "Chromosome Region":
            self.chr_label.state(["!disabled"])
            self.choose_chr.state(["readonly", "!disabled"])
            self.region_label.state(["!disabled"])
            self.start_region.state(["!disabled"])
            self.to_label.state(["!disabled"])
            self.end_region.state(["!disabled"])
            self.check_genome_message.state(["!disabled"])
            self.region_go_button.state(["!disabled"])

    def chr_selected(self, event):

        if self.chosen_view.get() == "Single Chromosome":
            self.update_data_table()

    def update_data_table(self, *event):

        chosen_view = self.chosen_view.get()
        chosen_chr = self.chosen_chr.get()
        reg_from = self.startbp.get()
        reg_to = self.endbp.get()

        row_n = self.row_n

        self.data_dictionary = {}
        filtered_data = []

        bonferonni = (0.05 / len(self.results.data))

        self.data_rows.sort(key = lambda x : (x[self.column_headers["p"]]))

        for index, v in self._variable.items():
            v.set("")
        for index, e in self._entry.items():
            e["style"] = "tabentry.TEntry"

        if chosen_view == "Single Chromosome":
            self.current_view_message["text"] = (f"Top {self.row_n}"
                                                " SNPs Across Chromosome "
                                                f"{str(chosen_chr)}")
            for row in self.data_rows:
                if str(row[self.column_headers["chrom"]]) == chosen_chr:
                    filtered_data.append(row)
        if chosen_view == "Chromosome Region":
            self.current_view_message["text"] = (f"Top {self.row_n} SNPs "
                                                "Across The Region Selected")
            for row in self.data_rows:
                chrom = str(row[self.column_headers["chrom"]])
                bp = row[self.column_headers["bp"]]
                if chrom == chosen_chr and int(reg_from) <= bp <= int(reg_to):
                    filtered_data.append(row)
        if chosen_view == "All Chromosomes":
            self.current_view_message["text"] = (f"Top {self.row_n}"
                                                " SNPs Across All Chromosomes")
            filtered_data = self.data_rows[:]

        filtered_data.sort(key = lambda x : (x[self.column_headers["p"]]))

        row_count = 0
        for row in filtered_data[:row_n]:
            x = row[self.column_headers["shiftpos"]]
            y = row[self.column_headers["logp"]]
            snp = row[self.column_headers["snp"]]
            chrom = row[self.column_headers["chrom"]]
            bp = row[self.column_headers["bp"]]
            data = []
            data = [x, y, snp, chrom, bp]

            self.data_dictionary[row[self.column_headers["snp"]]] = data

            if self.vep:
                if snp in self.vep_info:
                    self._variable[(row_count, 6)].set(self.vep_info[snp])

            column_count = 1
            for column in self.columns[:-2]:
                index = (row_count, column_count)
                if column_count == 5:
                    text = "{:.2f}".format(row[4])
                    text = str(text)
                else:
                    text = str(row[column_count - 1])
                self._variable[index].set(text)
                if column_count == 1:
                    for item in self.results.highest_pvals:
                        if item[2] == text:
                            self._entry[index]["style"] = "topsnp.TEntry"
                            break
                if column_count == 4:
                    if float(text) < bonferonni:
                        self._entry[index]["style"] = "sigsnp.TEntry"
                column_count += 1
            row_count += 1

    def clear_checkbuttons(self):
        for key, cv in self._checkvar.items():
            cv.set(0)
        if self.results.ann_list:
            for ann in self.results.ann_list:
                ann.remove()
            self.results.ann_list = []
            self.graph_canvas.draw_idle()

    def update_checkbuttons(self):
        ann_count = self.results.n_annotations
        for key, cv in self._checkvar.items():
            cv.set(0)
        if ann_count:
            for snp in self.results.highest_pvals[:ann_count]:
                for key, cv in self._checkvar.items():
                    snpid = self._variable[(key, 1)].get()
                    if snpid == snp[2]:
                        cv.set(1)
                        break

    def label_selected_snps(self):

        box_checked = False

        for key, cv in self._checkvar.items():
            if cv.get() == 1:
                if self.results.ann_list and not box_checked:
                    for ann in self.results.ann_list:
                        ann.remove()
                    self.results.ann_list = []
                box_checked = True

                snpid = self._variable[(key, 1)].get()
                data = self.data_dictionary[snpid]

                logp2df = "{:.2f}".format(data[1])
                ann = self.results.graph.annotate(
                                f"{logp2df}\n{data[2]}\n{data[3]}:{data[4]}",
                                (data[0], data[1]),
                                xytext = (0, 10), size = "x-small",
                                textcoords = "offset pixels")
                self.results.ann_list.append(ann)
        self.graph_canvas.draw_idle()
