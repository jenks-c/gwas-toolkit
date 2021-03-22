import sys

import math
import statistics
from matplotlib import pyplot
from matplotlib.figure import Figure

from scipy import stats as st

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)

def get_simple_filename(file_path):
    """cleans up file path and returns a simple filename"""
    filename = file_path#.split(".")
    if "\\" in r"%r" % filename:
        split_file = filename.split("\\")
        filename = split_file[-1]
    elif "/" in r"%r" % filename:
        split_file = filename.split("/")
        filename = split_file[-1]
    else:
        filename = filename[0]
    return filename

def get_gwas_data(assoc_file):
    """
    Takes GWAS assoc file and returns a list of nested lists containing the
    data, and a dictionary of the headers and their indexes for easy reference
    """
    header_dict = {}
    data = {}
    with open(assoc_file) as fobj:
        header = fobj.readline().strip().split()
        if len(header) == 14:
            pass
        else:
            print("That doesnt look like a PLINK .assoc file")
            sys.exit()
        for col in header:
            header_dict[col] = header.index(col)
        for line in fobj:
            snp_data = line.strip().split()
            data[snp_data[header.index("rs")]] = snp_data
    name = get_simple_filename(assoc_file)
    print(f"\nThere are {len(data)} SNPs in {name}")
    return data, header_dict

def get_assoc_columns(header_dictionary, filetype, plot = "assoc"):
    """
    Makes a standardised dictionary containing the indexs of the columns
    with the useful info for an association plot
    """
    item_indexs = {}
    if filetype == "plink":
        item_indexs["p"] = header_dictionary["P"]
        if plot == "assoc":
            item_indexs["snp"] = header_dictionary["SNP"]
            item_indexs["chr"] = header_dictionary["CHR"]
            item_indexs["bp"] = header_dictionary["BP"]
            item_indexs["a1"] = header_dictionary["A1"]
            item_indexs["a2"] = header_dictionary["A2"]
    elif filetype == "gemma":
        item_indexs["p"] = header_dictionary["p_score"]
        if plot == "assoc":
            item_indexs["snp"] = header_dictionary["rs"]
            item_indexs["chr"] = header_dictionary["chr"]
            item_indexs["bp"] = header_dictionary["ps"]
            item_indexs["a1"] = header_dictionary["allele0"]
            item_indexs["a2"] = header_dictionary["allele1"]
    elif filetype == "snpinfo":
        item_indexs["p"] = header_dictionary["ESp"]
        if plot == "qq":
            item_indexs["qp"] = header_dictionary["Qp"]
        elif plot == "assoc":
            item_indexs["snp"] = header_dictionary["snp"]
            item_indexs["chr"] = header_dictionary["chr"]
            item_indexs["bp"] = header_dictionary["bp"]
    return item_indexs
    
def user_input_assoc_columns(item_dictionary, header_dictionary):
    """
    Takes a dictionary of the items needed with their description,
    and a dictionary of a files headers and their indexes,
    and gets user inputed locations for the items needed in an analysis
    """
    item_indexs = {}
    print("\nPlease input the header of the column that contains the "
        "following:")
    for key, detail in item_dictionary.items():
        head = ""
        while True:
            head = input(f"\n{detail}\n\t> ")
            if key == "Qp" and head == "":
                break
            else:
                if head in header_dictionary:
                    print(f"\n{head}, column number "
                        f"{(header_dictionary[head]) + 1}, "
                        "is that correct? Y/N")
                    if input("\t> ").lower() == "y":
                        item_indexs[key] = head
                        break
                else:
                    print(f"\nCould not find '{item_indexs[key]}' in the file, "
                        "please try again.")
    for item in item_indexs:
        item_indexs[item] = header_dictionary[item_indexs[item]]
    return item_indexs

