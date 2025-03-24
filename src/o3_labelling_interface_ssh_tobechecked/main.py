import streamlit as st
import pandas as pd
import paramiko
import base64
import re
import os
from typing import Iterator


################################################ 
#        Global session layout settings        #
################################################

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")

# Empty session state
for key in ['video_id', 'video_name','nb_frames','FPS','Duration',
            'select_boxes','filename_array','image_data_array','overwrite','results_uploaded']:
    if key in st.session_state:
        del st.session_state[key]


################################################ 
#       SSH Server interaction functions       #
################################################

def ssh_connect() -> paramiko.SSHClient:
    """
    [Return]
    ssh connection to the SSH server
    """

    # SSH parammeters
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(**st.secrets.ssh_details)
    except:
        st.text("""
                Connection failed! 
                One reason could be because the secrets file 
                could not be found or it was not valid!

                To create a secrets file:
                1. Create a folder in the same directory as main.py
                2. Call this folder .streamlit
                3. Within the folder, create a file called secrets.toml
                4. Within the file secrets.toml, type:
                    [ssh_details]
                    hostname = "XX.XX.XX.XX"
                    username = "user"
                    password = "pass"
                    Replace the values with your own SSH server details.
                5. Save the file and refresh streamlit
                """)
        
    return ssh
    
def ssh_listdir(dir_path:str) -> list:
    """
    [Arguments]
    folder path - filepath of folder in the SSH server

    [Return]
    list of files in a directory in a SSH server 
    """

    # Open connections
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    sftp.chdir(dir_path)
    
    # For each image, run through it
    dir_list = sftp.listdir()
    dir_list.sort()

    # Close the connections
    sftp.close()
    ssh.close()

    return dir_list

def get_csv_file(filepath:str=os.environ["csv_filepath"]) -> pd.DataFrame:
    """
    [Return]
    panda dataframe of the csv file containing a summary of the list of videos
    """

    # Open connections
    ssh = ssh_connect()
    sftp = ssh.open_sftp()

    # Open dataframe
    remote_file = sftp.open(filepath)
    csv_df = pd.read_csv(remote_file)

    # Close the connections
    sftp.close()
    ssh.close()

    return csv_df

@st.cache_resource
def get_images_from_server(video_id:str, n:int=10) -> tuple[list[int], list[str]]:
    """
    Grab every n-th thumbnail from the SSH server.
    We use @st.cache_resource because the pulling process may take a long time
    especially if the number of thumbnails is large.
    Additionally, by separating 
        (i) the pulling of thumbnails 
        (ii) the rendering of thumbnails,
    each refresh of the page would not lead to excessive wait time resulting from (i) re-executing.

    [Arguments]
    video_id - YouTube video ID of the video. 
               The video_id is the key and is used to name the folders in the SSH server.
    step     - to grab every n-th thumbnail

    [Returns]
    filename_array   - array containing filepath of every n-th thumbnail
    image_data_array - array containing image data  of every n-th thumbnail
    """
    
    # Open connections
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    sftp.chdir(f'{os.environ["thumbnails_dir"]}/{video_id}')
    
    # Storage Variables
    filename_array = []
    image_data_array = []

    # For each n-th image, save it in an array for decoding later
    dir_list = sftp.listdir()
    dir_list.sort()

    for i, filename in enumerate(dir_list):

        if i % n == 0: 
            with sftp.open(filename, 'rb') as file:
                image_data = base64.b64encode(file.read()).decode('utf-8')
                filename_array.append(filename)
                image_data_array.append(image_data)
        else:
            continue

    # Close the connections
    sftp.close()
    ssh.close()

    return filename_array, image_data_array

################################################ 
#              User Interaction                #
################################################

