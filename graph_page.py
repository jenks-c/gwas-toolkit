from tkinter import ttk
import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                            NavigationToolbar2Tk) 
                                            
import threading

from numpy.lib.function_base import _update_dim_sizes
                                            
from custom_toolbar import CustomToolbar
from graph_option_pane import GraphOptionPane

from GWAS_toolkit_functions import *

class GraphPage(ttk.Frame):
    def __init__(self, master, results, plot_type):
        
        super().__init__(master)
        
        self["padding"] = 10
        self["style"] = "wframe.TFrame"
        
        self.results = results

        self.master = master
        self.plot_type = plot_type
        
        if self.plot_type == "imputed":
            self.app = self.master.app
        else:
            self.app = self.master
        
        self.results_frame = ttk.Frame(self, style = "wframe.TFrame")
        self.results_frame.grid(column = 0, row = 0)
        
        if plot_type == "all_chr":
            self.plot_all()
        elif plot_type == "imputed":
            self.plot_imputed()
        elif plot_type == "single_chr":
            self.plot_single_chr()
        elif plot_type == "single_chr_imputed":
            chroms = sorted(list(self.results.chromset))
            chrom = chroms[0]
            self.plot_single_chr_imputed(chrom)
        elif plot_type == "qq":
            self.plot_qq()
            
        self.init_toolbar()
        self.init_option_pane()
        if plot_type != "qq":
            self.init_click_canvas()

    def init_click_canvas(self):

        self.click_canvas = tk.Canvas(self, bg = "white", height = 34, width = 450,
                                        borderwidth = 0, highlightthickness = 0)
        self.click_canvas.grid(column = 0, row = 0, sticky = tk.SE, padx = 150, pady = 3)

        self.txt = self.click_canvas.create_text(2, 10, anchor = tk.NW)
        self.click_canvas.itemconfig(self.txt, text = "Click SNP Point For Info", font = ("courier", 10, "bold"))

        self.click_clear_button = ttk.Button(self, style = "wbutton.TButton", text = "Clear",
                                            command = self.click_clear,
                                            width=6)
        self.bwindow = self.click_canvas.create_window(397, 2, anchor = tk.NW, window = self.click_clear_button)

        self.last_clicked = ""

        self.click_canvas.update_idletasks()
        
    def plot_qq(self):
        
        self.canvas = FigureCanvasTkAgg(self.results.qq_fig, 
                                        master = self.results_frame)
                                        
        self.graph = self.results.qq_graph
        self.canvas.draw() 
        
        self.canvas.get_tk_widget().pack()
        
        x = threading.Thread(target=self.get_qq_results)
        x.start()
        
        self.app.progress.grid(column = 0, row = 5, pady = 5,
                            padx = 10, sticky = tk.W + tk.E)
        self.app.progress["mode"] = "indeterminate"
        self.app.progress.start(200)
        
        self.app.progresslabel["text"] = ("Plotting Quantile Quantile Plot")
        self.app.progresslabel.grid(column = 0, row = 4, columnspan = 2, pady = 5)
                            
        self.app.quit.grid(column = 0, row = 4, pady = (5,0), columnspan = 1,
                        sticky = tk.E, padx = 10)
        
        self.app.progress.update_idletasks()
        
    def get_qq_results(self):
        
        #make_qq_plot(self.results)
        make_qq_plot_pval(self.results)
        self.canvas.draw_idle()
        self.graph_option_pane.update_text_options()
        
        self.app.progress.grid_remove()
        self.app.progresslabel.grid_remove()
        
        self.app.quit.grid(column = 0, row = 6, pady = 5, columnspan = 2,
                        sticky = tk.N)
        
    def plot_all(self):

        self.canvas = FigureCanvasTkAgg(self.results.fig, 
                                        master = self.results_frame)
        self.graph = self.results.graph

        self.highlight_point = []
        self.results.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.draw() 
        
        self.canvas.get_tk_widget().pack()
        
    def plot_imputed(self):
        self.canvas = FigureCanvasTkAgg(self.results.imp_fig, 
                                        master = self.results_frame)
        self.graph = self.results.imp_graph
        self.highlight_point = []
        self.results.imp_fig.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
        
    def plot_single_chr(self):
        
        chroms = sorted(list(self.results.chromset))
        self.chrom = chroms[0]
        
        fig, graph, series = plot_single_chr(self.results, self.chrom)
        
        self.canvas = FigureCanvasTkAgg(fig, master = self.results_frame)

        self.graph = graph
        self.series = series
        self.fig = fig
        self.highlight_point = []
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
        
    def plot_single_chr_imputed(self, chrom, plot = "initial"):
        
        self.chrom = int(chrom)

        fig = Figure(figsize = [9, 5])
        graph = fig.add_subplot()
    
        gen_series = graph.scatter(self.results.gen_chr_snpbp[self.chrom],
                                    self.results.gen_chr_snplogp[self.chrom],
                                    5,
                                    color = f"C{(self.chrom - 1)}",
                                    picker = True)
        imp_series = graph.scatter(self.results.imp_chr_snpbp[self.chrom],
                                    self.results.imp_chr_snplogp[self.chrom],
                                    10,
                                    marker = "^",
                                    facecolors = "none",
                                    edgecolors = f"C{(self.chrom - 1)}",
                                    linewidths = 0.8,
                                    picker = True)
        
        self.series = {"genotyped" : gen_series, "imputed" : imp_series}
    
        plottitle = f"Chromosome {self.chrom} Association Plot (Imputed)"

        graph.set_xlabel("Position (bp)")
        graph.ticklabel_format(axis = "x", useOffset=False, style = "plain")
        graph.set_ylabel("-log10 p-value")
        graph.set_ylim(bottom = 0)
        graph.set_title(plottitle)
        ybottom, ytop = graph.get_ylim()
        ytop = math.ceil(ytop)
        graph.set_ylim(bottom = 0, top = ytop)
                
        graph.spines['right'].set_visible(False)
        graph.spines['top'].set_visible(False)
        
        if plot == "initial":
            self.canvas = FigureCanvasTkAgg(fig, master = self.results_frame)
        else:
            self.canvas.figure = fig
            
        self.graph = graph
        self.fig = fig

        self.highlight_point = []
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
    
    def click_clear(self, event = None):

        if self.highlight_point:
            for point in self.highlight_point:
                point.remove()
        
            self.highlight_point = []

            self.last_clicked = ""
            self.click_canvas.itemconfig(self.txt, text = "Click SNP Point For Info", font = ("courier", 10, "bold"))

        self.canvas.draw_idle()
        self.click_canvas.update_idletasks()

    def onpick(self, event):
        
        if self.plot_type == "all_chr" or self.plot_type == "imputed":
            dic = self.results.relgenpos_dic
        elif self.plot_type == "single_chr" or self.plot_type == "single_chr_imputed":
            dic = self.results.pos_dic

        thisline = event.artist
        self.data = thisline.get_offsets()
        ind = event.ind
        points = self.data[ind]
        pos = int(points[0][0])

        if self.plot_type == "single_chr" or self.plot_type == "single_chr_imputed":
            pos = f"{self.chrom}:{pos}"

        snp = dic[pos][0]
        
        if self.last_clicked == snp:
            for point in self.highlight_point:
                point.remove()
            self.highlight_point =[]
            self.last_clicked = ""
            self.click_canvas.itemconfig(self.txt, text = "Click SNP Point For Info", font = ("courier", 10, "bold"))
        
        else:
            self.last_clicked = snp
            bp = dic[pos][1]
            logp = "{:.2f}".format(points[0][1])
            chrom = dic[pos][2]
            snp_info = f"SNP: {snp}, Chr{chrom}:{bp}, -log10 p: {logp}"

            self.click_canvas.itemconfig(self.txt, text = snp_info, font = ("courier", 10, "bold"))
        
            if self.highlight_point:
                for point in self.highlight_point:
                    point.remove()
        
            self.highlight_point = []
            point = self.graph.scatter(
                            points[0][0],
                            points[0][1],
                            10,
                            marker = "o",
                            facecolors = "none",
                            edgecolors = "black",
                            linewidths = 1.5)
        
            self.highlight_point.append(point)

        self.canvas.draw_idle()
        self.click_canvas.update_idletasks()
        

    def init_toolbar(self):
  
        self.toolbar = CustomToolbar(self.canvas, 
                                   self.results_frame)
        self.toolbar.config(background = "teal")
        self.toolbar._message_label.config(background = "teal")
        self.toolbar.update() 
  
        self.canvas.get_tk_widget().pack()
        
    def init_option_pane(self):
        
        self.graph_option_pane = GraphOptionPane(master = self,
                                                app = self.app,
                                                results = self.results,
                                                canvas = self.canvas,
                                                plot_type = self.plot_type)
        self.graph_option_pane.grid(column = 1, row = 0, rowspan = 2, sticky = tk.NS)
