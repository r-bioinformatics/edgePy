import pandas as pd
import os

def merge(dir_path):
	"""
	Input
	========
	directory path with all count files from htseq

	Output
	========
	merged_count files in the same directory

	"""
	files_to_merge = [f for f in os.listdir(args.d) if f.endswith('.tsv')]
	_df = pd.read_csv(args.d+files_to_merge[0], sep='\t',names=['id','count'], index_col=0)
	final_df = pd.DataFrame(data=None, index=_df.index)
	for f in files_to_merge: 
		df_to_add = pd.read_csv(args.d+f, sep='\t', index_col=0, comment='_', names=[f.split('.')[0].split('/')[-1]]) 
		final_df = pd.merge(final_df, df_to_add, left_index=True, right_index=True) 

	final_df.to_csv(dir_path+'htseq_counts_output_merged.tsv', sep='\t')

	return