def parse_ranges(interval_str:str) -> Iterator[int]:
    """
    For preloading, we offer two options: a text input and a tabular checkbox input.
    This function handles the first case.
    
        [[text input -> tabular checkboxes]] -> st.session_state

    [Argument]
    interval_str - string of the form "0-5,7,9,11"

    [Return]
    Generator of integers in a list [1,2,3,...]

    This would then be used to tick the checkboxes on the table.
    This ensures that the text-input and the table are consistent with each other.
    """

    if interval_str is None:
        yield

    interval_str = interval_str.replace(" ", "")
    intervals = [x.strip() for x in interval_str.split(",")]    
    for interval in intervals:
        if "-" in interval:
            start, end = interval.split("-")
            for i in range(int(start),int(end)+1):
                yield i
        else:
            yield int(interval)

def preloaded_video_ids_array_to_intervals(preloaded_video_ids_array:list) -> str:
    """
    If the user ticked the checkboxes on the table and preloaded them, 
    st.session_state would contain the preloaded information and the
    text-input should consistently reflect this as well.

        tabular checkboxes -> [[st.session_state -> text input]]

    [Argument]
    checkboxes_list - ['✅ 3, 1eGPMBCkKH0', '✅ 4, ymArGFGA2C8', '✅ 5, j2CFny1yv9E']

    [Return]
    String of the form "1, 4-7, 10-13"
    This interval would be the default value in the text-input box.
    """
     
    # In case of empty list
    if preloaded_video_ids_array == None:
        return ""

    # Print out intervals
    video_nbs = [int(x.split(",")[0].split(" ")[1]) for x in preloaded_video_ids_array]
    video_nbs.sort()

    start_nb = None
    end_nb = None
    display_text = ""

    for index, nb in enumerate(video_nbs):

        # Initialise
        if start_nb == None:
            start_nb = nb
            end_nb = nb

        # Continuous
        if index < len(video_nbs) - 1 and video_nbs[index+1] == nb + 1:
            end_nb = nb + 1

        # Discontinuous
        else:
            if start_nb == end_nb:
                display_text += f"{start_nb},"
            else:
                display_text += f"{start_nb}-{end_nb},"

            start_nb = None
            end_nb = None

    # Truncate last comma
    display_text = display_text[:-1]

    return display_text

def get_ticked_preload_checkbox_rows(data_df_new:pd.DataFrame) -> list[str]:
    """
    From the tabular dataframe, users may tick checkboxes in the Preload column 
    to indicate which videos to preload.
    This function checks which checkboxes were ticked and returns them
    in a list of video_ids.

    [Arguments]
    data_df_new - updated dataframe of the table
    
    [Return]
    list of video ids
    """

    video_ids_to_preload = []
    for i, label in enumerate(data_df_new["Preload"]):
        if label == True:
            video_ids_to_preload.append(data_df.iloc[i]['Video ID'])

    return video_ids_to_preload

def get_ticked_access_checkbox_row(data_df:pd.DataFrame, data_df_new:pd.DataFrame) -> int:
    """
    From the tabular dataframe, users may tick a checkbox in the Access column 
    to access the video of that row. 
    This function checks returns the row that was ticked. 
    If no row has been ticked, return -1.

    [Arguments]
    data_df - dataframe of the table
    data_df_new - updated dataframe of the table
    
    [Return]
    row that the checkbox was ticked or -1 if no row was ticked
    """
        
    for i, (old_label,new_label) in enumerate(zip(data_df['Access'], data_df_new['Access'])):
        if old_label != new_label:
            return i
    return -1


def preload_images(video_ids_to_preload:list[str], step:int) -> None:
    """
    Preload images by pulling the images from the server.
    Additionally, provide a loading bar to indicate the progress of the preloading.

    [Arguments]
    video_ids_to_preload - list of video IDs
    step - to grab every n-th thumbnail

    [Return]
    none. The thumbnails are stored in memory (st.session_state).
    """

    progress_bar = st.progress(0,text="Preloading thumbnails...")

    for i, video_id in enumerate(video_ids_to_preload):
        try:
            st.session_state[f"{video_id}_4"] = get_images_from_server(video_id=video_id, n=step)
        except:
            st.text(f"Error for {video_id}")
        progress_bar.progress((i+1)/len(video_ids_to_preload),text=f"Preloaded thumbnails for {i+1}/{len(video_ids_to_preload)} videos")

    progress_bar.empty()
    st.session_state["preload_array"] = data_df_new["Preload"].tolist()

