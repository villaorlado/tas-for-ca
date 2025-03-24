import streamlit as st
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import ssh_connect, ssh_listdir
from main import get_images_from_server
import re
import json

############################################### 
#                Design styling               #
###############################################

# CSS Layouts
css_style_true = """
    background-color: #ff0000; 
    background-image: linear-gradient(45deg, #bd820c 25%, transparent 25%), 
                    linear-gradient(135deg, #a64d4d 25%, transparent 25%), 
                    linear-gradient(45deg, transparent 75%, #f48989 75%), 
                    linear-gradient(135deg, transparent 75%, #ccc 75%);
    background-size: 5px 5px; 
    background-position: 0 0, 5px 0, 5px -5px, 0px 5px;
    padding: 5px; 
    display: flex; 
    justify-content: center;
    border-radius: 5px;
"""

css_style_false = """
    background-color: #bababa; 
    padding: 5px; 
    display: flex; 
    justify-content: center;
    border-radius: 5px;
"""

empty_text = """
<div style="text-align: center; font-size: 16px; font-weight: bold; color: rgba(186, 186, 186, 0);">
    ~
</div>
"""

def text_colours(nb_current_labels:int) -> str:
    if nb_current_labels == 1:
        return "e25d5d"
    elif nb_current_labels == 2:
        return "fa8340"
    elif nb_current_labels == 3:
        return "a201ff"
    
def font_weights(nb_current_labels:int) -> str:
    if nb_current_labels == 1:
        return str(100)
    elif nb_current_labels == 2:
        return str(500)
    elif nb_current_labels == 3:
        return str(900)

################################################ 
#       SSH Server interaction functions       #
################################################

def write_results_to_server(video_id:str, thumbnail_view_size:int, select_boxes:dict) -> None:
    """
    Save the results to the server

    [Arguments]
    video_id            - YouTube video ID of the video.
    thumbnail_view_size - how many n-th thumbnails were viewed
    select_boxes        - dictionary containing which thumbnails are selected
    """

    # Prepare data 
    labelled_intervals_dict = select_boxes_to_intervals(select_boxes)
    json_data = {
		"thumbnail_view_size": thumbnail_view_size,
		"data": labelled_intervals_dict
	}

    # Open connections
    ssh = ssh_connect()
    sftp = ssh.open_sftp()

    with sftp.file(f"{os.environ["results_dir"]}/{video_id}.json", "w") as remote_file:
        json.dump(json_data, remote_file)

    # Close the connections
    sftp.close()
    ssh.close()

def get_previous_select_boxes_result(video_id:str) -> dict:
    """
    If the result has already been saved on the server, we want to
    present which frames were selected. To do so, we call the 
    list of intervals stored in the file.

    Note that the saved data is a list of frame intervals whereas 
    the keys of the select_boxes are frame numbers. As such, 
    we will say that the new thumbnail is in the interlude 
    if it is contained within any of the intervals.

    [Argument]
    video_id - YouTube video ID of the video. 
               The video_id is the key and is used to name the folders in the SSH server.

    [Return]
    selected_intervals - dict containing the selected intervals and their corresponding labels.
                        {'label1' : [start1,end1], 'label2' : [start2,end2] , ... }
    """

    # Open connections 
    ssh = ssh_connect()
    sftp = ssh.open_sftp()

    try:
        with sftp.file(f"{os.environ["results_dir"]}/{video_id}.json", "r") as remote_file:
            data = json.load(remote_file)
        selected_intervals = data["data"]
    except:
        selected_intervals = {}

    # Close the connections
    sftp.close()
    ssh.close()

    return selected_intervals


############################################### 
#            Page Layout Functions            #   
###############################################

