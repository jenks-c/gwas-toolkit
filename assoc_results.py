from matplotlib.figure import Figure 

class Assoc():
    """A class to contain assoc data for a plot"""
    def __init__(self):
        self.data = []
        self.item_indexs = {}
        self.assoclist = []
        self.assocheader = {}
        self.chromset = set()
        self.chrom_snpnum = {}
        self.chrom_snplogp = {}
        self.chrom_snpbp = {}
        self.relgenpos = {}
        self.relgenpos_dic = {}
        self.pos_dic = {}
        self.graphtitle = ""
        self.n_annotations = 0
        self.assoc_ticks = []
        self.highest_pvals = []
        self.fig = Figure(figsize = [9, 5])
        self.graph = self.fig.add_subplot()
        self.ann_list = []
        self.series_list = []
        self.qq_fig = Figure(figsize = [5, 5])
        self.qq_graph = self.qq_fig.add_subplot()
        self.snp_alleles = {}
        
    def imputed_graph(self):
        
        self.imp_chr_snplogp = {}
        self.gen_chr_snplogp = {}
        self.imp_chr_relgenpos = {}
        self.gen_chr_relgenpos = {}
        self.gen_chr_snpbp = {}
        self.imp_chr_snpbp = {}
        
        for chrom in self.chromset:
            self.imp_chr_snplogp[chrom] = []
            self.gen_chr_snplogp[chrom] = []
            self.imp_chr_relgenpos[chrom] = []
            self.gen_chr_relgenpos[chrom] = []
            self.imp_chr_snpbp[chrom] = []
            self.gen_chr_snpbp[chrom] = []
        
        self.imp_series_list = []
        self.gen_series_list = []
        self.imp_fig = Figure(figsize = [9, 5])
        self.imp_graph = self.imp_fig.add_subplot()
