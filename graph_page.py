from tkinter import ttk
import tkinter as tk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                            NavigationToolbar2Tk) 
                                            
import threading
                                            
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
            self.plot_single_chr_imputed(1)
        elif plot_type == "qq":
            self.plot_qq()
            
        self.init_toolbar()
        self.init_option_pane()
        
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
        self.canvas.draw() 
        
        self.canvas.get_tk_widget().pack()
        
    def plot_imputed(self):
        self.canvas = FigureCanvasTkAgg(self.results.imp_fig, 
                                        master = self.results_frame)
        self.graph = self.results.imp_graph
        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
        
    def plot_single_chr(self):
        
        self.chrom = 1
        
        fig, graph, series = plot_single_chr(self.results, self.chrom)
        
        self.canvas = FigureCanvasTkAgg(fig, master = self.results_frame)
        
        self.graph = graph
        self.series = series
        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
        
    def plot_single_chr_imputed(self, chrom, plot = "initial"):
        
        self.chrom = int(chrom)

        fig = Figure(figsize = [9, 5])
        graph = fig.add_subplot()
    
        gen_series = graph.scatter(self.results.gen_chr_snpbp[self.chrom],
                                    self.results.gen_chr_snplogp[self.chrom],
                                    5,
                                    color = f"C{(self.chrom - 1)}")
        imp_series = graph.scatter(self.results.imp_chr_snpbp[self.chrom],
                                    self.results.imp_chr_snplogp[self.chrom],
                                    10,
                                    marker = "^",
                                    facecolors = "none",
                                    edgecolors = f"C{(self.chrom - 1)}",
                                    linewidths = 0.8)
        
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
        
        self.canvas.draw()
        
        self.canvas.get_tk_widget().pack()
        
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
        self.graph_option_pane.grid(column = 1, row = 0, sticky = tk.NS)
