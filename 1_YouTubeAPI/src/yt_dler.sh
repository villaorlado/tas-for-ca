: '
We intend to use yt-dlp to download videos from YouTube. 
It is much easier to use yt-dlp on the terminal than using the python equivalent of yt-dlp.

[Download yt-dlp]
   https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation

[Usage]
   Download the videos between $1 (argument 1) inclusive and $2 (argument 2) exclusive using yt-dlp.
   The numbers provided to $1 and $2 refer to the indexing of the videos in the the file data_array_filtered.csv.

[Command Line Arguments]
   $1 : input_csv_file       -- with columns in the order: nb, url, title
   $2 : output_dir           -- use $(pwd) for the current directory
   $3 : start_nb (inclusive) -- the starting index of the video to download (see nb in the input csv file)
   $4 : end_nb (exclusive)   -- the ending index of the video to download (see nb in the input csv file)

[Downloaded Videos]
   The videos would be downloaded in the output directory with the format

      video_{video_id}.mp4

[Example]

   The following command downloads the videos corresponding 
   to index 0017, 0018, 0019, ... , 0038, 0039.
      
      bash yt_dler.sh    videos_to_download.csv $(pwd) 17 40 
      ---- [script name] [~~~~~~~~~$1~~~~~~~~~] [~$2~] $3 $4

'

# Check if argument count is correct
if [ "$#" -ne 4 ]; then
    echo "Error: Exactly 4 arguments are required."
    echo "Usage: $0 [input_csv_file in nb, url, title] [output_dir] [start_nb] [end_nb (excluded)]"
    exit 1
fi

# Parse the arguments
csv_file=$1
output_dir=$2
echo "Input CSV file: $csv_file"
echo "Output directory: $output_dir"
echo ""

# Read the CSV file line by line
while IFS=',' read -r count_id url _;
do
   
   # Only download the videos between the specified range $3 ≤ x < $4
   if [ "$count_id" -ge "$3" ] && [ "$count_id" -lt "$4" ]; then

      # Process the values in the columns
      echo "Column 1: $count_id"
      echo "Column 2: $url"
      # echo "Column 3: $video_title"
      video_id=${url##*v=}
      echo "Video ID: $video_id"

      # Download the videos with video_id as identifier
      yt-dlp --output "$2/${video_id}.%(ext)s" -f bv*[vcodec^=avc]+ba[ext=m4a]/b[ext=mp4]/b --limit-rate 3.0M --sleep-interval 70 --max-sleep-interval 80 ${url}

   fi

   if [ "$count_id" -ge "$4" ]; then
      break
   fi

done < <(tail -n +2 $csv_file)
   

   
