import pandas as pd

""" 
[purpose]
Pre-process the file from 
	sample_to_download.csv -> data_array_filtered.csv 
We shall discard irrelevant columns for easier management of each row of the data.
"""

# Read the CSV file
data = pd.read_csv("../../data/jan_videos_summary.csv")
data_array = data.to_dict(orient='records')

# Only keep the relevant columns
data_array_filtered = [{'count': str(i).zfill(4), 'URL': item['URL'], 'Title': item['Title']} for i, item in enumerate(data_array)]
df_filtered = pd.DataFrame(data_array_filtered)
df_filtered.to_csv("../../data/jan_videos_to_download.csv", index=False)