def display_images(filename_array:list[str], image_data_array:list[str], select_boxes:dict, nb_columns:int=5) -> dict:
    """
    After pulling the images from the server, we would want to render the thumbnails 
    for the user to perform the labelling. 

    [Arguments]
    filename_array - array containing filepath of every n-th thumbnail
    image_data_array - array containing image data  of every n-th thumbnail
    select_boxes - dictionary containing which thumbnails are selected -> {'frame_name' : list of selected labels }
    nb_columns - to display the thumbnails in {nb_columns} columns

    [Return]
    select_boxes - updated select_boxes variable    
    """

    # Parameters
    cols           = st.columns(nb_columns)
    current_labels = []

    for i, (filename, image_data) in enumerate(zip(filename_array,image_data_array)):

        # Organise into different columns
        with cols[i % nb_columns]:

            # When reloading from a saved copy, re-tick the relevant select_boxes
            with st.popover(label="✏️"):
                select_boxes[filename] = st.multiselect(label='Show Image', key=filename, options=st.session_state["labelling_classes"], label_visibility="hidden", default=select_boxes[filename])

            # Relevant HTML for thumbnails' background
            html_code_true = f"""
            <div style="{css_style_true}">
                <img src="data:image/png;base64,{image_data}" style="max-width: 100%;">
            </div>
            """

            html_code_false = f"""
            <div style="{css_style_false}">
                <img src="data:image/png;base64,{image_data}" style="max-width: 100%;">
            </div>
            """

            # Render the thumbnails, render the text, and keep track of the labelling intervals
            opened_labels = []
            closed_labels = []
            if select_boxes[filename] != []:

                st.markdown(html_code_true, unsafe_allow_html=True)

                for label in select_boxes[filename]:
                    
                    if label not in current_labels:

                        current_labels.append(label)
                        opened_labels.append(label)

                    else:
                    
                        current_labels.remove(label)
                        closed_labels.append(label)

                if opened_labels != [] and closed_labels == []:
                    display_text = f">>>>>>> {','.join(opened_labels)}"

                elif opened_labels == [] and closed_labels != []:
                    display_text = f"{','.join(closed_labels)} <<<<<<<"

                elif opened_labels != [] and closed_labels != []:
                    display_text = f"{','.join(closed_labels)} << || >> {','.join(opened_labels)}"

                else:
                    display_text = f"~~~ {len(current_labels)} ~~~"

    
                display_text_html = f"""
                <div style="text-align: center; font-size: 16px; font-weight: bold; color: #{text_colours(1)} ">
                    {display_text}
                </div>
                """
                st.markdown(display_text_html, unsafe_allow_html=True)


            elif current_labels != []:

                st.markdown(html_code_true, unsafe_allow_html=True)

                interlude_intermediate_text = f"""
                <div style="text-align: center; font-size: 16px; font-weight: {font_weights(len(current_labels))}; color: #{text_colours(len(current_labels))}">
                    ~~~~ {len(current_labels)} ~~~~
                </div>
                """

                st.markdown(interlude_intermediate_text, unsafe_allow_html=True)

            else:
                
                st.markdown(html_code_false, unsafe_allow_html=True)
                st.markdown(empty_text, unsafe_allow_html=True)
                    
            st.text('')

    return select_boxes

def select_boxes_to_intervals(select_boxes:dict) -> list[tuple[int,int]]:
    """
    Process the select_boxes data such that when the data is reloaded, it can
    be adapted to any number of n-th thumbnail. 
    For example, if thumbnail (frame 450) was selected, the next time the data is reloaded,
    it may not necessarily include the same thumbnail (frame 450).

    [Argument]
    select_boxes - dictionary containing which thumbnails are selected -> {'frame_name' : list of selected labels}

    [Return]
    selected_intervals - list of intervals (tuple(int,int)) containing 
                         which frames the interlude start and end in tuple form (start, end)
    """

    largest_frame_nb = int(max(select_boxes.keys(), key=lambda x: int(x.split('.')[0])).split('.')[0])

    # Process the select_boxes data
    labelled_frames_dict = {}

    # Go through each frame one-by-one and check if there's a label.
    for frame_name, labels in select_boxes.items():
        if labels != []:

            # For each label, append the frame nb when it appears.
            for label in labels:

                frame_nb = int(frame_name.split(".")[0])
                if label in labelled_frames_dict.keys():
                    labelled_frames_dict[label].append(frame_nb)
                else:
                    labelled_frames_dict[label] = [frame_nb]

    # If the labels were not closed at the very end, we end it with the last frame
    for label, labelled_frame_nbs in labelled_frames_dict.items():
        if len(labelled_frame_nbs) % 2 == 1:
            labelled_frames_dict[label].append(largest_frame_nb)

    # Organise it into list of tuples
    labelled_intervals = {}
    for label, labelled_frames in labelled_frames_dict.items():
        labelled_interval = []
        for i in range(0, len(labelled_frames), 2):
            labelled_interval.append([labelled_frames[i], labelled_frames[i+1]])
        labelled_intervals[label] = labelled_interval

    return labelled_intervals

