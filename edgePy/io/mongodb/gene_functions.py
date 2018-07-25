
"""The core Python code for generating data."""


def get_genelist_from_file(filename):
    if not filename:
        return None
    gene_list = []
    with open(filename, 'r') as file_handle:
        for line in file_handle:
            gene_list.append(line.strip())
    return gene_list


def translate_genes(genes, mongo_reader):
    ensg_genes = []
    non_ensg_genes = []
    gene_symbols = {}

    if genes:
        for gene in genes:
            if gene.startswith("ENSG"):
                ensg_genes.append(gene)
            else:
                non_ensg_genes.append(gene)
    if ensg_genes or not genes:
        if not genes:
            query = {}
        else:
            query = {'_id': {'$in': ensg_genes}}

        symbol_gene_list = mongo_reader.find_as_cursor('ensembl_90_37', 'symbol_by_ensg',
                                                       query=query)
        for symbol_gene in symbol_gene_list:
            for symbol in symbol_gene['symbols']:
                gene_symbols[symbol_gene['_id']] = symbol
        for ensg in ensg_genes:
            if ensg not in gene_symbols:
                gene_symbols[ensg] = ensg
    if non_ensg_genes or not genes:
        if not genes:
            query = {}
        else:
            query = {'_id': {'$in': non_ensg_genes}}
        translated_gene_list = mongo_reader.find_as_cursor('ensembl_90_37', 'ensg_by_symbol',
                                                           query=query)
        for trans_gene in translated_gene_list:
            symbol = trans_gene['_id']
            ensgs = trans_gene['ensgs']
            for ensg in ensgs:
                gene_symbols[ensg] = symbol
                ensg_genes.append(ensg)
    return ensg_genes, gene_symbols


def get_gene_list(mongo_reader):
    genes = mongo_reader.find_as_cursor('ensembl_90_37', 'symbol_by_ensg', query={})
    gene_symbols = {}
    for symbol_gene in genes:
        for symbol in symbol_gene['symbols']:
            gene_symbols[symbol_gene['_id']] = symbol
    return gene_symbols


def get_sample_details(group_by, mongo_reader):

    sample_details = {}
    search = {group_by: {'$exists': True}}
    sample_grouping = mongo_reader.find_as_cursor('Tenaya', 'samples',
                                                  query=search,
                                                  projection={'_id': 0, group_by: 1, 'sample_name': 1,
                                                              'Description': 1})

    for sample in sample_grouping:
        sample_details[sample['sample_name']] = {
            'description': sample['Description'] if 'Description' in sample else sample['sample_name'],
            'category': sample[group_by]}

    return sample_details


def get_canonical_rpkm(result):
    transcript_list = result['transcripts']
    for trans in transcript_list.values():
        if int(trans['canonical']) == 1:
            return trans['rpkm']
    return None
