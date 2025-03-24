**Wayang Kulit Labelling** <br />
Contains a Streamlit interface to label video thumbnails as 'interlude' or not."

**Installation** <br />
```bash
pip install -r requirements.txt
```

**First Steps**
1. Before starting, create a folder called .streamlit
2. Within the folder, create a file called secrets.toml
3. The file will contain username, password, and IP address of the SSH server
4. Populate the text file in the following manner:
   
&nbsp;&nbsp;&nbsp;&nbsp;[ssh_details]<br />
&nbsp;&nbsp;&nbsp;&nbsp;hostname = "XX.XX.XX.XX"<br />
&nbsp;&nbsp;&nbsp;&nbsp;username = "user"<br />
&nbsp;&nbsp;&nbsp;&nbsp;password = "pass"<br />

*(Remember to add this file into your .gitignore to prevent leakage of your details!)*

5. Launch streamlit with
     streamlit run main.py



     