def select_interlude_intervals(video_id:str, filename_array:list[str]) -> dict:
    """
    We first retrieve the data from the server. 
    The data is in the form of a dictionary.
    The keys are the label names and the values are the list of intervals.

    For every label and for every interval, we select the option for that particular frame when:
    - the first thumbnail >= start frame_number
    - the last thumbnail immediately <= end frame_number.
    This criteria is 

    [Arguments]
    video_id - YouTube video ID of the video. 
               The video_id is the key and is used to name the folders in the SSH server.
    filename_array - array containing filepath of every n-th thumbnail

    [Return]
    select_boxes - dictionary containing boolean values of whether the thumbnail is in the interlude (selected_intervals)
    """

    # Get previous results
    stored_file = get_previous_select_boxes_result(video_id)

    # Exit function if stored_file is empty
    if stored_file == {}:
        select_boxes = {}
        for filename in filename_array:
            select_boxes[filename] = []
        
        return select_boxes

    # If stored_file is not empty, we shall go through each frame one-by-one. 
    # The filename contains the frame number.
    select_boxes = {}

    for label, intervals in stored_file.items():

        # Parameters
        interval_nb = 0 
        in_interlude = False
        interval_check = True
        prev_filename = None
        if len(intervals) > 0:
            start, end = intervals[interval_nb]

        for filename in filename_array:

            if filename is None:
                continue

            # Initialise
            frame_nb = int(filename.split('.')[0])

            if filename in select_boxes:
                pass
            else:
                select_boxes[filename] = []
    
            if len(intervals) > 0 and intervals != [] and frame_nb >= int(start) and interval_check == True and in_interlude == False:
                select_boxes[filename].append(label)
                in_interlude = True

            elif len(intervals) > 0 and intervals != [] and frame_nb > int(end) and interval_check == True and in_interlude == True:

                select_boxes[prev_filename].append(label)
                in_interlude = False
                interval_nb += 1

                if int(interval_nb) == len(intervals):
                    interval_check = False 
                else:
                    start,end = intervals[interval_nb]
                
            else:
                pass

            prev_filename = filename

    return select_boxes

@st.cache_resource
def get_preloaded_images(video_id:str, step:int) -> tuple[list[str], list[str]]:
    """
    Retrieve the preloaded thumbnails from st.session_state.
    If it doesn't exist, pull them from the server immediately now.

    [Arguments]
    video_id - YouTube video ID of the video. 
    step     - extract every n-th thumbnail

    [Return]
    tuple of the following:
        filename_array   - array containing filepath of every n-th thumbnail
        image_data_array - array containing image data  of every n-th thumbnail
    """

    key = f"{video_id}_{step}"
    if key not in st.session_state:
        st.session_state[key] = get_images_from_server(video_id=video_id, n=step)
    return st.session_state[key]

def get_key_name(video_id:str) -> str:
    """
    st.session_state can contain the names of every thumbnail as well.
    Consequently, there would be many keys that start with the video ID.
    To extract the correct key, we use this RegEx pattern.

    [Argument]
    video_id - YouTube video ID of the video. 

    [Return] 
    key_name - If it exists, the key name in st.session_state that contains the preloaded thumbnails.
               Otherwise, None.
    """

    pattern = re.compile(rf'^{video_id}[^_]*_[^_]*$')
    for key_name in list(st.session_state.keys()):
        if pattern.match(key_name):
            return key_name
    
    return None

################################################ 
#                Page Structure                #
################################################

#-------------------#
#  SSH parameters   #
#-------------------#
ssh_client = ssh_connect()

#-------------------#
#  Page parameters  #
#-------------------#

