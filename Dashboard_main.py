import Dashboard_functions as f
import pandas as pd
import plotly.graph_objects as go
import collections
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

############################ DATA PREPARATION ################################

events, devices, manufacturers, df = f.data_preparation()
dictionaries = f.get_dictionaries()

################## FILLING NAN OF CLASSIFICATION DATAFRAME COLUMN ############

print('Actual missing values in the classification feature: ', df['classification'].isnull().sum())
"""f.updating_classification(df, dictionaries)
# This operation requires really high computation times 

print('Number of missing values once the classification feature has been modified:', len(df[df['classification'] == 'None']))

# Saving the updated dataframe (only 100 items)
outfname = 'datafram_1000_cat_'+str(a)+'.csv'
outpath = 'saved_files/' + outfname
df.to_csv(outpath, index=False)
"""


################################## DASHBOARD #################################

## Initial dashboard settings
external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
app= dash.Dash(__name__, external_stylesheets=external_stylesheets)
background_color = '#b3cde0'


## Feature extraction
countries_tot = list(devices.country.unique()) 
categories = list(devices.classification.unique())
risk = df[['description','country']]
anni = f.find_year(events)

# Features related to different countries
device_sum_country = devices['country'].value_counts() 
device_list_country = device_sum_country.tolist()         
device_index_country = device_sum_country.index.tolist()  

# Features related to different events' type
events_sum_type = events['type'].value_counts()
events_list_type= events_sum_type.tolist()              
events_index_type = events_sum_type.index.tolist()

# Features related to different events' type and country
event_sum_country = events['country'].value_counts() 
event_list_country = event_sum_country.tolist()          
event_index_country = event_sum_country.index.tolist()

# Features related to all PubMed papers(df_papers) and to only relevant PubMed papers(df_papers1) 
path = "datasources/df_papers.csv"
path1 = "datasources/df_papers1.csv"
df_papers = pd.read_csv(path, low_memory=False)
df_papers1 = pd.read_csv(path1, low_memory=False)

df_papers['Pub year'] = df_papers['Pub year'].fillna(0)
df_papers1['Pub year'] = df_papers1['Pub year'].fillna(0)
df_papers['Pub year'] = df_papers['Pub year'].astype(int)
df_papers1['Pub year'] = df_papers1['Pub year'].astype(int)


# Features related to the characterisation of all papers
char_sum = df_papers['Study Type'].value_counts()
char_frequency =  char_sum.tolist()
char_index = char_sum.index.tolist()

# Features related to the characterisation of relevant papers
char_sum1 = df_papers1['Study Type'].value_counts()
char_frequency1 =  char_sum1.tolist()
char_index1 = char_sum1.index.tolist()

# Collecting countries with the same type of event in a dictionary
tipi = df['type'].unique().tolist()
dic = {}
for tipo in tipi:
    #print(tipo)
    dic[tipo]=[]
    for country in countries_tot:
        df_country = df[df['country']== country] 
        if len(df_country['type'].unique().tolist()) == 1: 
            tipo_selezioanto = df_country['type'].unique().tolist()[0]
            if tipo == tipo_selezioanto: 
                dic[tipo].append(country)

titles = df_papers1['Title'].tolist()
gt_perc, pred_perc = f.info_df_papers(df_papers1)

            
## LAYOUT DEFINITION   