def find_file_type(header_dict):
    """
    Uses key column headers to identify the filetype, then calls functions
    to get the header indexs for analyses
    """
    plink = ["P", "SNP", "CHR", "BP"]
    gemma = ["p_score", "rs", "chr", "ps"]
    snpinfo = ["snp", "chr", "bp", "ESp", "Qp"]

    if all(columns in header_dict for columns in plink):
        message = ("This looks like an assoc file produced by PLINK or after"
                " a meta-analysis. Is that correct?")
        filetype = "plink"
    elif all(columns in header_dict for columns in gemma):
        message = ("This looks like an assoc file produced by GEMMA."
            " Is that correct?")
        filetype = "gemma"
    elif all(columns in header_dict for columns in snpinfo):
        message = ("This looks like a snpinfo file produced by a meta-analysis"
                ". Is that correct?")
        filetype = "snpinfo"
    else:
        message = "The file format is not recognised."
        filetype = "unknown"

    return message, filetype

def keep_common_snps(dataset1, dataset2):
    """Removes the SNPs not in both of two GWAS datasets"""
    n = 0
    snp_remove = []
    for snp in dataset1:
        if snp in dataset2:
            n += 1
        else:
            snp_remove.append(snp)
    for snp in dataset2:
        if snp not in dataset1:
            snp_remove.append(snp)

    for snp in snp_remove:
        if snp in dataset1:
            del dataset1[snp]
        elif snp in dataset2:
            del dataset2[snp]
    
    if len(dataset1) == n and len(dataset2) == n:
        print(f"\nThere are {n} SNPs in common between the two datasets.")
        print(f"\nOnly the common SNPs kept in both datasets.")
    else:
        print("\nSomething went wrong with finding shared SNPs. Exiting.")
        sys.exit()
        
def header_index(header_list):
    """
    takes a list of column headers and returns a dictionary with the indexes
    """
    dictionary = {}
    for h in header_list:
        dictionary[h] = header_list.index(h)
    return dictionary
    
def make_qq_plot(resultsobj):
    """
    Takes data from a meta-analysis and produces a quantile - quantile plot
    """
    
    # this is slow, takes just under 2 minutes
    
    assoc_data_list = resultsobj.assoclist
    header_index_dict = resultsobj.assocheader
    
    graph = resultsobj.qq_graph
    
    print("\nPreparing data for QQ-plot...")
    #missing_qp = []
    #for snp in assoc_data_list:
    #    if bool(snp[header_index_dict["Qp"]]) == False:
           # missing_qp.append(snp[header_index_dict["snp"]])
    
    # sort by esp (the p - value)

    assoc_data_list.sort(key = lambda x : x[header_index_dict["p"]])
    e_chi = []
    o_chi = []
    rank = 1
    n = 10
    for snp in assoc_data_list:
        #if bool(snp[header_index_dict["Qp"]]) == True:
        obs_p = float(snp[header_index_dict["p"]])
        exp_p = (rank - 0.5) / ((len(assoc_data_list)))
        exp_chi = (st.chi2.isf(exp_p, 1))
        e_chi.append(exp_chi)
        obs_chi = (st.chi2.isf(obs_p, 1))
        o_chi.append(obs_chi)
        rank += 1
        percent = (rank / len(assoc_data_list)) * 100
        if round(percent) == n:
            percent_complete = round(percent)
            print(f"SNPs analysed: {round(percent_complete)}%")
            n +=10
    print(f"SNPs analysed: {rank - 1}")
    
    obsallmean = statistics.mean(o_chi)
    expallmean = statistics.mean(e_chi)
    lambda1 = obsallmean / expallmean
    print(f"\nThe lambda (as calculated from the means) is: {lambda1}")
    
    obsallmedian = statistics.median(o_chi) #stata script does this on obs p ???
    expallmedian = statistics.median(e_chi)
    lambda2 = obsallmedian / expallmedian
    print(f"obsallmedian: {obsallmedian}, expallmedian: {expallmedian}")
    print(f"The lambda (as calculated from the medians) is: {lambda2}")
    
    print("\nPlotting data...")
    graph.scatter(e_chi, o_chi, label = "Observed Chi")
    graph.scatter(e_chi, e_chi, label = "Expected Chi")
    graph.legend(loc = "lower center")
    graph.set_xlabel("Expected Chi")
    graph.set_ylabel("Observed Chi")
    graph.set_title(f"QQ plot for association tests for "
            f"{(len(assoc_data_list))} SNPs (1 df)")
    
    resultsobj.qq_graph = graph
    
