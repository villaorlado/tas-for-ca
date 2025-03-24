# Querying YouTube Data API and Downloading YouTube Videos
In this code, we focus on carrying out two tasks.

# 1. Querying YouTube Data API
We first search for all YouTube videos consisting of the keyword **wayang kulit**.

## Instructions
1. Create a *.env* file containing
> YOUTUBE_DATA_API_KEY="XXXXX"
where XXXXX is the data API key
*(It would be good practice to have a .gitignore file that excludes .env to prevent leakage of your API key)*

2. Adjust the search parameters in *youtube_data_api_query.py*. The comments in the file are fairly detailed and would give you a good understanding of how the code works.

3. Run the command
```bash
python3 youtube_data_api_query.py
```
or with the following options

```bash
python3 youtube_data_api_query --output_data_path "XX" --output_completion_log_path XX --temp_dir_file_path XX --i_start XX --i_end XX --ref_datetime XX --window_size_in_mins XX
```

As mentioned in the comments in *youtube_data_api_query.py*, each API key is granted 10,000 credits daily.
Getting a page of YouTube videos cost 100 credits and getting the details of a video costs 1 credit each.
Therefore, we could theoretically obtain the details of up to 6666 videos daily. Using more than one API key
per project would violate the Terms of Use of YouTube Data API!

# 2. Downloading YouTube videos
We use *yt-dlp* on the command line to download YouTube videos

## Instructions
1. Download yt-dlp [yt-dlp github](https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation)

2. Prepare a csv file with 3 columns in the order: nb, url, title
- nb: a unique identifier for the video
- url: YouTube url of the video
- title: title of the YouTube video

3. Designate a folder for the videos to be saved into

4. Decide which videos to download (identified by nb) from range $m$ to $n-1$

5. Run the command
*General*
```bash
bash yt_dler.sh videos_to_download.csv /path/to/destination/folder m n
```
*Our Usage*
```bash
bash yt_dler.sh videos_to_download.csv "../../data/videos" 0 100
```

More details are available in the comments of *yt_dler.sh*.