# First tab layout definition. General overview of the ICIJ Database and insight 
# relative to a selected country and over a certain period of time 
layout1 = html.Div([
         html.H1("Dashboard of ICIJ Medical Devices", 
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px', 'marginBottom': 50,'font-weight': 'bolder','margin-top':'70px'}), 
         html.H2("Country selection: ", style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50}),     
         html.H2("Selecting the countries: ITA, TUR or FRA, you will have further insights about the produced medical devices",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50,'font-size':'28px'}),  
         html.Div([ 
                 dcc.Dropdown(                          
                     id="country",
                     options=[{'label': country, 'value': country} for country in countries_tot] 
                     ),
                 ], style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 12,'background-color':background_color}),
         
         html.Div([
            html.Div([
                #html.H3('Distribution of devices per country ',style={'margin-left':'50px','marginBottom': 50}),
                dcc.Graph(id='devices_graph',style={'width':'95%','vertical-align':'top','margin-left':'50px','margin-top':'50px'})], className="six columns"),
            html.Div([
                #html.H3('Distribution of events per country',style={'margin-left':'50px','marginBottom': 50}),
                dcc.Graph(id='events_country',style={'width':'95%','vertical-align':'top','margin-left':'50px','margin-top':'50px'})],className="six columns"),
            ],className='row'),
                                 
         html.H1("Analysis over a selected period of time",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
         html.H2("Slide until the desired date",style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50}), 

         html.Div([
             dcc.Slider(
            id="year", min=min(anni), max=max(anni), value=min(anni),
            marks={str(year): str(year) for year in anni},step=1
            )
        ],style={'width': '60%','font-weight':'bolder','margin-left':'560px'}),
          
         html.Div([],id='years_events_country',
             style={'width':'70%','vertical-align':'top','margin-left':'500px','margin-top':'50px'}),

         html.Div([],id='risk', 
                  style={'width':'70%','vertical-align':'top','margin-left':'500px','margin-top':'50px'}),
                  
          html.H2('We can state that the unique type of event often depends on the selected country. It is possible to verify that selecting the desired country and checking the correspondent pie graph',
                  style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': '50','margin-top':'50px'}),
          html.H4('Field Safety Notice event type : {}'.format(dic[tipi[0]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),
          html.H4('Safety Alert event type : {}'.format(dic[tipi[1]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),
          html.H4('Recall event type : {}'.format(dic[tipi[2]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),
          html.H4('Recall/Safety Alert event type : {}'.format(dic[tipi[3]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),
          html.H4('Recall/Field Safety Notice event type : {}'.format(dic[tipi[4]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),
          html.H4('Safety Alert/Field Safety Notice event type : {}'.format(dic[tipi[6]]),
            style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50}),


     ],style={'background-color': background_color})  

# Second tab layout definition. Insights relative to a specific category and to its main parent companies  
layout2 = html.Div([
         html.H1("Dashboard of Medical Devices specific for a single category",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50,'font-weight': 'bolder','margin-top':'70px'}),
         html.H2("Category selection:",style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50}), 
         html.Div([
             dcc.Dropdown(
             id = "cat",
             options=[{'label':category,'value':category} for category in categories]
             ),
        ],style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 12}),

        html.H1("Analysis of the number of devices and type of event belonging to a single category",
                style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
        html.Div([
            html.Div([
                html.Div([],id='n_dev_category',style={'width':'95%','vertical-align':'top','margin-left':'50px','margin-top':'50px'})], className="six columns"),
            html.Div([
                html.Div([],id='events_setcat',style={'width':'95%','vertical-align':'top','margin-left':'50px','margin-top':'50px','margin-right':'50px'})],className="six columns")
            ],style={'background-color':background_color},className='row'),
        
        html.H1("Parent companies and relavtive manufacturers belonging to the chosen category",
                style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
        html.Div([],id='manufacturers_category',style={'width':'85%','vertical-align':'top','margin-left':'170px','margin-top':'50px'}),
        html.Div([],id='manuf_action',style={'width':'85%','vertical-align':'top','margin-left':'170px','margin-top':'50px'}),
        html.Div([],id="manufacturers_category_man",style={'width':'85%','vertical-align':'top','margin-left':'170px','margin-top':'50px'})
        
],style={'background-color':background_color})

# Third tab layout definition. Insights relative to Neurostimulator devices, exploiting PubMed as a research tool.
layout3 = html.Div([
         html.H1("Insights relative to neurostimulator devices",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','marginBottom': 50,'font-weight': 'bolder'}),
         html.Div([ 
             html.Button('Show dashboards', id='show', n_clicks=0),
          ], style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 20,'background-color':background_color}),
       
         html.H1("Characterisation of the study type of all anlaysed papers (on the left) and of the relevant papers (on the right) and below we reported the identification of the relevance of all papers",
                style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
         html.H2("The relevance of the papers is based on an identification algortihm",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50}),     

         html.H2("Total number of analysed papers: 4217",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50}),     
    
         html.Div([
             html.Div([
                 html.Div([],id='char',  
                      style={'vertical-align':'top','margin-top':'50px'})],className="six columns"),
             html.Div([
                 html.Div([],id='char1',  
                      style={'vertical-align':'top','margin-top':'50px'})],className="six columns"),    
         ],style={'background-color':background_color},className='row'),
         
         html.Div([],id='rel', style={'width':'60%','vertical-align':'top','margin-top':'50px','margin-left':'600px'}),
         html.Div([],id='years', style={'width':'60%','vertical-align':'top','margin-top':'50px','margin-left':'600px'}),
         
         html.H1("Download the dataframe related to the relevant scientific articles of neurostimulators",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
         html.Div([html.Button("Download csv of relevant papers", id="btn1"), Download(id="download1")],
                  style={'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 12}),

         html.H1("Download the dataframe related to all 4217 PubMed results",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'70px','marginBottom': 50,'font-weight': 'bolder'}),
         html.Div([html.Button("Download csv of all papers", id="btn"), Download(id="download")],
                  style={'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 12}),
    ],style={'background-color': background_color})


         #html.Div([ 
             #dcc.Dropdown(                          
             #id="title", options=[{'label': title, 'value': title} for title in titles])
                 #], style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50, "font-size": 12,'background-color':'#457b9d'}),
         


## MANAGING DAHSBOARD UPDATES 

# Selection of the specific tab
@app.callback(                                          
    Output('tabs-example-content', 'children'),
    [Input('tabs-icij', 'value')])

def render_content(tab):
    if tab == 'tab-1':
        return layout1
    elif tab == 'tab-2':
        return layout2
    elif tab == 'tab-3':
        return layout3

 
# Layout 1 updates

@app.callback(                                      
    Output('devices_graph', 'figure'),
    [Input('country', 'value')]) 

# Number of devices per country 
def update_graph_devicespercountry(country):
    if country == None:        
        device_list_country = devices['country'].value_counts().tolist()
        trace = go.Bar(x=device_index_country, y=device_list_country, name='Number of devices')
        layout = go.Layout(title='Distribution of medical devices in the whole world',font=dict(size=18))
    else:
        devices_1country = devices[devices['country'] == country]
        device_index_1country = devices_1country['country'].value_counts().index.tolist()  
        device_freq_1country = devices_1country['country'].value_counts().tolist() 

        trace = go.Pie(labels=device_index_1country, values=device_freq_1country, name='Number of device',
                     textinfo='value', textfont_size=60, showlegend=False)
        layout = go.Layout(title='Number of devices for {}'.format(country), font=dict(size=18))


    return { 'data': [trace],'layout': layout}
        


@app.callback(
    Output('events_country', 'figure'),
    [Input('country', 'value')])

# Type of events per country
def update_graph_eventspercountry(country):
    if country == None:
        figure={'layout': {'title': 'Different type of events in the world',
                           'font':{'size':'18'} 
                           },
            'data': [
                {'values': events_list_type,    
                 'labels': events_index_type,  
                 'type': 'pie',                
                 'name': 'Ships'}]}
        return figure
    else:
        df_country = df[df['country']==country]
        events_type1 = df_country['type'].value_counts()
        events_list1 = events_type1.tolist()               
        events_index1 = events_type1.index.tolist()
        figure={'layout': {'title': 'Different type of events for the selected country {}'.format(country),
                          'font':{'size':'18'},
                          'legend':{'orientation':"h"}
                          },
            'data': [
                {'values': events_list1,    
                 'labels': events_index1,   
                 'type': 'pie',                
                 'name': 'Ships'}]}
        
        return figure
    

@app.callback(
    Output('years_events_country', "children"),
    [Input("year", "value"),
    Input("country","value")],
    [State('years_events_country', "children")])

# Amount of events per year in that country    
def update_years_events_country(year, country, children):
    print(year)
    print(country)
    events_1c = events[events['country']==country]
    
    for i,anno in enumerate(anni):
        if anno==str(year):
            index_year = i # 11
    labels = anni[0:index_year+1] 
    
    labels1 = f.anni_df(events_1c)
    values = f.calcolo_years(events_1c,labels) 
    trace = go.Pie(labels=labels1, values= values, name='Amount of events from 1999 to the selected year',
                     textinfo='value', textfont_size=20, showlegend=True)
    if country and year: 
        if children:
            children[0]["props"]["figure"] = {"data": [trace],"layout": go.Layout(title='Amount of events from 1999 to the selected year: {}, in {}'.format(year,country),font=dict(size=18), legend=dict(orientation="h"))}
        else:
            children.append(
                dcc.Graph(
                    figure={"data": [trace],"layout": go.Layout(title='Amount of events from 1999 to the selected year: {}, in {}'.format(year,country),font=dict(size=18), legend=dict(orientation="h"))})
                    )
    return children

@app.callback(
    Output('risk', "children"),
    [Input("country","value")],
    [State('risk', "children")])

# Associated description for selected countries (ITA,FRA,TUR)
def update_risk(country, children):

    print(country)
    risk_val = [] 
    if country == 'ITA':
        risk_ita = risk[risk['country']=='ITA']
        risk_index = ['md','ivd','aimd']
        for elemento in risk_index:
            df_tmp = risk_ita[risk_ita['description']==elemento]
            risk_val.append(len(df_tmp))
        risk_index = ['Medical_Device','In_Vitro_MD','Active_Implantable_MD']
    
    if country == 'TUR': # 1,2a,2b,3
        risk_tur = risk[risk['country']=='TUR'] 
        to_replace = ['Class I - other','AIMDD','Class I - Other','IVD A 2-List B','Class I - sterile','IVD Other']
        replacing = ['Class I','Class III','Class I','Class III','Class I','Class III']
        risk_tur['description'] = risk_tur['description'].replace(to_replace, replacing)
        risk_index = risk_tur['description'].value_counts().index.tolist()
        risk_val = risk_tur['description'].value_counts().values.tolist()
    
    if country == 'FRA':
        risk_fra = risk[risk['country']=='FRA']
        risk_index = risk_fra['description'].value_counts().index.tolist() 
        risk_val = risk_fra['description'].value_counts().values.tolist()
            
    trace = go.Pie(labels=risk_index, values=risk_val, name='Distribution of medical device description',
                     textinfo='value', textfont_size=20, showlegend=True)
    
    if country: 
        if children:
            children[0]["props"]["figure"] = {"data": [trace],"layout": go.Layout(title='Distribution of medical device description in {}'.format(country),font=dict(size=18),legend=dict(orientation='h'))}
        else:
            children.append(
                dcc.Graph(
                    figure={"data": [trace],"layout": go.Layout(title='Distribution of medical device description in {}'.format(country),font=dict(size=18),legend=dict(orientation='h'))}
                    )
                )
    return children
        

# Layout 2

@app.callback(
    Output("n_dev_category", "children"),
    [Input("cat", "value")],
    [State("n_dev_category", "children")])

# Number of devices per single category 
def update_n_dev_category(var, children):
    print(var)
    devices_1cat = devices[devices['classification'] == var] 
    device_index_1cat = devices_1cat['classification'].value_counts().index.tolist() #x
    device_freq_1cat = devices_1cat['classification'].value_counts().tolist() #y
    trace2 = go.Pie(labels=device_index_1cat, values=device_freq_1cat,
                     textinfo='value', textfont_size=60, showlegend=False)
    if var:
        if children:
            children[0]["props"]["figure"] = {"data": [trace2],"layout": go.Layout(title='Number of medical devices of {} category'.format(var),font=dict(size=18))}
        else:
            children.append(
                dcc.Graph(
                    figure={"data": [trace2],"layout": go.Layout(title='Number of medical devices of {} category'.format(var),font=dict(size=18))})
                        )
    return children


@app.callback(
    Output("events_setcat", "children"),
    [Input("cat", "value")],
    [State("events_setcat", "children")])

# Type of events of a single category 
def update_graph_events_setcat(var,children):
    df_cat = df[df['classification']==var]
    events_type1cat = df_cat['type'].value_counts()
    events_list1 = events_type1cat.tolist() #y              
    events_index1 = events_type1cat.index.tolist()#x
    trace = go.Pie(labels=events_index1, values=events_list1)
    
    if var:
        if children:
            children[0]["props"]["figure"] = {"data": [trace],"layout": go.Layout(title='Different type of events for {} category'.format(var),font=dict(size=18))}
        else:
            children.append(
                dcc.Graph(
                    figure={"data": [trace], "layout": go.Layout(title='Different type of events for {} category'.format(var),font=dict(size=18))})
                        )
    return children

@app.callback(
    Output("manufacturers_category", "children"),
    [Input("cat", "value")],
    [State("manufacturers_category", "children")])

# Top 10 parent companies according to the number of associated events! 
def update_graph_manufacturer_cat(cat,children):
    print(cat)
    manufacturers_cat = df[df['classification'] == str(cat)]
   #manufacturers_cat = manufacturers_cat[['event_id','type','device_id','device_name','manufacturer_id','parent_company','manufacturer_name']]
    res = manufacturers_cat['parent_company'].value_counts()
    labels = res.index[0:10].tolist()
    values = res.values[0:10].tolist()
    
    fig = {
            'data': [
                {'x': labels, 'y': values, 'type': 'bar',
                 'line':{'shape':'hv'}
                 },
            ],
            'layout': {
                'title': '10 parent company with highest number of associated events for the {} category'.format(cat),
                'yaxis':{'title':'Number of associated events'},
                'font':{'size':'18'}    
            }
        }
    if cat:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(
                    figure=fig
                      )
                ) 
    return children 

    
            
"""    if cat:
        if children:
            children[0]["props"]["figure"] = {"data": [dict(x=labels, y=values, textfont_size=50,fillcolor=dict(color='rgba(246, 78, 19, 0.6)', width=3),line=dict(shape='hv'))],
                                              "layout": go.Layout(title='10 parent company with highest number of associated events for the {} category'.format(cat),                                       
                                                yaxis=dict(title='Number of associated events')
                                                )}
        else:
            children.append(
                dcc.Graph(
                    figure={"data": [dict(x=labels, y=values, textfont_size=50,fillcolor=dict(color='rgba(246, 78, 19, 0.6)', width=3),line=dict(shape='hv'))], 
                            "layout": go.Layout(title='10 parent company with highest number of associated events for the {} category'.format(cat),  
                                                yaxis=dict(title='Number of associated events')
                                                )
                            }
                      )
                )  """ 
    

@app.callback(
    Output("manufacturers_category_man", "children"),
    [Input("cat", "value")],
    [State("manufacturers_category_man", "children")])

# Among the parent companies that have more associated events, highlight the manufacturers with highest number of associated events
def update_parent_events(cat,children):
    manufacturers_cat = df[df['classification'] == str(cat)]
    pc_top10 = manufacturers_cat['parent_company'].value_counts().index[0:10].tolist() # top 10 with associated events 
    man_top10 = manufacturers_cat[manufacturers_cat['parent_company'].isin(pc_top10)] # manufacturers of the top10 parent
    #man_top10 = man_top10[['event_id','type','device_id','device_name','manufacturer_id','parent_company','manufacturer_name']]
    values = man_top10['manufacturer_name'].value_counts().values[0:10].tolist()
    labels = man_top10['manufacturer_name'].value_counts().index[0:10].tolist()
 
    fig = {
            'data': [
                {'x': labels, 'y': values, 'type': 'bar', 'name': 'manuf_action'},
            ],
            'layout': {
                'title': '10 manufacturers with highest number of associated events (Belonging to the 10 parent companies mentioned above)',
                'yaxis':{'title':'Number of associated events'},
                'font':{'size':'18'}    
            }
        }
    
    if cat:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children


@app.callback(
    Output("manuf_action", "children"),
    [Input("cat", "value")],
    [State("manuf_action", "children")])

# Top 10 parent companies and the relative number of action summaries applied
def update_manuf_events(cat,children):
    manufacturers_cat = df[df['classification'] == str(cat)]
    mantop10 = manufacturers_cat['parent_company'].value_counts().index[0:10].tolist()
    totals = manufacturers_cat['parent_company'].value_counts().values[0:10].tolist()
    action_sum = []
    for i,man in enumerate(mantop10): 
        df_man = manufacturers_cat[manufacturers_cat['parent_company']==man]
        action_sum.append(sum(df_man['action_summary'].value_counts().tolist()) / totals[i])
    fig = {
            'data': [
                {'x': mantop10, 'y': action_sum, 'type': 'bar', 'name': 'manuf_action'},
            ],
            'layout': {
                'title': 'Proportioned number of action summaries associated to events of the top 10 parent companies', 
                'height': 700,
                'yaxis':{'tickformat' : "%"},
                'font':{'size':'18'}    
            }
        }
    
    if cat:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children



# Layout 3

@app.callback(
    Output('container-button-basic', 'children'),
    [Input('show', 'n_clicks')],
    [State('input-on-submit', 'value')])

def update_output(n_clicks, value):
    return 'The input value was "{}" and the button has been clicked {} times'.format(
        value,
        n_clicks
    )

@app.callback(
    Output('result_pmid', 'children'),
    [Input('title', 'value')]
)
def update_pmid(title):
    print(title)
    if title:
        df = df_papers[df_papers['Title']==title]
        pmid = df['Pmid'].tolist()[0]
        #to_print = "The pmid of the selected paper is {} The computed study type of the selectd paper is {} {}According to the ground truth is the selected paper relevant? {}".format(str(pmid),"\n",study_type,"\n",rel)
        return "The pmid of the selected paper is {}".format(pmid)

@app.callback(
    Output('result_studytype', 'children'),
    [Input('title', 'value')]
)    
def update_studytype(title):
    if title:
        df = df_papers[df_papers['Title']==title]
        study_type = df['Study Type'].tolist()[0]
        return "The computed study type of the selectd paper is {}".format(study_type)
    
@app.callback(
    Output('result_relevance', 'children'),
    [Input('title', 'value')]
)    
def update_relevance(title):
    if title:
        df = df_papers[df_papers['Title']==title]
        rel = df['Relevance GT'].tolist()[0]
        if rel == 0: 
            out = 'Yes'
        else: out = 'No'
        
        return "According to performed analysis is the selected paper relevant? {}".format(out)


@app.callback(
    Output("char", "children"),
    [Input('show', 'n_clicks')],
    [State("char", "children")])

def update_char(show,children):
    fig = {
            'data': [
                {'x': char_index, 'y': char_frequency, 'type': 'bar', 'name': 'char'},
            ],
            'layout': {
                'title': 'Characterisation of the study type of all selected papers', 
                'height': 700,
                'xaxis' : {'title' : 'Study types',"height": 700},
                'yaxis':{'title':'Study types frequency',"height": 700},
                'font':{'size':'18'}    
            }
        }
    
    if show:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children

@app.callback(
    Output("char1", "children"),
    [Input('show', 'n_clicks')],
    [State("char1", "children")])

def update_char1(show,children):
    fig = {
            'data': [
                {'x': char_index1, 'y': char_frequency1, 'type': 'bar', 'name': 'char'},
            ],
            'layout': {
                'title': 'Characterisation of the study type of considered relevant papers about Neurostimulators', 
                'height': 700,
                'xaxis' : {'title' : 'Study types',"height": 700},
                'yaxis':{'title':'Study types frequency',"height": 700},
                'font':{'size':'18'}    
            }
        }
    
    if show:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children

@app.callback(
    Output("rel", "children"),
    [Input('show', 'n_clicks')],
    [State("rel", "children")])

def update_rel(show,children): 
    values = df_papers['Relevance PRED'].value_counts().tolist()
    labels = df_papers['Relevance PRED'].unique().tolist()
    fig = {
            'data': [
                {'x': labels, 'y': values, 'type': 'bar', 'name': 'char'},
            ],
            'layout': {
                'title': 'Relevance predicted over all analysed papers', 
                'height': 700,
                'xaxis' : {'title' : 'Relevance', 
                           "height": 700, 
                           'tickmode':'array',
                           'tickvals':[0,1], 
                           'ticktext':['Non Relevant', 'Relevant']},
                'yaxis':{'title':'Frequency',"height": 700},
                'font': {'size':'18'}    
            }
        }
    
    if show:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children

@app.callback(
    Output("years", "children"),
    [Input('show', 'n_clicks')],
    [State("years", "children")])

def update_years(show,children): 
    sort_y = sorted(df_papers['Pub year'])
    counter=collections.Counter(sort_y)
    labels = list(counter.keys())[1:-1]
    values = list(counter.values())[1:-1]
    fig = {
            'data': [
                {'x': labels, 'y': values, 'type': 'bar', 'name': 'char'},
            ],
            'layout': {
                'title': 'Distribution of published papers over the years', 
                'height': 700,
                'xaxis' : {'title' : 'Published year', 
                           "height": 700},
                'yaxis':{'title':'Frequency',"height": 700},
                'font': {'size':'18'}    
            }
        }
    
    if show:
        if children:
            children[0]["props"]["figure"] = fig
        else:
            children.append(
                dcc.Graph(figure=fig))
    return children

# DOWNLOAD BUTTON 
@app.callback(Output("download", "data"), 
              [Input("btn", "n_clicks")])

def generate_csv(n_nlicks):
    return send_data_frame(df_papers.to_csv, filename="download_df1.csv")
        
@app.callback(Output("download1", "data"), 
              [Input("btn1", "n_clicks")])

def generate_csv1(n_nlicks):
    return send_data_frame(df_papers1.to_csv, filename="download_rel_df1.csv")


######################### LAYOUT GROUPING  
app.layout = html.Div([
    dcc.Tabs(id='tabs-icij', value='tab-1', children=[
        dcc.Tab(label='General overview', value='tab-1'),
        dcc.Tab(label='Category information', value='tab-2'),
        dcc.Tab(label='Neurostimlutators information', value='tab-3')
    ]),
    html.Div(id='tabs-example-content')
])


# end 
if __name__ == '__main__':
    app.run_server()
    
    
"""
html.H2("Select a single title from PubMed resources: ",
                 style={'width': '55%', 'vertical-align':'top','margin-left':'50px','marginBottom': 50,'font-weight': 'bolder'}),          
        
        

         html.Div(id='result_pmid',style={'font-size':'30px','margin-left':'50px'}), #,'font-weight': 'bolder'
         html.Div(id='result_studytype',style={'font-size':'30px','margin-left':'50px'}),
         html.Div(id='result_relevance',style={'font-size':'30px','margin-left':'50px'}),           
         html.H5("Percentage of relevant papers in the ground truth selection: {:.1%}".format(gt_perc),
                 style={'font-size':'30px','width': '55%', 'vertical-align':'top','margin-left':'50px','margin-top':'50px','margin-bottom': '50'}),
         html.H5("Percentage of relevant papers in the prediction performance: {:.1%}".format(pred_perc),
                 style={'font-size':'30px','width': '55%', 'vertical-align':'top','margin-left':'50px','margin-bottom': '50'}),

"""

    