def make_qq_plot_pval(resultsobj):
    """
    Takes data from a meta-analysis and produces a quantile - quantile plot
    but with p values instead of chi
    """
    
    assoc_data_list = resultsobj.assoclist
    header_index_dict = resultsobj.assocheader
    
    graph = resultsobj.qq_graph
    
    print("\nPreparing data for QQ-plot...")

    assoc_data_list.sort(key = lambda x : x[header_index_dict["p"]])
    e_logp = []
    e_p = []
    o_logp = []
    o_p = []
    rank = 1
    n = 10
    for snp in assoc_data_list:
        obs_p = float(snp[header_index_dict["p"]])
        exp_p = (rank - 0.5) / ((len(assoc_data_list)))
        exp_logp = (math.log10(exp_p)) * -1
        e_p.append(exp_p)
        e_logp.append(exp_logp)
        obs_logp = (math.log10(obs_p)) * -1
        o_p.append(obs_p)
        o_logp.append(obs_logp)
        rank += 1
        percent = (rank / len(assoc_data_list)) * 100
        if round(percent) == n:
            percent_complete = round(percent)
            print(f"SNPs analysed: {round(percent_complete)}%")
            n +=10
    print(f"SNPs analysed: {rank - 1}")
    
    o_chi = st.chi2.isf(o_p, 1)
    e_chi = st.chi2.isf(e_p, 1)
    
    obsallmean = statistics.mean(o_chi)
    expallmean = statistics.mean(e_chi)
    lambda1 = obsallmean / expallmean
    print(f"\nThe lambda (as calculated from the means) is: {lambda1}")
    
    obsallmedian = statistics.median(o_chi) #stata script does this on obs p ???
    expallmedian = statistics.median(e_chi)
    lambda2 = obsallmedian / expallmedian
    print(f"obsallmedian: {obsallmedian}, expallmedian: {expallmedian}")
    print(f"The lambda (as calculated from the medians) is: {lambda2}")
    
    print("\nPlotting data...")
    graph.scatter(e_logp, o_logp, label = "Observed -Log10 P-value")
    graph.scatter(e_logp, e_logp, label = "Expected -Log10 P-value")
    graph.legend(loc = "lower center")
    graph.set_xlabel("Expected -Log10 P-value")
    graph.set_ylabel("Observed -Log10 P-value")
    graph.set_title(f"QQ plot for association tests for "
            f"{(len(assoc_data_list))} SNPs (1 df)")
    
    resultsobj.qq_graph = graph
 
    
def plot_single_chr(resultsobj, chrom):
    """
    plots an association plot of only a single chromosome, with bp on the x axis
    """
    chrom_snpbp = resultsobj.chrom_snpbp
    chrom_snplogp = resultsobj.chrom_snplogp
    
    fig = Figure(figsize = [9, 5])
    graph = fig.add_subplot()
    
    series = graph.scatter(chrom_snpbp[chrom], chrom_snplogp[chrom], 5)
    
    plottitle = f"Chromosome {chrom} Association Plot"

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
    
    return fig, graph, series