def check_if_video_id_preloaded(video_id:str) -> bool:
    """
    Check if the thumbnails for a given video_id has been preloaded
    and saved in st.session_state.

    [Argument]
    video_id 

    [Return]
    True/False
    """

    for key in list(st.session_state.keys()):
        pattern = re.compile(rf'^{video_id}[^_]*_[^_]*$')
        if pattern.match(key):
            return True
    return False


def switch_to_thumbnails_page(video_nb:int) -> None:
    """
    Switch to the thumbnails page while saving everything relevant
    into st.session_state.
    """
    st.session_state['video_nb'] = video_nb
    st.session_state['video_id'] = data_df.iloc[video_nb]['Video ID']
    st.session_state['video_name'] = data_df.iloc[video_nb]['Title']
    st.session_state['nb_frames'] = data_df.iloc[video_nb]['Total Frames']
    st.session_state['FPS'] = data_df.iloc[video_nb]['FPS']
    st.session_state['Duration'] = data_df.iloc[video_nb]['Duration']

    st.switch_page("pages/thumbnails.py")





################################################ 
#                Page Structure                #
################################################

#-----------------------#
#     SSH parameters    #
#-----------------------#
ssh_client = ssh_connect()

#------------------------------#
#     Dataframe processing     #
#------------------------------#
# Grab and process dataframe
data_df = get_csv_file()
data_df = data_df.drop(columns=['URL'])

# Grab labelling and thumbnails directories
thumbnails_dir_list = ssh_listdir(os.environ["thumbnails_dir"])
results_dir_list    = ssh_listdir(os.environ["results_dir"])

results_video_id_list = [x.split('.')[0] for x in results_dir_list]

# Generate list of visual cues to determine if thumbnails generated and thumbnails labelled
# These arrays are for the table on the main page for the Labelled, Preload, Access columns.
labelled_array = []
if "preload_array" in st.session_state:
    preload_array = st.session_state["preload_array"]
else:
    preload_array = [False] * len(data_df["Video ID"])
access_array = []
preloaded_video_ids_array = []

# Overall visualisation
ticks = 0
crosses = 0
waiting = 0

# Go through each video, we want to gather some useful statistics for visualisation
for video_nb, video_id in enumerate(data_df["Video ID"]):

    # Overall visualisation
    if video_id in results_video_id_list:
        labelled_array.append('✅')
        ticks += 1
    elif video_id in thumbnails_dir_list:
        labelled_array.append('❌')
        crosses += 1
    else:
        labelled_array.append('⏳')
        waiting += 1

    # If the video has been preloaded (available in st.session_state), 
    # indicate √ on access column and list on the selection box.
    if check_if_video_id_preloaded(video_id) == True:
        access_array.append(True)

        if video_id in results_video_id_list:
            preloaded_video_ids_array.append(f"✅ {video_nb}, {video_id}")
        else:
            preloaded_video_ids_array.append(f"❌ {video_nb}, {video_id}")
    else:
        access_array.append(False)




#=================#
#   Page Layout   #
#=================#

st.title(f'Preloading Overview ✅ {ticks} ❌ {crosses} ⏳ {waiting}')
st.text('')

step_slider = st.number_input("Thumbnails were generated for every 15 seconds of the video. Preload every n-th thumbnail", 
                              value=4, 
                              min_value=1, 
                              placeholder=4)
st.text(f'Preloading one thumbnail every {int(15*step_slider)} seconds.')
st.text('')
st.text('')

