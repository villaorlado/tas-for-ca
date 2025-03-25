
import json
import matplotlib.pyplot as plt

def plot_video_heatmaps(json_file_path):

	# Open files
	with open(json_file_path, 'r') as file:
		data = json.load(file)

	# Define a colormap for the labels and predictions
	cmap = plt.get_cmap('viridis', 2)  # 2 discrete colors

	for key in data.keys():
		
		# Extract the label data
		labels = data[key]['groundtruth']
		pred = data[key]['predictions']

		# Plot the 1-dimensional heatmap
		plt.figure(figsize=(15, 3))

		# Plot the labels
		plt.subplot(2, 1, 1)
		plt.imshow([labels], aspect='auto', cmap=cmap, vmin=0, vmax=1)
		plt.colorbar(label='Label', ticks=[0, 1])
		plt.xlabel('Index')
		plt.title(f'1-Dimensional Heatmap of Labels for {key}')
		plt.gca().set_yticks([0])
		plt.gca().set_yticklabels(['Labels'])
		plt.gca().tick_params(axis='y', which='both', length=0)

		# Plot the predictions
		plt.subplot(2, 1, 2)
		plt.imshow([pred], aspect='auto', cmap=cmap, vmin=0, vmax=1)
		plt.colorbar(label='Prediction', ticks=[0, 1])
		plt.xlabel('Index')
		plt.title(f'1-Dimensional Heatmap of Predictions for {key}')
		plt.gca().set_yticks([0])
		plt.gca().set_yticklabels(['Predictions'])
		plt.gca().tick_params(axis='y', which='both', length=0)

		plt.tight_layout()
		plt.show()