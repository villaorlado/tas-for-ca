import argparse
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import glob
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
import json
import os
import pandas as pd
import requests
import yaml


def get_video_metadata(output_data_path:str,
                       output_completion_log_path:str,
                       temp_dir_file_path:str,
                       i_start:int,
                       i_end:int,
                       ref_datetime:str,
                       window_size_in_mins:int):
    """
    [Arguments]
        output_data_path: filepath to the CSV file to save data in
        output_completion_log_path: filepath to the CSV file to save completion results in
        temp_dir_file_path: filepath to save backup files

        i_start: API Results tracking (inclusive)
        i_end: API Results tracking (exclusive)

        ref_datetime: reference datetime to start the search from
                      (the latest date of the search window)
        window_size_in_mins: size of the search window in minutes


    [Explanation]
        We want to extract all YouTube videos with 'wayang kulit' in the title using Google YouTube API.
        Each day, we are provided with 10 000 credits to make API calls.
            - Getting one page of results (up to 50 results) costs 100 credits each.
            - Getting the details of a specific video costs 1 credit each.
        This works out to at least 3 credits per video (≥2 for the search + 1 for the details) 
        and about 6666 videos per day.

        Note that for a given search, we can only access up to 10 pages (restriction imposed by Google).
        This gives a maximum of 500 videos per search.
        To circumvent this restriction, we choose a sufficiently narrow time window such that 
        the search results are less than (10 pages x 50 results/page).
       
        Given a defined time window in minutes, we collect all the results then shift
        the time window backwards in time.

        The code below does the following: 
            1. Get the list of YouTube videos with 'wayang kulit' in the title from 
               Google's YouTube API within the specified timeframe

            2. For each video in the list:
                a. Get the relevant information from the response
                    - Video URL
                    - Title
                    - Duration
                    - Name of the Channel 
                    - Number of Likes 
                    - Date 
                    - Description
                b. Write the data into {local_i={i}_metadata} csv file

            3. If there's a next page, get results for the next page. 
               If not:
                   - combine the csv file from {local_i={i}_metadata} csv file to the 
                     main {output_data_path} csv file 
                   - write to {output_completion_log_path} csv file
                   - redefine the timeframe to something earlier 
                   - go to step 2.

    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~#
    #   Filepath management   #
    #~~~~~~~~~~~~~~~~~~~~~~~~~#

    # Check if output file exists
    headers = ['i', 'video_id', 'URL', 'channel_name', 'title', 'published_date', 'duration', 'view_count', 'like_count', 'comment_count', 'description']
    if os.path.exists(output_data_path) == False:
        with open(output_data_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

    # Check if output completion_results file exists
    if os.path.exists(output_completion_log_path) == False:
        with open(output_completion_log_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['i', 'completed_datetime','window_start_datetime', 'window_end_datetime', 'nb_videos'])

    # Check if temp dir file path exists
    if os.path.exists(temp_dir_file_path) == False:
        os.makedirs(temp_dir_file_path)
    else:
        # Ensure that the backup file is empty
        for i in range(i_start,i_end):
            for page_nb in range(10):
                for file in os.listdir(temp_dir_file_path):
                    if file.startswith(f'local_metadata_i={str(i).zfill(5)}_page={page_nb}.csv'):
                        raise ValueError("Temp directory is not empty. Please clear the directory before running the script.")

    #~~~~~~~~~~~~~~~~~~~~~~~~~#
    #    Window definition    #
    #~~~~~~~~~~~~~~~~~~~~~~~~~#

    # Ensure i_start <= i_end
    if i_start >= i_end:
        raise ValueError('i_start has to be < i_end')

    # Each API request is enumerated with i. 
    # We need to ensure that there are no duplicates of identifier i
    last_value_of_i = -1
    if os.path.exists(output_completion_log_path) == True:
        with open(output_completion_log_path, mode='r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                last_value_of_i = int(row[0])

    if i_start <= last_value_of_i:
        raise ValueError('i_start must be greater than the last value of i in the completion log file')

    # We have i_start and i_end to keep track of the number of pages called:
    i = i_start

    # Define the initial starting point (latest date) and the interval of the window in minutes
    # Take note that the query started from present moment and we are going backwards in time
    datetime_bef = datetime.fromisoformat(ref_datetime)
    window_end_datetime = datetime_bef.isoformat() + 'Z'


    #~~~~~~~~~~~~~~~~~~~~~~~~~#
    #   Variable definition   #
    #~~~~~~~~~~~~~~~~~~~~~~~~~#

    # API key management
    load_dotenv()
    API_KEY = os.getenv('YOUTUBE_DATA_API_KEY')

    # Counters and page tracking
    nb_videos_on_page = 0
    pageToken = ''
    page_count = 0


    #~~~~~~~~~~~~~~~~~~~~~~~~~#
    #      Grab Metadata      #
    #~~~~~~~~~~~~~~~~~~~~~~~~~#

    while i < i_end:

        # 1. Obtain the list of YouTube videos with 'wayang kulit'
        # Date interval definition 
        datetime_aft = datetime_bef - timedelta(minutes=max(1,window_size_in_mins))
        window_start_datetime = datetime_aft.isoformat() + 'Z'

        # Load the configuration as a dictionary
        with open("src/query_config.yaml", "r") as f:
            yaml_dict = yaml.safe_load(f)
        yaml_dict["pageToken"] = pageToken 
        yaml_dict["publishedAfter"] = window_start_datetime
        yaml_dict["publishedBefore"] = window_end_datetime

        # Calling search results
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        search_request = youtube.search().list(**yaml_dict)

        # search_request = youtube.search().list(
        #     part='snippet',
        #     channelType='any',
        #     eventType='completed',
        #     maxResults=50,
        #     order='relevance',
        #     pageToken=pageToken,
        #     publishedAfter=window_start_datetime,
        #     publishedBefore=window_end_datetime,
        #     q='wayang kulit',
        #     # relevanceLanguage='id',
        #     type='video',
        #     videoCaption='any',
        #     videoDefinition='any',
        #     videoDimension='any',
        #     videoDuration='any',
        #     videoEmbeddable='any',
        #     videoLicense	='any',
        #     videoPaidProductPlacement='any',
        #     videoSyndicated='any',
        #     videoType='any',
        # )

        search_results = search_request.execute()

        # Create CSV file to write search results to
        local_temp_file_path = f"{temp_dir_file_path}/local_metadata_i={str(i).zfill(5)}_page={page_count}.csv"
        with open(local_temp_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

        # 2. For each video in the search results,
        for video_details in search_results['items']:

            # 2a. Grab the video description, etc...
            video_id = video_details['id']['videoId']
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'id'  : video_id,
                'part': 'contentDetails, snippet, statistics',
                'key' : API_KEY}
            response = requests.get(url, params=params)

            # Ensure that response is valid, if not throw error
            if response.status_code != 200:
                print('nope!')
                raise HttpError(response.status_code)

            # 2b. Parse the results and insert into csv
            results = json.loads(response.text)

            id = results['items'][0]['id']
            channel_name = results['items'][0]['snippet']['channelTitle']
            title = results['items'][0]['snippet']['title']
            try: 
                view_count = results['items'][0]['statistics']['viewCount']
            except:
                view_count = None

            try: 
                like_count = results['items'][0]['statistics']['likeCount']
            except:
                like_count = None

            try:
                comment_count = results['items'][0]['statistics']['commentCount']
            except:
                comment_count = None

            duration = isodate.parse_duration(results['items'][0]['contentDetails']['duration']).total_seconds()
            published_date = results['items'][0]['snippet']['publishedAt']
            description = results['items'][0]['snippet']['description']

            # Write to CSV file
            local_temp_file_path = f"{temp_dir_file_path}/local_metadata_i={str(i).zfill(5)}_page={page_count}.csv"

            results = [i, id, f'https://www.youtube.com/watch?v={id}', channel_name, title, published_date, duration, view_count, like_count, comment_count, description]
            with open(local_temp_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(results)


        # 3. Keep track of counters
        nb_videos_on_page += int(search_results['pageInfo']['resultsPerPage'])
        page_count += 1 


        # 4. Go to next page if possible. If not, write to log and redefine the search window
        try:
            pageToken = search_results['nextPageToken']

        except:
            
            # Combine to main file
            new_csv_files = glob.glob(f"{temp_dir_file_path}/local_metadata_i={str(i).zfill(5)}_*.csv") 
            old_df = [pd.read_csv(output_data_path)]
            new_dfs = [pd.read_csv(file) for file in new_csv_files if pd.read_csv(file).empty == False]
            df = pd.concat(old_df + new_dfs, ignore_index=True)
            df.to_csv(output_data_path,index=False)

            # Completion print
            print(f'√ {i} -- Number of Videos: {nb_videos_on_page} Completed at:{datetime.now().strftime("%y-%m-%d-%H-%M-%S")} -- Window[{datetime_aft.strftime("%y-%m-%d-%H-%M-%S")} ~> {datetime_bef.strftime("%y-%m-%d-%H-%M-%S")}]')
            print_results = [i, datetime.now().strftime("%y-%m-%d-%H-%M-%S"),datetime_aft, datetime_bef, nb_videos_on_page]
            with open(output_completion_log_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(print_results)

            # Re-adjust parameters
            pageToken = ''
            datetime_bef = datetime_aft
            window_end_datetime = datetime_bef.isoformat() + 'Z'
            window_size_in_mins = window_size_in_mins
            i += 1
            page_count = 0
            nb_videos_on_page = 0
            

if __name__ == "__main__":

    ############################
    #        Parameters        #
    #############################
    
    # Filepath to the CSV file to save data in
    output_data_path = 'data/video_metadata.csv'
    output_completion_log_path = 'data/completion_results.csv'
    temp_dir_file_path = 'data/temp_dir'

    # Read the CSV file to get default values
    if os.path.exists(output_completion_log_path) == True:
        with open(output_completion_log_path, mode='r', encoding='UTF-8') as file:

            reader = csv.reader(file)

            # Count number of rows
            rows = len(list(reader))
            
            # Define window
            if rows <= 1:
                last_value_of_i = -1
                window_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                file.seek(0) 
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    last_value_of_i = int(row[0])
                    window_end_time = row[2]
    else:
        last_value_of_i = -1
        window_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    parsed_time = datetime.strptime(window_end_time, '%Y-%m-%d %H:%M:%S')
    formatted_window_end_time = parsed_time.strftime('%Y-%m-%dT%H:%M:%S')

    # API Results page tracking
    i_start = last_value_of_i + 1
    i_end = last_value_of_i + 2

    # Window parameters
    ref_datetime = formatted_window_end_time
    window_size_in_mins = 1800

    # Parse results
    parser = argparse.ArgumentParser(description='Scrape YouTube video metadata.')
    parser.add_argument('--output_data_path', type=str, default=output_data_path, help='Filepath to the CSV file to save data in')
    parser.add_argument('--output_completion_log_path', type=str, default=output_completion_log_path, help='Filepath to the CSV file to save completion results in')
    parser.add_argument('--temp_dir_file_path', type=str, default=temp_dir_file_path, help='Filepath to save backup files')
    parser.add_argument('--i_start', default=i_start, type=int, help='API Results tracking start (inclusive)')
    parser.add_argument('--i_end', default=i_end, type=int, help='API Results tracking end (exclusive)')
    parser.add_argument('--ref_datetime', type=str, default=ref_datetime, help='Reference datetime to start the search from')
    parser.add_argument('--window_size_in_mins', type=int, default=window_size_in_mins, help='Size of the search window in minutes')
    args = parser.parse_args()


    # Get video metadata
    get_video_metadata(
        output_data_path=args.output_data_path,
        output_completion_log_path=args.output_completion_log_path,
        temp_dir_file_path=args.temp_dir_file_path,
        i_start=args.i_start,
        i_end=args.i_end,
        ref_datetime=args.ref_datetime,
        window_size_in_mins=args.window_size_in_mins
    )