#~~~~~~~~~~~~~~~~~~~~~~~#
# Preloading text-input #
#~~~~~~~~~~~~~~~~~~~~~~~#

# Sort the text input by the first char ❌ followed by ✅
preloaded_video_ids_array = sorted(preloaded_video_ids_array, key=lambda x: x[0], reverse=True)


# The text-input itself
preload_range = st.text_input(label="To preload, enter a range OR tick the checkboxes in the table below THEN click the Preload button.", 
                              value=f"{preloaded_video_ids_array_to_intervals(preloaded_video_ids_array)}", 
                              help="e.g. 0-5, 7, 11, 13-15")

# Drop-down box when ≥1 pre-loaded video exists
if len(preloaded_video_ids_array) > 0: 
    access_selectbox = st.selectbox(label="Access a preloaded video", 
                                    index=None, 
                                    placeholder="Choose a preloaded video", 
                                    options=preloaded_video_ids_array)

    # Switch page when selected
    if access_selectbox != None:
        video_nb = int(access_selectbox.split(",")[0].split(" ")[1])
        switch_to_thumbnails_page(video_nb)


#~~~~~~~~~~~~~~~~~~~~#
# Dataframes Display #
#~~~~~~~~~~~~~~~~~~~~#

# For the Preload column
try: 
    preload_video_ids_generator = parse_ranges(preload_range)
    for i in preload_video_ids_generator: 
        preload_array[i] = True
        if i is None:
            break
except:
    if preload_range != "": 
        st.text("Invalid range input!")

data_df["Labelled"] = labelled_array
data_df["Preload"] = preload_array
data_df["Access"] = access_array
data_df = data_df

data_df_new = st.data_editor(
    data_df,
    column_config={
        "Access": st.column_config.CheckboxColumn(),
        "Preload": st.column_config.CheckboxColumn(),
    },
    disabled=["widgets"],
    hide_index=True,
    use_container_width=True,
    height=400,
)

#~~~~~~~~~~~~~~~~~~~#
# Preloading button #
#~~~~~~~~~~~~~~~~~~~#

# Gather what video_ids to preload
# If text-input was entered, the checkboxes would be updated. Consequently, this is accurate.
video_ids_to_preload = get_ticked_preload_checkbox_rows(data_df_new)

# The actual preload button
if st.button("Preload") and len(video_ids_to_preload) > 0:
    preload_images(video_ids_to_preload, step_slider)
    st.rerun()


#~~~~~~~~~~~~~~~~#
# Page switching #
#~~~~~~~~~~~~~~~~#
selected_video_nb = get_ticked_access_checkbox_row(data_df,data_df_new)
if selected_video_nb >= 0:
    switch_to_thumbnails_page(selected_video_nb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Page switching -- Continuous Labelling Mode #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

if "last_video_nb" not in st.session_state:
    pass   
if "last_video_nb" in st.session_state and st.session_state["continuous_labelling_mode"] == True:
    preloaded_video_nbs_array = [int(x.split(",")[0].split(" ")[1]) for x in preloaded_video_ids_array]
    for index, video_nb in enumerate(preloaded_video_nbs_array):
        if st.session_state["last_video_nb"] == video_nb and index < len(preloaded_video_nbs_array) - 1:
            video_nb = preloaded_video_nbs_array[index+1]
            switch_to_thumbnails_page(video_nb)
            break

"---"

#~~~~~~~~~~~~~~~~~~~#
# Labelling classes #
#~~~~~~~~~~~~~~~~~~~#
try:
    current_labelling_classes = ', '.join(st.session_state["labelling_classes"])
except:
    current_labelling_classes = "Interlude, NP"

st.title("Labelling Classes")
labelling_classes_text = st.text_input(label="Enter the labelling classes here separate with a comma", value=current_labelling_classes)
st.session_state["labelling_classes"] = [x.strip() for x in labelling_classes_text.split(',')]