def plot_assoc_chr(resultsobj, chrom):
    """
    Takes a list of lists containing pvalues, snp name, chr, and bp position,
    and a dictionary idicating which is which, to plot an -logp assoc plot
    """
    data = resultsobj.assoclist
    dataheader = resultsobj.assocheader
    chrom_snpnum = resultsobj.chrom_snpnum
    chrom_snpbp = resultsobj.chrom_snpbp
    chrom_snplogp = resultsobj.chrom_snplogp
    relgenpos = resultsobj.relgenpos
    assoc_ticks = resultsobj.assoc_ticks
    highest_pvals = resultsobj.highest_pvals
    graph = resultsobj.graph
    series_list = resultsobj.series_list
    
    
    print(f"Plotting: chr{chrom} ({len(chrom_snpnum[chrom])} SNPs)")
    #series = graph.scatter(chrom_snpnum[chrom], chrom_snplogp[chrom], 3,
    #            label = chrom)
    series = graph.scatter(relgenpos[chrom], chrom_snplogp[chrom], 3,
                label = chrom)
    series_list.append(series)
    #chrom_start = chrom_snpnum[chrom][0]
    chrom_start = relgenpos[chrom][0]
    chrom_end = chrom_snpnum[chrom][-1]
    chrom_mid = (chrom_start + chrom_end) / 2
    assoc_ticks.append(chrom_start)
    high_snp = [0]
    num = 0
    for snp in chrom_snplogp[chrom]:
        if snp > high_snp[0]:
            pos = relgenpos[chrom][num]
            snpnum = chrom_snpnum[chrom][num]
            high_snp = [snp, pos]
            for item in data:
                if item[dataheader["n"]] == snpnum:
                    high_snp.append(item[dataheader["snp"]])
                    high_snp.append(item[dataheader["chrom"]])
                    high_snp.append(item[dataheader["bp"]])
        num += 1
    highest_pvals.append(high_snp)
    
    resultsobj.assoc_ticks = assoc_ticks
    resultsobj.highest_pvals = highest_pvals
    resultsobj.graph = graph
    resultsobj.series_list = series_list
    
    return resultsobj
        
def plot_assoc_graph(resultsobj, graph_type = "genotyped"):

    assoc_ticks = resultsobj.assoc_ticks
    chromset = resultsobj.chromset
    #highest_pvals = resultsobj.highest_pvals
    #data = resultsobj.data
    if graph_type == "genotyped":
        graph = resultsobj.graph
    elif graph_type == "imputed":
        graph = resultsobj.imp_graph

    

    plottitle = "Association Plot"

    graph.set_ylabel("-log10 p-value")
    graph.set_ylim(bottom = 0)
    graph.set_xticks(assoc_ticks)
    graph.set_xticklabels(chromset, size = "x-small")
    graph.set_xlabel("Chromosome")
    graph.set_title(plottitle)
    ybottom, ytop = graph.get_ylim()
    ytop = math.ceil(ytop)
    graph.set_ylim(bottom = 0, top = ytop)
                
    graph.spines['right'].set_visible(False)
    graph.spines['top'].set_visible(False)
    
    if graph_type == "genotyped":
        resultsobj.graph = graph
    elif graph_type == "imputed":
        resultsobj.imp_graph = graph
    
    resultsobj.graphtitle = plottitle
    
    return resultsobj
    
def add_remove_annotations(resultsobj, graph_type = "all_chr"):
    
    ann_list = resultsobj.ann_list
    n_annotations = resultsobj.n_annotations
    highest_pvals = resultsobj.highest_pvals
    
    highest_pvals.sort(key = lambda x : x[0], reverse = True)
    
    if graph_type == "all_chr":
        graph = resultsobj.graph
    elif graph_type == "imputed":
        graph = resultsobj.imp_graph
        
    if ann_list:
        for ann in ann_list:
            ann.remove()
        ann_list = []
    
    if n_annotations == 0:
        pass
    else:
        for item in highest_pvals[:n_annotations]:
            logp2df = "{:.2f}".format(item[0])
            ann = graph.annotate(f"{logp2df}\n{item[2]}\n{item[3]}:{item[4]}",
                                (item[1], item[0]),
                                xytext = (0, 10), size = "x-small",
                                textcoords = "offset pixels")
            ann_list.append(ann)
    
    resultsobj.ann_list = ann_list
    
    if graph_type == "all_chr":
        resultsobj.graph = graph
    elif graph_type == "imputed":
        resultsobj.imp_graph = graph
    
    return resultsobj