# From main page
if 'video_id' in st.session_state:
    video_nb    = st.session_state['video_nb']
    video_id    = st.session_state['video_id']
    video_name  = st.session_state['video_name']
    nb_frames   = st.session_state['nb_frames']
    duration    = st.session_state['Duration']
    fps         = st.session_state['FPS']
else:
    st.text("directing you to the main page immediately")
    st.session_state["continuous_labelling_mode"] = False
    st.switch_page("main.py")
    


# Session state values from reloads of this thumbnails page
if 'select_boxes' in st.session_state:
    select_boxes     = st.session_state['select_boxes']
    filename_array   = st.session_state['filename_array']
    image_data_array = st.session_state['image_data_array']
    overwrite        = st.session_state['overwrite']
    results_uploaded = st.session_state['results_uploaded']
else:
    select_boxes = {}
    filename_array = []
    image_data_array = []
    overwrite = False
    results_uploaded = False

# Check if previous result exists
results_dir_list = ssh_listdir(os.environ["results_dir"])
results_video_id_list = [x.split('.')[0] for x in results_dir_list]

if video_id in results_video_id_list:
    previous_result_exists = True
else:
    previous_result_exists = False

# Thumbnails calculation
nb_thumbnails = int(nb_frames/(fps * 15)) + 1

#-------------#
# Page Layout #
#-------------#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Overvall Visualisation section #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Navigation buttons
if st.button("Home"):
    st.session_state["continuous_labelling_mode"] = False
    st.switch_page("main.py")

# Title and subheaders
if previous_result_exists == True:
    st.title(f'✅ Video {video_nb}, {video_id}')
else:
    st.title(f'❌ Video {video_nb}, {video_id}')

st.subheader(video_name)
st.subheader(f'{duration} seconds, {fps} FPS, {nb_frames} frames')
st.subheader(f'{nb_thumbnails} thumbnails')

"---"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Thumbnails parameters section #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


# Render pre-loaded thumbnails
key_name = get_key_name(video_id)
if key_name is not None:
    step_val = int(key_name.split('_')[-1])
    filename_array, image_data_array = get_preloaded_images(video_id, step_val)
    select_boxes = select_interlude_intervals(video_id, filename_array)
    st.text("Preloaded thumbnails have been rendered below.")
else:
    step_val=4

st.text('Thumbnails were generated for every 15 seconds of the video.')
step_slider = st.number_input("Grab every n-th thumbnail", value=step_val, min_value=1, placeholder=step_val)
st.text(f'Displaying one thumbnail every {int(15*step_slider)} seconds. Total of {int(nb_thumbnails/step_slider) + 1} thumbnails.')

if st.button("Generate thumbnails") == True:
    filename_array, image_data_array = get_preloaded_images(video_id, step_slider)
    select_boxes = select_interlude_intervals(video_id, filename_array)

"---"

#~~~~~~~~~~~~#
# Thumbnails #
#~~~~~~~~~~~~#

if image_data_array != []:

    # Slider to adjust how many columns
    st.subheader("Number of columns to display thumbnails")
    nb_columns = st.slider(label="Number of columns to display thumbnails", value=10, min_value=4, max_value=15, label_visibility="hidden")

    "---"
    
    # Display thumbnails
    select_boxes = display_images(filename_array, image_data_array, select_boxes, nb_columns)

    "---"

    # Submission of results
    if previous_result_exists == True:
        if st.checkbox("Overwrite existing results?",value=False):
            overwrite = True

    if previous_result_exists == False or (previous_result_exists == True and overwrite == True):
        if st.button('Submit labelling results to server'):
            write_results_to_server(video_id, step_val, select_boxes)  
            st.text("Results uploaded!")
            st.session_state["last_video_nb"] = video_nb
            st.session_state["continuous_labelling_mode"] = True
            results_uploaded = True
            
            st.switch_page("main.py")
    
if results_uploaded == True:

    if st.button("Go Home!"):
        st.session_state["continuous_labelling_mode"] = False
        st.switch_page("main.py")

#-----------------------#
# Session State Storage #
#-----------------------#
st.session_state['select_boxes']      = select_boxes
st.session_state['filename_array']   = filename_array
st.session_state['image_data_array'] = image_data_array
st.session_state['overwrite']        = overwrite
st.session_state['results_uploaded'] = results_uploaded
