import argparse
import json
import os
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from tqdm import tqdm

def load_data(results_json_path:str, video_id:str):

	with open(results_json_path,'r') as file:
		new_data = json.load(file)
	pred = new_data[video_id]['predictions']

	return pred

def render_results(video_id:str, 
				   results_json_path:str,
				   thumbnails_parent_dir:str,
				   thumbnails_render_resolution:tuple,
				   num_cols:int,
				   output_pdf_dir:str):
	
	# Parse argument
	thumbnails_dir = f'{thumbnails_parent_dir}/{video_id}'

	# Load thumbnails
	thumbnails_path = os.listdir(thumbnails_dir)
	thumbnails_path.sort()

	# Load prediction results
	pred = load_data(results_json_path, video_id)

	# Grid parameters
	top_margin = 40
	side_margin = 20
	vertical_spacing = 40
	horizontal_spacing = 20

	num_rows = len(thumbnails_path) // num_cols + 1
	image_width, image_height = thumbnails_render_resolution
	grid_width = side_margin + num_cols * (image_width + horizontal_spacing) 
	grid_height = top_margin + num_rows * (image_height + vertical_spacing)

	# Create a blank grid image
	grid_image = Image.new("RGB", (grid_width, grid_height), "white")
	draw = ImageDraw.Draw(grid_image)

	# Place images in the grid
	for idx, image_path in enumerate(thumbnails_path):
		img = Image.open(f"{thumbnails_dir}/{image_path}")
		img = img.resize(thumbnails_render_resolution)
		row = idx // num_cols
		col = idx % num_cols
		x = side_margin + col * (image_width + horizontal_spacing)
		y = top_margin + row * (image_height + vertical_spacing)
		
		# Highlight if interlude
		if pred[idx] == 1:
			rectangle_position = (x-horizontal_spacing//2, y-vertical_spacing//2, 
								x+image_width+horizontal_spacing//2, y+image_height+vertical_spacing//2)  
			draw.rectangle(rectangle_position, fill=(100, 0, 0))

		# Render thumbnail
		grid_image.paste(img, (x, y))

	# Save the grid as a temporary file
	temp_grid_path = f"{output_pdf_dir}/{video_id}.jpg"
	grid_image.save(temp_grid_path)

	# Create a PDF with the grid image using reportlab
	pdf_path = f"{output_pdf_dir}/{video_id}.pdf"
	c = canvas.Canvas(pdf_path, pagesize=(grid_width,grid_height))
	c.drawImage(temp_grid_path, 0, 0, width=grid_width, height=grid_height)
	c.showPage()
	c.save()

def render_results_for_dir(results_json_path:str,
						   thumbnails_parent_dir:str,
						   thumbnails_render_resolution:tuple,
						   num_cols:int,
						   output_pdf_dir:str):
	
	# Load results JSON
	with open(results_json_path, "r") as file:
		results = json.load(file)
	
	# Iterate over videos
	for video_id in tqdm(results.keys()):
		render_results(
			video_id=video_id,
			results_json_path=results_json_path,
			thumbnails_parent_dir=thumbnails_parent_dir,
			thumbnails_render_resolution=thumbnails_render_resolution,
			num_cols=num_cols,
			output_pdf_dir=output_pdf_dir
		)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Render results into a PDF.")
	parser.add_argument("--results_json_path", type=str, help="Path to the results JSON file")
	parser.add_argument("--thumbnails_parent_dir", type=str, help="Parent directory containing thumbnails")
	parser.add_argument("--thumbnails_render_resolution", type=int, nargs=2, help="Resolution to render thumbnails (width height)")
	parser.add_argument("--num_cols", type=int, help="Number of columns in the grid")
	parser.add_argument("--output_pdf_dir", type=str, help="Directory to save the output PDF")
	args = parser.parse_args()

	render_results_for_dir(
		results_json_path=args.results_json_path,
		thumbnails_parent_dir=args.thumbnails_parent_dir,
		thumbnails_render_resolution=tuple(args.thumbnails_render_resolution),
		num_cols=args.num_cols,
		output_pdf_dir=args.output_pdf_dir
	)