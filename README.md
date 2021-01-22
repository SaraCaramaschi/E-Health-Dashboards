# E-Health-Dashboards
Dashboards coming from INCJ Database

Libraries needed to run all the codes: 
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import collections
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

import urllib.request
from bs4 import BeautifulSoup
from sklearn.metrics import confusion_matrix
import nltk 
import os
from scholarly import scholarly as sc
import re

What you need to do to visualize DASHBOARDS: 
0. For reasons of folders dimension and Beep available space, we had to remove the 'interpreter' folder. 
We ask you to add yours from your PyCharm version in the folder '1_dashboard_group8'

1. Open 'Dashboard_main.py' and RUN it
2. Copy and paste your local host address on your browser to see the dashboards

3. IF you want to see how we worked on Pubmed Papers: 
Open ‘Pubmed_main.py’ and RUN it, it can require a bit of time

Objects contained in '1_dashboard_group8' folder: 
Python files: 
- Dashboard_main.py: DASHBOARD MAIN CODE. This is the only code that needs to be run and that will make you visualize all the dashboards
- Dashboard_functions.py: file that contains all of the functions exploited to visualize correct dashboards
- Pubmed_main.py: code that we exploited to download .xml files on local computer and manage their information
- Pubmed_functions.py: file that contains all of the functions exploited to extract information from .xml files

Folders: 
- datasources: folder containing all the .csv 
- XML: folder containing all the .xml files of the Pubmed papers
- studyType_dictionaries: folder containing dictionaries relative to the study type
- Dictionaries: folder containing dictionaries relative to medical device classification
- interpreter: folder needed to correctly run PyCharm 
	
Other files contained in the Project folder: 
- pmid-Neurostimulators.txt: TXT file containing all of the PMIDS from Pubmed. This file is needed in order not to download every time all of the papers pmids list from Pubmed

