from tkinter import ttk
import tkinter as tk

import matplotlib.colors as mcolors
import graph_page as gp
from imputed_data_graph_page import ImputedDataGraphPage

from GWAS_toolkit_functions import *

class GraphOptionPane(ttk.Frame):
    def __init__(self, master, app, results, canvas, plot_type):
        
        super().__init__(master)
        
        self["style"] = "wframe.TFrame"
        
        self.master = master
        self.results = results
        self.plot_type = plot_type
        self.app = app
        
        self.fig_canvas = canvas
        
        self.title = ttk.Label(self, text = "Figure Options",
                                    style = "teallabel.TLabel",
                                    padding = 5)
        
        self.canvas = tk.Canvas(self, bg = "white", height = 500, width = 345,
                                        scrollregion = (0, 0, 345, 1000),
                                        borderwidth = 0, highlightthickness = 0)
        
        self.scrollY = ttk.Scrollbar(self,
                                    orient=tk.VERTICAL,
                                    command=self.canvas.yview,
                                    style = "fancy.Vertical.TScrollbar")
                                    
        self.title.grid(column = 0, row = 0, sticky = tk.NSEW, pady = 5,
                        columnspan = 2)
        self.canvas.grid(column = 0, row = 1, sticky = tk.NS)
        self.scrollY.grid(row=1, column=1, sticky=tk.NS)

        self.canvas['yscrollcommand'] = self.scrollY.set
        
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.choice_of_other_plots()
            print(self.plot_type, "choice")
        elif (self.plot_type == "single_chr" or
                self.plot_type == "single_chr_imputed"):
            self.single_chr_choice()
            print(self.plot_type, "chr choice")
        elif self.plot_type == "qq":
            print(self.plot_type, "none")
            bbox = [10,0,0,0]
            self.text_options(bbox)
            self.scrollY.grid_forget()
        
        contents = self.canvas.bbox("all")
        
        self.canvas.config(width = (contents[2] + 10))
        self.canvas.config(scrollregion = contents)
        self.canvas.update_idletasks()
            
    def single_chr_choice(self):
        
        self.chr_choice_label = ttk.Label(self.canvas,
                                        text = "Choose Chromosome:",
                                        style = "Optlabel.TLabel")
        chr_choice_label_pane = self.canvas.create_window(
                                            10, 10, anchor = tk.NW,
                                            window = self.chr_choice_label)
        
        self.canvas.update_idletasks()
        chr_choice_bbox = self.canvas.bbox(chr_choice_label_pane)
        
        self.chr_list = list(self.results.chromset)
        self.chr_list.sort()
        self.chosen_chr = tk.StringVar()
        self.chosen_chr.set(self.master.chrom)
        self.chr_box = ttk.Combobox(self.canvas,
                                    textvariable = self.chosen_chr,
                                    values = self.chr_list)
                                    
        chr_box_pane = self.canvas.create_window(
                                            (chr_choice_bbox[2] + 10),
                                            chr_choice_bbox[1], anchor = tk.NW,
                                            window = self.chr_box)

        self.chr_box.state(["readonly"])
        if self.plot_type == "single_chr":
            self.chr_box.bind("<<ComboboxSelected>>", self.change_chr)
        elif self.plot_type == "single_chr_imputed":
            self.chr_box.bind("<<ComboboxSelected>>", self.change_imputed_chr)
        
        self.text_options(chr_choice_bbox)
        
    def change_imputed_chr(self, event):
        
        chrom = self.chosen_chr.get()
        
        self.master.plot_single_chr_imputed(chrom, plot = "replace")
        
        self.current_title.set(str(self.master.graph.get_title()))
        self.current_xlabel.set(self.master.graph.get_xlabel())
        self.current_ylabel.set(self.master.graph.get_ylabel())
        
        self.app.assocnotebook.tab("current",
                                    text = f"Chr {chrom} Plot (Imputed)")
        
        self.implement_choices()
        self.master.canvas.draw()
        
    def change_chr(self, event):
        
        chrom = self.chosen_chr.get()
        fig, graph, series = plot_single_chr(self.master.results, int(chrom))
        self.master.graph = graph
        self.master.series = series
        
        self.master.canvas.figure = fig
        
        self.current_title.set(str(self.master.graph.get_title()))
        self.current_xlabel.set(self.master.graph.get_xlabel())
        self.current_ylabel.set(self.master.graph.get_ylabel())
        
        self.app.assocnotebook.tab("current", text = f"Chr {chrom} Plot")
        
        self.implement_choices()
        self.master.canvas.draw()
        
    def implement_choices(self):
        
        self.margins_set = False
        self.set_margin_xlim_method(self.chosen_margin_float.get())
        
        self.plot_bonferonni_line()
        self.single_chr_colour()
        
        self.set_x_fontsize()
        self.set_y_fontsize()
        self.set_ylabel_fontsize()
        self.set_xlabel_fontsize()
        self.set_title_fontsize()
        self.set_graph_font()
            
    def choice_of_other_plots(self):
        
        self.single_chr_button = ttk.Button(self.canvas,
                                   text = "Plot Single Chr",
                                   style = "wbutton.TButton",
                                   command = self.make_single_chr_page)
        singlechr_pane = self.canvas.create_window(
                                            10, 10, anchor = tk.NW,
                                            window = self.single_chr_button)
                                            
        if self.plot_type == "imputed":
            self.single_chr_button["text"] = "Plot Single Chr (Imputed)"
                                            
        self.canvas.update_idletasks()
        singlechr_bbox = self.canvas.bbox(singlechr_pane)
        
        self.qqplot_button = ttk.Button(self.canvas,
                                        text = "Plot QQ-Plot",
                                        style = "wbutton.TButton",
                                        command = self.make_qq_page)
        qq_pane = self.canvas.create_window(
                                            (singlechr_bbox[2] + 10),
                                            singlechr_bbox[1], anchor = tk.NW,
                                            window = self.qqplot_button)
                                            
        self.canvas.update_idletasks()
        qq_bbox = self.canvas.bbox(qq_pane)
        
        if self.plot_type == "all_chr":
            self.imputed_button = ttk.Button(self.canvas,
                                   text = "Plot Imputed Data",
                                   style = "wbutton.TButton",
                                   command = self.make_imputed_page)
        
            imputed_pane = self.canvas.create_window(
                                            (qq_bbox[2] + 10),
                                            qq_bbox[1],
                                            anchor = tk.NW,
                                            window = self.imputed_button)
        
        self.text_options(singlechr_bbox)
        
    def make_imputed_page(self):
        
        self.app.imputed_page = ImputedDataGraphPage(master = self.app,
                                                results = self.results)
        self.app.imputed_page.grid(column = 0, row = 1)
        
        self.app.assocnotebook.add(self.app.imputed_page, text = "Imputed Assoc Graph")
        self.app.assocnotebook.select(self.app.imputed_page)
        
        self.imputed_button.state(["disabled"])
        
    def make_qq_page(self):
        
        self.app.qq_page = gp.GraphPage(master = self.app, results = self.results,
                                    plot_type = "qq")
        self.app.qq_page.grid(column = 0, row = 1)
        
        self.app.assocnotebook.add(self.app.qq_page, text = f"QQ - Plot")
        self.app.assocnotebook.select(self.app.qq_page)
        
        self.qqplot_button.state(["disabled"])
        
    def make_single_chr_page(self):
        
        if self.plot_type == "imputed":
            self.single_chr_page = gp.GraphPage(master = self.app, results = self.results,
                                    plot_type = "single_chr_imputed")
        else:
            self.single_chr_page = gp.GraphPage(master = self.app,
                                            results = self.results,
                                            plot_type = "single_chr")
                                            
        self.single_chr_page.grid(column = 0, row = 1)
        
        chrom = self.single_chr_page.chrom
        if self.plot_type == "imputed":
            self.app.assocnotebook.add(self.single_chr_page,
                                text = f"Chr {chrom} Plot (Imputed)")
        else:
            self.app.assocnotebook.add(self.single_chr_page,
                                text = f"Chr {chrom} Plot")
                                
        self.app.assocnotebook.select(self.single_chr_page)
        
    def text_options(self, bbox):
        x = bbox[0]
        y = bbox[3] + 10
        
        textframe_title = ttk.Label(self.canvas,
                                   text = "Text Options",
                                    style = "Optheadlabel.TLabel")
        self.text_options_frame = ttk.LabelFrame(self.canvas,
                                                labelwidget = textframe_title,
                                                padding = 10,
                                                style = "Optpane.TLabelframe")
        text_pane = self.canvas.create_window(
                                            x, y, anchor = tk.NW,
                                            window = self.text_options_frame
                                            )
        
        self.title_entry_label = ttk.Label(self.text_options_frame,
                                        text = "Enter / Change Title:\n" + 
                                        "(then hit return to update)",
                                        style = "Optlabel.TLabel")
        self.title_entry_label.grid(column = 0, row = 0, sticky = tk.W,
                                    padx = 5)
        
        self.current_title = tk.StringVar()
        self.current_title.set(str(self.master.graph.get_title()))
        self.title_entry = ttk.Entry(self.text_options_frame,
                                    textvariable = self.current_title,
                                    width = 45)
        self.title_entry.bind("<KeyPress-Return>", self.update_title)
        self.title_entry.grid(column = 0, row = 1, sticky = tk.W,
                                columnspan = 2, padx = 5)
        
        self.xlabel_label = ttk.Label(self.text_options_frame,
                                    style = "Optlabel.TLabel",
                                    text = "X Label:")
        self.xlabel_label.grid(column = 0, row = 2, sticky = tk.W, padx = 5)
        
        self.current_xlabel = tk.StringVar()
        self.current_xlabel.set(self.master.graph.get_xlabel())
        self.xlabel_entry = ttk.Entry(self.text_options_frame,
                                    textvariable = self.current_xlabel,
                                    width = 20)
        self.xlabel_entry.bind("<KeyPress-Return>", self.update_xlabel)
        self.xlabel_entry.grid(column = 0, row = 3, sticky = tk.W, padx = 5)
        
        self.ylabel_label = ttk.Label(self.text_options_frame,
                                    style = "Optlabel.TLabel",
                                    text = "Y Label:")
        self.ylabel_label.grid(column = 1, row = 2, sticky = tk.W, padx = 5)
        
        self.current_ylabel = tk.StringVar()
        self.current_ylabel.set(self.master.graph.get_ylabel())
        self.ylabel_entry = ttk.Entry(self.text_options_frame,
                                    textvariable = self.current_ylabel,
                                    width = 20)
        self.ylabel_entry.bind("<KeyPress-Return>", self.update_ylabel)
        self.ylabel_entry.grid(column = 1, row = 3, sticky = tk.W, padx = 5)
        
        if self.plot_type == "all_chr" or self.plot_type ==  "imputed":
            self.annotation_choice_label = ttk.Label(self.text_options_frame,
                                        style = "Optlabel.TLabel")
            self.annotation_choice_label["text"] = ("Number of top hit\n" +
                                                    "annotations:")
            self.annotation_choice_label.grid(column = 0, row = 6, sticky = tk.W,
                                        pady = (5, 0), padx = 5)
        
            label_options = list(range(0, 38))
            self.plot_label_value2 = tk.StringVar()
            current_n = self.results.n_annotations
            n_index = label_options.index(current_n)
            self.plot_label_value2.set(label_options[n_index])
            self.plot_label2 = ttk.Combobox(self.text_options_frame,
                                        textvariable = self.plot_label_value2,
                                        values = label_options,
                                        width = 4)
            self.plot_label2.state(["!disabled", "readonly"])
            self.plot_label2.grid(column = 0, row = 6, columnspan = 2, padx = 5,
                            pady = (5, 0))
            self.plot_label2.bind("<<ComboboxSelected>>", self.annotations)
        
        self.canvas.update_idletasks()
        text_bbox = self.canvas.bbox(text_pane)
        
        self.font_options(text_bbox)
        
    def update_text_options(self):
        
        self.current_title.set(str(self.master.graph.get_title()))
        self.current_xlabel.set(self.master.graph.get_xlabel())
        self.current_ylabel.set(self.master.graph.get_ylabel())
        t,x,y,xl,yl = self.get_text_sizes()
        self.chosen_titlesize.set(t)
        self.chosen_xsize.set(x)
        self.chosen_ysize.set(y)
        self.chosen_ylabelsize.set(yl)
        self.chosen_xlabelsize.set(xl)
        
    def font_options(self, bbox):
        
        fontx = bbox[0]
        fonty = bbox[3] + 10
        
        fontframe_title = ttk.Label(self.canvas,
                                    text = "Font Options",
                                    style = "Optheadlabel.TLabel")
        
        self.font_options_frame = ttk.LabelFrame(self.canvas,
                                                labelwidget = fontframe_title,
                                                padding = 10,
                                                style = "Optpane.TLabelframe")
        font_pane = self.canvas.create_window(
                                            fontx, fonty, anchor = tk.NW,
                                            window = self.font_options_frame
                                            )
        self.font_selected = False
        self.font_list = ["DejaVu Sans (Default)", "Arial", "Times New Roman",
                        "Courier New", "Verdana", "Tahoma", "Comic Sans MS",
                        "Calibri", "Bookman Old Style"]
        self.font_list.sort()
        self.chosen_font = tk.StringVar()
        self.chosen_font.set("DejaVu Sans (Default)")
        self.font_label = ttk.Label(self.font_options_frame,
                                    text = ("Graph Font:"),
                                        style = "Optlabel.TLabel")
        self.font_label.grid(column = 0, row = 0, columnspan = 2, padx = 5)
        self.font_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_font,
                                    values = self.font_list)
        self.font_box.grid(column = 0, row = 1, columnspan = 2)
        self.font_box.state(["readonly"])
        self.font_box.bind("<<ComboboxSelected>>", self.set_graph_font)
        
        self.font_size_values = list(range(0, 30))
        
        t,x,y,xl,yl = self.get_text_sizes()
        
        self.chosen_titlesize = tk.StringVar()
        self.chosen_titlesize.set(t)
        self.titlesize_label = ttk.Label(self.font_options_frame,
                                    text = "Title Font Size:",
                                    style = "Optlabel.TLabel")
        self.titlesize_label.grid(column = 0, row = 2, sticky = tk.W, padx = 5)
        self.titlesize_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_titlesize,
                                    values = self.font_size_values,
                                    width = 4)
        self.titlesize_box.grid(column = 0, row = 3)
        self.titlesize_box.state(["readonly"])
        self.titlesize_box.bind("<<ComboboxSelected>>", self.set_title_fontsize)
        
        self.chosen_xsize = tk.StringVar()
        self.chosen_xsize.set(x)
        self.xfontsize_label = ttk.Label(self.font_options_frame,
                                    text = "X Axis Font Size:",
                                    style = "Optlabel.TLabel")
        self.xfontsize_label.grid(column = 0, row = 4, sticky = tk.W, padx = 5)
        self.xfontsize_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_xsize,
                                    values = self.font_size_values,
                                    width = 4)
        self.xfontsize_box.grid(column = 0, row = 5)
        self.xfontsize_box.state(["readonly"])
        self.xfontsize_box.bind("<<ComboboxSelected>>", self.set_x_fontsize)
        
        self.chosen_ysize = tk.StringVar()
        self.chosen_ysize.set(y)
        self.yfontsize_label = ttk.Label(self.font_options_frame,
                                    text = "Y Axis Font Size:",
                                    style = "Optlabel.TLabel")
        self.yfontsize_label.grid(column = 1, row = 4, sticky = tk.W, padx = 5)
        self.yfontsize_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_ysize,
                                    values = self.font_size_values,
                                    width = 4)
        self.yfontsize_box.grid(column = 1, row = 5)
        self.yfontsize_box.state(["readonly"])
        self.yfontsize_box.bind("<<ComboboxSelected>>", self.set_y_fontsize)
        
        self.chosen_ylabelsize = tk.StringVar()
        self.chosen_ylabelsize.set(yl)
        self.ylabelfontsize_label = ttk.Label(self.font_options_frame,
                                    text = "Y Label Font Size:",
                                    style = "Optlabel.TLabel")
        self.ylabelfontsize_label.grid(column = 1, row = 6, sticky = tk.W,
                                        padx = 5)
        self.ylabelfontsize_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_ylabelsize,
                                    values = self.font_size_values,
                                    width = 4)
        self.ylabelfontsize_box.grid(column = 1, row = 7)
        self.ylabelfontsize_box.state(["readonly"])
        self.ylabelfontsize_box.bind("<<ComboboxSelected>>",
                                    self.set_ylabel_fontsize)
                                    
        self.chosen_xlabelsize = tk.StringVar()
        self.chosen_xlabelsize.set(xl)
        self.xlabelfontsize_label = ttk.Label(self.font_options_frame,
                                    text = "X Label Font Size:",
                                    style = "Optlabel.TLabel")
        self.xlabelfontsize_label.grid(column = 0, row = 6, sticky = tk.W,
                                        padx = 5)
        self.xlabelfontsize_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_xlabelsize,
                                    values = self.font_size_values,
                                    width = 4)
        self.xlabelfontsize_box.grid(column = 0, row = 7)
        self.xlabelfontsize_box.state(["readonly"])
        self.xlabelfontsize_box.bind("<<ComboboxSelected>>",
                                    self.set_xlabel_fontsize)
        if self.plot_type == "all_chr" or self.plot_type == "imputed":                            
            self.rotation_values = ["0", "45", "90"]
                                    
            self.chosen_xlabelrotation = tk.StringVar()
            self.chosen_xlabelrotation.set(self.rotation_values[0])
            self.xlabelrotation_label = ttk.Label(self.font_options_frame,
                                        text = "X Axis Rotation:",
                                        style = "Optlabel.TLabel")
            self.xlabelrotation_label.grid(column = 0, row = 8, sticky = tk.W,
                                        padx = 5)
            self.xlabelrotation_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_xlabelrotation,
                                    values = self.rotation_values,
                                    width = 4)
            self.xlabelrotation_box.grid(column = 0, row = 9)
            self.xlabelrotation_box.state(["readonly"])
            self.xlabelrotation_box.bind("<<ComboboxSelected>>",
                                    self.set_xticks_rotation)
            self.ann_rotated = False
            self.chosen_ann_rotation = tk.StringVar()
            self.chosen_ann_rotation.set(self.rotation_values[0])
            self.ann_rotation_label = ttk.Label(self.font_options_frame,
                                    text = "Annotation Rotation:",
                                    style = "Optlabel.TLabel")
            self.ann_rotation_label.grid(column = 1, row = 8, sticky = tk.W,
                                    padx = 5)
            self.ann_rotation_box = ttk.Combobox(self.font_options_frame,
                                    textvariable = self.chosen_ann_rotation,
                                    values = self.rotation_values,
                                    width = 4)
            self.ann_rotation_box.grid(column = 1, row = 9)
            self.ann_rotation_box.state(["readonly"])
            self.ann_rotation_box.bind("<<ComboboxSelected>>",
                                    self.set_ann_rotation)
        
        self.canvas.update_idletasks()
        font_bbox = self.canvas.bbox(font_pane)
        
        if self.plot_type == "qq":
            self.save_options(font_bbox)
        else:
            self.graph_plot_options(font_bbox)
        
    def graph_plot_options(self, bbox):
        
        fontx = bbox[0]
        fonty = bbox[3] + 10
        
        plotframe_title = ttk.Label(self.canvas,
                                    text = "Plot Options",
                                    style = "Optheadlabel.TLabel")
        
        self.plot_options_frame = ttk.LabelFrame(self.canvas,
                                                labelwidget = plotframe_title,
                                                padding = 10,
                                                style = "Optpane.TLabelframe")
        plot_pane = self.canvas.create_window(
                                            fontx, fonty, anchor = tk.NW,
                                            window = self.plot_options_frame
                                            )
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.graphtypelabel = ttk.Label(self.plot_options_frame,
                                        text = "Graph Colour Scheme:",
                                        style = "Optlabel.TLabel")
            self.graphtypelabel.grid(column = 0, row = 6, columnspan = 2,
                                    padx = 5)
        
            self.graphtypes = ["Default range of colours", "Custom two colours"]
            self.graphtype = tk.StringVar()
            self.graphtype.set(self.graphtypes[0])
            self.plot_colour_type = ttk.Combobox(self.plot_options_frame,
                                            textvariable = self.graphtype,
                                            values = self.graphtypes,
                                            width = 25)
            self.plot_colour_type.grid(column = 0, row = 7, columnspan = 2,
                                        padx = 5)
            self.plot_colour_type.bind("<<ComboboxSelected>>",
                                        self.select_graph_type)
            self.plot_colour_type.state(["readonly"])
        
            self.colour_choice_label = ttk.Label(self.plot_options_frame,
                                            style = "Optlabel.TLabel")
            self.colour_choice_label["text"] = ("Choose the two colours to be "
                                        "used on the graph.\n"
                                        "'tab:' indicates colour is one of the"
                                        " 10 used as default")
            self.colour_choice_label.grid(column = 0, row = 8, columnspan = 2,
                                        sticky = tk.W, padx = 5)
            self.colour_choice_label.state(["disabled"])
        
        colour_names = self.get_colour_list()
        
        self.firstcolourlabel = ttk.Label(self.plot_options_frame,
                                        style = "Optlabel.TLabel")
                                        
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.firstcolourlabel["text"] = "Colour 1:"
            self.firstcolourlabel.state(["disabled"])
        else:
            self.firstcolourlabel["text"] = "Graph Colour:"
            
        self.firstcolourlabel.grid(column = 0, row = 9, sticky = tk.W, padx = 5)
        self.first_color = tk.StringVar()
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.first_color.set(colour_names[0])
        else:
            self.first_color.set(colour_names[6])
        self.first_colours_box = ttk.Combobox(self.plot_options_frame,
                                    textvariable = self.first_color,
                                    values = colour_names)
        self.first_colours_box.grid(column = 0, row = 10, padx = 5)
        
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.first_colours_box.state(["readonly", "disabled"])
            self.first_colours_box.bind("<<ComboboxSelected>>",
                                        self.graph_twotone)
        else:
            self.first_colours_box.state(["readonly"])
            self.first_colours_box.bind("<<ComboboxSelected>>",
                                        self.single_chr_colour)
        
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            self.secondcolourlabel = ttk.Label(self.plot_options_frame,
                                            text = "Colour 2:",
                                            style = "Optlabel.TLabel")
            self.secondcolourlabel.state(["disabled"])
            self.secondcolourlabel.grid(column = 1, row = 9, sticky = tk.W,
                                        padx = 5)
            self.second_color = tk.StringVar()
            self.second_color.set(colour_names[5])
            self.second_colours_box = ttk.Combobox(self.plot_options_frame,
                                        textvariable = self.second_color,
                                        values = colour_names)
            self.second_colours_box.grid(column = 1, row = 10, padx = 5)
            self.second_colours_box.state(["readonly", "disabled"])
            self.second_colours_box.bind("<<ComboboxSelected>>",
                                        self.graph_twotone)
            self.colour_selection_on = False
        
        line_colour_names = self.get_colour_list()
        self.line_colour = tk.StringVar()
        self.line_colour.set(line_colour_names[0])
        
        line_style_names = ["solid", "dashed", "dashdot", "dotted"]
        self.line_style = tk.StringVar()
        self.line_style.set(line_style_names[3])
        
        self.bonfline = ""
        bonf_options = ["Off", "On"]
        self.bonflabel = ttk.Label(self.plot_options_frame,
                                        text = "Plot Bonferonni Line:",
                                        style = "Optlabel.TLabel")
        self.bonflabel.grid(column = 0, row = 11, sticky = tk.W, padx = 5)
        self.bonf_var = tk.StringVar()
        self.bonf_var.set(bonf_options[0])
        self.bonf_box = ttk.Combobox(self.plot_options_frame,
                                    textvariable = self.bonf_var,
                                    values = bonf_options)
        self.bonf_box.grid(column = 0, row = 12, padx = 5)
        self.bonf_box.state(["readonly"])
        self.bonf_box.bind("<<ComboboxSelected>>", self.plot_bonferonni_line)
        
        self.linecolourlabel = ttk.Label(self.plot_options_frame,
                                        text = "Line Colour:",
                                        style = "Optlabel.TLabel")
        self.linecolourlabel.state(["disabled"])
        self.linecolourlabel.grid(column = 0, row = 13, sticky = tk.W, padx = 5)

        self.line_colours_box = ttk.Combobox(self.plot_options_frame,
                                    textvariable = self.line_colour,
                                    values = line_colour_names)
        self.line_colours_box.grid(column = 0, row = 14, padx = 5)
        self.line_colours_box.state(["readonly", "disabled"])
        self.line_colours_box.bind("<<ComboboxSelected>>",
                                    self.set_line_colour)
                                    
        self.linestylelabel = ttk.Label(self.plot_options_frame,
                                        text = "Line Style:",
                                        style = "Optlabel.TLabel")
        self.linestylelabel.state(["disabled"])
        self.linestylelabel.grid(column = 1, row = 13, sticky = tk.W, padx = 5)

        self.line_style_box = ttk.Combobox(self.plot_options_frame,
                                    textvariable = self.line_style,
                                    values = line_style_names)
        self.line_style_box.grid(column = 1, row = 14, padx = 5)
        self.line_style_box.state(["readonly", "disabled"])
        self.line_style_box.bind("<<ComboboxSelected>>",
                                    self.set_line_style)
                                    
        self.chosen_margin = tk.StringVar()
        self.chosen_margin.set("1")
        self.margin_label = ttk.Label(self.plot_options_frame,
                                    text = "Graph X margin:"
                                            " (the 'padding' either side)",
                                    style = "Optlabel.TLabel")
        self.margin_label.grid(column = 0, row = 19, sticky = tk.W, padx = 5,
                                columnspan = 2)
        self.margin_box = ttk.Entry(self.plot_options_frame,
                                    textvariable = self.chosen_margin,
                                    width = 4)
        self.margin_box.grid(column = 0, row = 20, sticky = tk.W, padx = 5)
        self.margin_box.state(["readonly"])
        
        self.margins_set = False
        self.chosen_margin_float = tk.DoubleVar()
        self.chosen_margin_float.set(1.00)
        self.margin_scale = ttk.Scale(self.plot_options_frame,
                                    from_ = 0.00, to = 1.00, value = 1.00,
                                    cursor = "hand2",
                                    command = self.set_margin_xlim_method,
                                    variable = self.chosen_margin_float,
                                    style = "Optscrol.Horizontal.TScale")
        self.margin_scale.grid(column = 0, row = 20, columnspan = 2, padx = 5)
        
        self.canvas.update_idletasks()
        plot_bbox = self.canvas.bbox(plot_pane)
        
        self.save_options(plot_bbox)
        
    def save_options(self, bbox):
        
        fontx = bbox[0]
        fonty = bbox[3] + 10
        
        saveframe_title = ttk.Label(self.canvas,
                                    text = "Save Options",
                                    style = "Optheadlabel.TLabel")
        
        self.save_options_frame = ttk.LabelFrame(self.canvas,
                                                labelwidget = saveframe_title,
                                                padding = 10,
                                                style = "Optpane.TLabelframe")
        save_pane = self.canvas.create_window(
                                            fontx, fonty, anchor = tk.NW,
                                            window = self.save_options_frame
                                            )
        
        self.dpichoicelabel = ttk.Label(self.save_options_frame,
                                        text = "High Resolution Save Option: "
                                            "\n(dpi)",
                                        style = "Optlabel.TLabel")
        self.dpichoicelabel.grid(column = 0, row = 0, sticky = tk.W, padx = 5)
        self.dpi_list = ["300", "600"]
        self.dpi_value = tk.StringVar()
        self.dpi_value.set(self.dpi_list[1])
        self.dpi_choice = ttk.Combobox(self.save_options_frame,
                                        textvariable = self.dpi_value,
                                        values = self.dpi_list)
        self.dpi_choice.grid(column = 0, row = 1, sticky = tk.W, padx = 5)
        self.dpi_choice.state(["readonly"])
        self.dpi_choice.bind("<<ComboboxSelected>>", self.dpi_select)
        
        self.master.toolbar.inputdpi = self.dpi_value.get()
        self.canvas.update_idletasks()

        
    def dpi_select(self, event):
        self.toolbar.inputdpi = self.dpi_value.get()
        
    def update_title(self, event):
        self.master.graph.set_title(self.current_title.get())
        self.fig_canvas.draw()
        
    def update_xlabel(self, event):
        self.master.graph.set_xlabel(self.current_xlabel.get())
        self.fig_canvas.draw()
        
    def update_ylabel(self, event):
        self.master.graph.set_ylabel(self.current_ylabel.get())
        self.fig_canvas.draw()
        
    def select_graph_type(self, event):
        
        if self.graphtype.get() == "Default range of colours":
            self.graph_default()
        elif self.graphtype.get() == "Custom two colours":
            self.two_colour_selection()
    
    def two_colour_selection(self):
        self.colour_choice_label.state(["!disabled"])
        self.first_colours_box.state(["readonly", "!disabled"])
        self.firstcolourlabel.state(["!disabled"])
        self.second_colours_box.state(["readonly", "!disabled"])
        self.secondcolourlabel.state(["!disabled"])
        self.graph_twotone()
        self.colour_selection_on = True
        
    def annotations(self, event):
        self.results.n_annotations = int(self.plot_label_value2.get())
        self.results = add_remove_annotations(self.results,
                                            graph_type = self.plot_type)
        if self.font_selected:
            self.set_graph_font()
        if self.ann_rotated:
            self.set_ann_rotation()
        self.app.table_page.update_checkbuttons()
        
        self.fig_canvas.draw()
        
    def graph_twotone(self, event = None):
        c1 = self.first_color.get()
        c2 = self.second_color.get()
        c = [c1, c2]
        if self.plot_type == "all_chr":
            n = 1
            for series in self.results.series_list:
                series.set_color(c[n % 2])
                n += 1
        if self.plot_type == "imputed":
            n = 1
            for series in self.results.gen_series_list:
                series.set_color(c[n % 2])
                n += 1
            n = 1
            for series in self.results.imp_series_list:
                series.set_edgecolor(c[n % 2])
                n += 1
        
        self.fig_canvas.draw()
        
    def single_chr_colour(self, event = None):
        c = self.first_color.get()
        if self.plot_type == "single_chr_imputed":
            self.master.series["genotyped"].set_color(c)
            self.master.series["imputed"].set_edgecolor(c)
        else:
            self.master.series.set_color(c)
        self.fig_canvas.draw()
        
    def graph_default(self):
        
        if self.colour_selection_on:
            self.colour_choice_label.state(["disabled"])
            self.first_colours_box.state(["readonly", "disabled"])
            self.firstcolourlabel.state(["disabled"])
            self.second_colours_box.state(["readonly", "disabled"])
            self.secondcolourlabel.state(["disabled"])
            self.colour_selection_on = False
        
        if self.plot_type == "all_chr":
            n = 0
            for series in self.results.series_list:
                series.set_color(f"C{n % 10}")
                n += 1
        elif self.plot_type == "imputed":
            n = 0
            for series in self.results.gen_series_list:
                series.set_color(f"C{n % 10}")
                n += 1
            n = 0
            for series in self.results.imp_series_list:
                series.set_edgecolor(f"C{n % 10}")
                n += 1
        self.fig_canvas.draw()
        
    def get_colour_list(self):
        tabcolors = mcolors.TABLEAU_COLORS
        by_hsv_tab = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                         name)
                        for name, color in tabcolors.items())
        tabnames = [name for hsv, name in by_hsv_tab]
        
        csscolors = mcolors.CSS4_COLORS
        by_hsv_css = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color))),
                         name)
                        for name, color in csscolors.items())
        cssnames = [name for hsv, name in by_hsv_css]
        
        names = []
        
        for name in tabnames:
            names.append(name)
        for name in cssnames:
            names.append(name)
            
        return names
        
    def plot_bonferonni_line(self, event = None):
        
        if self.margins_set == False:
            self.set_min_max_x()
        
        if self.bonf_var.get() == "On":
            bonferonni = math.log10(0.05 / len(self.results.data)) * -1
            xleft, xright = self.master.graph.get_xlim()
            line_colour = self.line_colour.get()
            line_style = self.line_style.get()
            self.bonfline = self.master.graph.plot([0, self.xright_min],
                                                    [bonferonni, bonferonni],
                                                    linestyle = line_style,
                                                    color = line_colour)
            self.master.graph.set_xlim(xleft, xright)
            self.linecolourlabel.state(["!disabled"])
            self.line_colours_box.state(["readonly", "!disabled"])
            self.linestylelabel.state(["!disabled"])
            self.line_style_box.state(["readonly", "!disabled"])
        elif self.bonf_var.get() == "Off" and self.bonfline:
            self.bonfline.pop(0).remove()
            del self.bonfline
            self.linecolourlabel.state(["disabled"])
            self.line_colours_box.state(["readonly", "disabled"])
            self.linestylelabel.state(["disabled"])
            self.line_style_box.state(["readonly", "disabled"])
            
        self.fig_canvas.draw()
        
    def set_line_colour(self, event):
        line_colour = self.line_colour.get()
        for line in self.bonfline:
            line.set_color(line_colour)
        self.fig_canvas.draw()
        
    def set_line_style(self, event):
        line_style = self.line_style.get()
        for line in self.bonfline:
            line.set_linestyle(line_style)
        self.fig_canvas.draw()
        
    def set_graph_font(self, event = None):
        font_choice = {"fontname" : self.chosen_font.get()}
        if font_choice["fontname"] == "DejaVu Sans (Default)":
            font_choice["fontname"] = "DejaVu Sans"
        self.master.graph.title.set_fontname(font_choice["fontname"])
        ylabel = self.master.graph.get_ylabel()
        self.master.graph.set_ylabel(ylabel, **font_choice)
        yticks = self.master.graph.get_yticklabels()
        for l in yticks:
            l.set_fontname(font_choice["fontname"])
        xticks = self.master.graph.get_xticklabels()
        self.master.graph.set_xticklabels(xticks, **font_choice)
        xlabel = self.master.graph.get_xlabel()
        self.master.graph.set_xlabel(xlabel, **font_choice)
        if self.results.ann_list:
            for ann in self.results.ann_list:
                ann.set_fontname(font_choice["fontname"])
                
        self.font_selected = True
        
        self.fig_canvas.draw()
        
    def set_x_fontsize(self, event = None):
        fontsize = int(self.chosen_xsize.get())
        xticks = self.master.graph.get_xticklabels()
        self.master.graph.set_xticklabels(xticks,
                                                size = fontsize)
        
        self.fig_canvas.draw()
        
    def set_y_fontsize(self, event = None):
        fontsize = int(self.chosen_ysize.get())
        ylabels = self.master.graph.get_yticklabels()
        
        for l in ylabels:
            l.set_size(fontsize)
                                                
        self.fig_canvas.draw()
        
    def set_ylabel_fontsize(self, event = None):
        fontsize = int(self.chosen_ylabelsize.get())
        ylabel = self.master.graph.get_ylabel()
        self.master.graph.set_ylabel(ylabel, size = fontsize)

        self.fig_canvas.draw()
        
    def set_xlabel_fontsize(self, event = None):
        fontsize = int(self.chosen_xlabelsize.get())
        xlabel = self.master.graph.get_xlabel()
        self.master.graph.set_xlabel(xlabel, size = fontsize)

        self.fig_canvas.draw()
        
    def set_title_fontsize(self, event = None):
        fontsize = int(self.chosen_titlesize.get())
        self.master.graph.title.set_size(fontsize)
        
        self.fig_canvas.draw()
        
    def set_xticks_rotation(self, event):
        input_rotation = int(self.chosen_xlabelrotation.get())
        xlabels = self.master.graph.get_xticklabels()
        self.master.graph.set_xticklabels(xlabels,
                                                rotation = input_rotation)

        self.fig_canvas.draw()
        
    def set_ann_rotation(self, event = None):
        input_rotation = int(self.chosen_ann_rotation.get())
        ann_list = self.results.ann_list
        for ann in ann_list:
            ann.set_rotation(input_rotation)
            
        self.ann_rotated = True

        self.fig_canvas.draw()
        
    def set_margin_xlim_method(self, v):
        
        if self.margins_set == False:
            self.set_min_max_x()
        
        new_margin = float("{:.2f}".format(float(v)))
        self.chosen_margin_float.set(new_margin)
        self.chosen_margin.set(new_margin)
        
        newleft = self.xleft_margin * new_margin
        newright = self.xright_min + (self.xright_margin * new_margin)
        
        self.master.graph.set_xlim(newleft, newright)
        
        self.master.toolbar.update()
        self.fig_canvas.draw()
        
    def set_min_max_x(self):
        #get start xlim, with the standard margin
        xleft_max, xright_max = self.master.graph.get_xlim()
        # same margin either side. plot starts at 0, so left will be negative
        self.xleft_margin = xleft_max
        self.xright_margin = xleft_max * -1
        self.margins_set = True
        # calculate where the plot ends on x for the minimum x right margin
        self.xright_min = xright_max - self.xright_margin
        
    def get_text_sizes(self):
        ylabel = self.master.graph.yaxis.get_label().get_size()
        xlabel = self.master.graph.xaxis.get_label().get_size()
        title = self.master.graph.title.get_size()
        xticks = self.master.graph.get_xticklabels()
        xsize = xticks[0].get_size()
        yticks = self.master.graph.get_yticklabels()
        ysize = yticks[0].get_size()
        return  (round(title), round(xsize), round(ysize), round(xlabel),
               round(ylabel))
