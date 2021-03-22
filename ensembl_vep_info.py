import requests, sys
import json

def get_ensembl_vep_info(snp_data, vep_data = {}):
    vep_info = vep_data
    snp_pos = snp_data
    pos_snp_dictionary = {}
    vep_query = {"variants" : []}
    for key, value in snp_pos.items():
        if key not in vep_info:
            chrom = value[0]
            bp = value[1]
            alleles = " ".join(value[2])
            query = f"{chrom} {bp} . {alleles} . . ."
            pos = f"{chrom} {bp}"
            pos_snp_dictionary[pos] = key
            vep_query["variants"].append(query)
        
    server = "https://rest.ensembl.org"
    ext = "/vep/dog/region"

    headers = { "Content-Type" : "application/json",
                "Accept" : "application/json"}
                
    data = json.dumps(vep_query)

    r = requests.post(server + ext, headers=headers, data = data)
    
    if not r.ok:
        r.raise_for_status()
        sys.exit()
 
    decoded = r.json()
    
    for item in decoded:
        gene_list = []
        if "transcript_consequences" in item:
            for effect in item["transcript_consequences"]:
                if "gene_symbol" in effect:
                    gene_list.append(effect["gene_symbol"])
                elif "gene_id" in effect:
                    gene_list.append(effect["gene_id"])
        gene_list = set(gene_list)
        results = (f"{item['most_severe_consequence'].upper()}")
        if bool(gene_list):
            results += f", Gene: {', '.join(gene_list)}"
            
        query = item['input'].split()
        pos = f"{query[0]} {query[1]}"
        snp = pos_snp_dictionary[pos]
        
        vep_info[snp] = results

    return vep_info
