from tkinter import ttk
import tkinter as tk

import threading

from GWAS_toolkit_functions import *
import graph_page as gp

class ImputedDataGraphPage(ttk.Frame):
    def __init__(self, master, results):
        
        super().__init__(master)
        
        self["padding"] = 10
        self["style"] = "wframe.TFrame"
        
        self.results = results
        self.master = master
        self.app = master
        
        self.inputframe = ttk.Frame(self, style = "wframe.TFrame")
        self.inputframe.grid(column = 0, row = 0)
        
        self.entertextlabel = ttk.Label(self.inputframe,
                                        style = "wlabel.TLabel")
        self.entertextlabel["text"] = ("A file containing a column of SNP IDs"
                                        " and a column indicating if each is "
                                        "imputed \n(1 = imputed, 0 = genotyped)"
                                        " is needed (no headers).\n\n"
                                        "Click browse to pick file:")
        self.entertextlabel.grid(column = 0, row = 1, padx = 5, sticky = tk.W)
        
        self.enter_text = ttk.Entry(self.inputframe, width = 75)
        self.enter_text.insert(0, "")
        self.enter_text.grid(column = 0, row = 2, padx = 5, sticky = tk.W)
        self.enter_text.state(["!disabled", "readonly"])
        
        self.browse = ttk.Button(self.inputframe, style = "wbutton.TButton")
        self.browse["text"] = "Browse Files"
        self.browse["command"] = self.pick_file
        self.browse.grid(column = 1, row = 2, padx = 5)
        
        self.go_button = ttk.Button(self.inputframe, style = "wbutton.TButton",
                                    text = "Plot Graph",
                                    command = self.check_data_and_status_file)
        self.go_button.grid(column = 0, row = 4, pady = 5)
        self.go_button.state(["disabled"])
        
    def check_data_and_status_file(self):
        
        file_location = self.enter_text.get()
        self.snp_impute_status = []
        
        with open(file_location) as fobj:
            for line in fobj:
                snp_status = line.strip().split()
                self.snp_impute_status.append(snp_status)
                
        if len(self.snp_impute_status) == len(self.results.assoclist):
            self.plot_imputed_data()
        else:
            self.incorrect_status_file()
            
    def incorrect_status_file(self):
        self.file_length_warning = ttk.Label(self.inputframe,
                                            foreground = "red",
                                            background = "white")
        self.file_length_warning["text"] = ("File does not match data\n"
                                            "status file lenght: "
                                            f"{len(self.snp_impute_status)}, "
                                            "SNPs in data: "
                                            f"{len(self.results.assoclist)}")
        self.file_length_warning.grid(column = 0, row = 3, pady = 5)
        
    def plot_imputed_data(self):
        
        self.inputframe.grid_remove()
        self.split_gen_imp_data()
        
        
        self.master.progress = ttk.Progressbar(self.master, mode = "determinate",
                                        style = "green.Horizontal.TProgressbar")
        self.master.progress.grid(column = 0, row = 5, pady = 5,
                            padx = 10, sticky = tk.W + tk.E)
                            
        self.master.quit.grid(column = 0, row = 4, pady = (5,0), columnspan = 1,
                        sticky = tk.E, padx = 10)
        
        self.master.progress.update_idletasks()
        self.master.progress["maximum"] = len(self.results.chromset) + 0.001
        
        x = threading.Thread(target=self.plot_imp_chr, daemon = True)
        x.start()
        
        self["padding"] = 0
        self.imp_graph = gp.GraphPage(master = self,
                                    results = self.results,
                                    plot_type = "imputed")
        self.imp_graph.grid(column = 0, row = 0)
        
    def split_gen_imp_data(self):
        
        self.status_dictionary = {}
        for snp in self.snp_impute_status:
            self.status_dictionary[snp[0]] = snp[1]
        
        self.results.imputed_graph()
        
        missing = 0
        imputed = 0
        genotyped = 0
        for snp in self.results.assoclist:
            headers = self.results.assocheader
            snp_id = snp[headers["snp"]]
            chrom = snp[headers["chrom"]]
            logp = snp[headers["logp"]]
            bp = snp[headers["bp"]]
            bp_adjusted = snp[headers["shiftpos"]]
            if self.status_dictionary[snp_id] == "0":
                self.results.gen_chr_snplogp[chrom].append(logp)
                self.results.gen_chr_snpbp[chrom].append(bp)
                self.results.gen_chr_relgenpos[chrom].append(bp_adjusted)
                genotyped += 1
            elif self.status_dictionary[snp_id] == "1":
                self.results.imp_chr_snplogp[chrom].append(logp)
                self.results.imp_chr_snpbp[chrom].append(bp)
                self.results.imp_chr_relgenpos[chrom].append(bp_adjusted)
                imputed += 1
            else:
                missing += 1
        print(f"There are {missing} snps missing imputation status"
                f"\nImputed: {imputed} \nGenotyped: {genotyped}")
                
    def plot_imp_chr(self):
        
        for chrom in self.results.chromset:
            
            print(f"Plotting: chr{chrom} genotyped SNPs")
            gen_series = self.results.imp_graph.scatter(
                                    self.results.gen_chr_relgenpos[chrom],
                                    self.results.gen_chr_snplogp[chrom],
                                    3,
                                    label = chrom)
            self.results.gen_series_list.append(gen_series)
        
            print(f"Plotting: chr{chrom} imputed SNPs")
            imp_series = self.results.imp_graph.scatter(
                                    self.results.imp_chr_relgenpos[chrom],
                                    self.results.imp_chr_snplogp[chrom],
                                    8,
                                    label = chrom,
                                    marker = "^",
                                    facecolors = "none",
                                    edgecolors = f"C{(chrom - 1) % 10}",
                                    linewidths = 0.5)
            self.results.imp_series_list.append(imp_series)
            
            self.master.progress.step()
            self.master.progress.update_idletasks()
            
        self.master.progress.grid_remove()
        
        self.master.quit.grid(column = 0, row = 6, pady = 5, columnspan = 2,
                        sticky = tk.N)
        
        self.results = plot_assoc_graph(self.results,
                                        graph_type = "imputed")
        
        self.results.imp_fig.subplots_adjust(left = 0.07, right = 0.98,
                                            top = 0.92)
        self.imp_graph.canvas.draw_idle()
        self.imp_graph.graph_option_pane.update_text_options()


    def pick_file(self):
        filename = tk.filedialog.askopenfilename(defaultextension = ".txt",
                                        filetypes=[("TEXT", ".txt")],
                                        title = "Choose File")
        self.enter_text.state(["!readonly"])
        self.enter_text.delete(0, "end")
        self.enter_text.insert(0, filename)
        self.enter_text.state(["readonly"])
        self.check_if_empty()
        
    def check_if_empty(self):
        if self.enter_text.get() == "":
            self.go_button.state(["disabled"])
        elif self.enter_text.get() != "":
            self.go_button.state(["!disabled"])