def get_data(file_location):
    
    header_dict = {}
    data = []
    
    with open(file_location) as fobj:
        header = fobj.readline().strip().split()
        for col in header:
            header_dict[col] = header.index(col)
        for line in fobj:
            snp_data = line.strip().split()
            data.append(snp_data)
    return header_dict, data

def prep_assoc_data(resultsobj):

    for line in resultsobj.data:
        snp = line[resultsobj.item_indexs["snp"]]
        chrom = int(line[resultsobj.item_indexs["chr"]])
        bp = int(line[resultsobj.item_indexs["bp"]])
        p = float(line[resultsobj.item_indexs["p"]])
        data = [snp, chrom, bp, p]
        resultsobj.assoclist.append(data)
        
        if "a1" in resultsobj.item_indexs:
            a1 = line[resultsobj.item_indexs["a1"]]
            a2 = line[resultsobj.item_indexs["a2"]]
            alleles = [a1, a2]
            resultsobj.snp_alleles[snp] = alleles
            

    resultsobj.assocheader = {"snp": 0, "chrom" : 1, "bp" : 2, "p" : 3}

    
    print("\nPreparing data for association plot.")
    chromlist = []
    for snp in resultsobj.assoclist:
        chromlist.append(snp[resultsobj.assocheader["chrom"]])
    resultsobj.chromset = set(chromlist)

    for chrom in resultsobj.chromset:
        resultsobj.chrom_snpnum[chrom] = []
        resultsobj.chrom_snplogp[chrom] = []
        resultsobj.chrom_snpbp[chrom] = []
        resultsobj.relgenpos[chrom] = []

    resultsobj.assoclist.sort(key = lambda x : (
                        x[resultsobj.assocheader["chrom"]],
                        x[resultsobj.assocheader["bp"]]
                        )
                        )

    n = 1
    for snp in resultsobj.assoclist:
        p = snp[resultsobj.assocheader["p"]]
        logp = (math.log10(p)) * -1
        resultsobj.chrom_snplogp[snp[resultsobj.assocheader["chrom"]]].append(logp)
        snp.append(logp)
        resultsobj.chrom_snpnum[snp[resultsobj.assocheader["chrom"]]].append(n)
        snp.append(n)
        bp = snp[resultsobj.assocheader["bp"]]
        resultsobj.chrom_snpbp[snp[resultsobj.assocheader["chrom"]]].append(bp)
        n += 1

    resultsobj.assocheader["logp"] = 4
    resultsobj.assocheader["n"] = 5
    
    chrom_max = {}
    
    for chrom in resultsobj.chromset:
        if chrom == 1:
            chrom_max[chrom] = resultsobj.chrom_snpbp[chrom][-1]
        else:
            prev_chr = chrom - 1
            prev_max = chrom_max[prev_chr]
            chrom_max[chrom] = resultsobj.chrom_snpbp[chrom][-1] + prev_max
        
    for snp in resultsobj.assoclist:
        chrom = snp[resultsobj.assocheader["chrom"]]
        if chrom == 1:
            shiftpos = snp[resultsobj.assocheader["bp"]]
        else:
            prev_chr = chrom - 1
            shiftpos = snp[resultsobj.assocheader["bp"]] + chrom_max[prev_chr]
        resultsobj.relgenpos[chrom].append(shiftpos)
        snp.append(shiftpos)
        
    resultsobj.assocheader["shiftpos"] = 6

    print(f"\nThe dataset contains {len(resultsobj.chromset)} chromosomes.")

    return resultsobj
