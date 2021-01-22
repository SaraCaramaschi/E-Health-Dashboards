import pandas as pd
import os
from scholarly import scholarly as sc
import re
#from concurrent.futures import ThreadPoolExecutor
import nltk

stopwords = nltk.corpus.stopwords.words("english")


def data_preparation():
    # Loading csv
    path_dev = "datasources/devices.csv"
    path_man = "datasources/manufacturers.csv"
    path_ev = "datasources/events.csv"

    devices = pd.read_csv(path_dev, low_memory=False)
    manufacturers = pd.read_csv(path_man, low_memory=False)
    events = pd.read_csv(path_ev, low_memory=False)
    
    # Selection most important features
    events.loc[events['type'] == 'Recall / Safety alert', 'type'] = 'Recall / Safety Alert'
    events1 = events[["id", "action_summary", "country", "slug", "type", "device_id","date"]]
    devices1 = devices[["id", "name", "description", "classification", "slug", "country", "implanted", "manufacturer_id"]]
    manufacturers1 = manufacturers[["id", "slug","name",'parent_company','source','updated_at']] 

    # Merging dataframe by specific ID
    df = pd.merge(events1, devices1, left_on='device_id', right_on='id', how='left')
    df1 = pd.merge(df, manufacturers1, left_on='manufacturer_id', right_on='id', how='left')
    df1.drop(['id_y', 'id', 'slug_x', 'country_x'], axis=1, inplace=True)

    df1.rename(columns={'name_x': 'device_name', 'slug_x': 'device_slug','id_x':'event_id',
                                'name_y': 'manufacturer_name', 'slug_y': 'manufacturer_slug',
                                'date': 'event_date', 'country_y': 'country'}, inplace=True)
    
    to_replace = ['Cardiovascular Devices', 'Gastroenterology-Urology Devices', 'Neurological Devices', 'Dental Devices', 'Obstetrical and Gynecological Devices']
    replacing = ['Cardiology', 'Gastroenterology', 'MentalHealthAndNeurology', 'Dentistry', 'GinecologyAndObstetrics']
    
    df1['classification'] = df1['classification'].replace(to_replace, replacing)
    devices1['classification'] = devices1['classification'].replace(to_replace, replacing)
 
    return events1, devices1, manufacturers1, df1

# Percentage of relevant papers
def info_df_papers(df_papers): 
    gt_perc = 0
    tot = 198
    for i,rel in enumerate(df_papers['Relevance GT'].tolist()):
        #print(i)
        if rel == 1:
            gt_perc += 1
            
    pred_perc = 0
    for i,rel in enumerate(df_papers['Relevance PRED'].tolist()):
        if rel == 1:
            pred_perc += 1
    
    return (gt_perc)/tot, (pred_perc)/tot

# Year specification (used in dashboards)
def find_year(events):
    col_date = events['date']
    date = col_date.unique().tolist()
    anni_=[]
    anni = []
    for i in range(len(date)): 
        if type(date[i])==str:
            data = date[i]
            anni_.append(data[0:4])
    [anni.append(item) for item in anni_ if item not in anni]
    del(anni[-1])
    del(anni[-1])
    del(anni[-1])
    del(anni[-1])
    anni.reverse()
    anni.sort()
    return anni 

def anni_df(events_1c):
    anni_ita_ = []
    for data in events_1c['date'].tolist():
        if type(data)==str:  
            anni_ita_.append(data[0:4])
    df_anni = pd.DataFrame(data=anni_ita_, columns=["y"])
    labels = sorted(df_anni['y'].value_counts().index.tolist())
    return labels  
        
        
# Year specification (used in dashboards)
def calcolo_years(events_1c, labels):
    res = {}
    for data in events_1c['date'].tolist():
        for year in labels:
            if year in data:
                if year not in res.keys():
                    res[year] = '1'
                else: 
                    intero = int(res[str(year)])
                    intero += 1
                    res[str(year)] = str(intero)
    res = sorted(res.items())
    values=[]
    for i in range(len(res)):
        print(i)
        values.append(res[i][1])
    return values

# Uploading dictionaries used for category selection
def get_dictionaries():
    path = "Dictionaries/"
    dict_list = os.listdir(path)
    total_dict = {}
    #print(dict_list)
    for name in dict_list:
        list_0 = []
        lista = []
        path_name = path + name
        with open(path_name, 'r') as fp:
            name = re.sub('.txt', '', name)
            list_0 = fp.readlines()
        for element in range(len(list_0)):
            list_0[element] = re.sub('-', ' ', list_0[element])
            list_0[element] = re.sub(',', '', list_0[element])
            list_0[element] = list_0[element].split()
        for elemento in range(len(list_0)):
            for lemma in range(len(list_0[elemento])):
                lista.append(list_0[elemento][lemma])

        lista = lower_case(lista)
        lista = remove_stop_words(lista)
        lista = remove_double_from_dict(lista)

        total_dict[name] = lista

    return total_dict

# Text editing
def lower_case(lista):
    for i in range(len(lista)):
        lista[i] = lista[i].lower()
    return lista

# Text editing
def remove_stop_words(lista):
    stop_words = stopwords
    new_list = []
    for w in lista:
        if w not in stop_words and len(w) > 1:
            new_list.append(w)
    return new_list

# Removing double words present in the dictionaries
def remove_double_from_dict(lista):
    new = []
    for i,term in enumerate(lista):
        if term not in new:
            new.append(term)  
    return new

# Obtaining abstract list from Google Scholar
def get_abstract(name):
    try:
        query = sc.search_pubs(name)
    except: None
    abs_list = []
    index = 0
    while index < 5:
        abstract = ''
        try:
            abstract = next(query).bib['abstract']
        except: None
          
        abs_list.append(abstract)
        index += 1

    for n_abs in range(len(abs_list)):
        abs_list[n_abs] = re.sub('-', ' ', abs_list[n_abs])
        abs_list[n_abs] = re.sub(',', '', abs_list[n_abs])
        abs_list[n_abs] = abs_list[n_abs].split()      
    return abs_list

# Assignment of score based on word frequency 
def get_score(abstract, dictionary, num):
    frequenze = []
    somma = 0
    i = 0
    for term in dictionary:
        frequenze.append(abstract.count(str(term)))
        somma = somma + frequenze[i]
        i += 1
    return somma

# Defining the category of a single abstract
def single_cat(abstract, dictionaries, num):
    score = []
    count = 0
    max = 0
    # print("For abstract number :", num)
    for dict_name in dictionaries:
        score.append(get_score(abstract, dictionaries[dict_name], num))
        #print("\nDictionary:" + str((list(dictionaries))[count]) + ", score: \f", score[-1])
        if score[-1] >= score[max]:
            max = count
        count = count + 1
    if score[max] == 0:
        #print(" No dictionaries matched")
        category = None
    else:
        category = str((list(dictionaries))[max])
    return category

# Defining the final category of the device based on the category obtained from all the abstracts
def get_category(name, dictionaries):
    abstracts = get_abstract(name)
    categories = []
    num = 0
    for abstract in abstracts:
        if abstract == '':
            categories.append(None)
        else:
            categories.append(single_cat(abstract, dictionaries, num))
        num += 1
    freq = []
    maximum = 0
    count = 0
    for element in categories:
        if element is not None:
            if element not in freq:
                freq.append(categories.count(element))
                if freq[count] >= freq[maximum]:
                    maximum = count
            count += 1
    #print(categories)
    categories = list(filter(None, categories))

    if not categories:
        #print("The category for this medical device stays Nan")
        winner_category = 'None'
    else:
        #print("Most frequent categories that have been found: ")
        #print(categories)
        winner_category = categories[maximum]
        #print("The winner category relative to the medical device: " + name + ", is: " + winner_category)

    return winner_category


# General function that would add the computed category to devices who actually have missing values in the classification field
def updating_classification(df, dictionaries):
    # Getting the category of the device and filling up the classification column:
    index_true = df['classification'].isna()  # TRUE DOVE C'è nan
    for a in range(0, 12):
        b = (10000*a)+1
        c = b + 9999
        for i in range(b, c):
            if index_true[i]:
                name = df['device_name'].iloc[i]
                df['classification'].replace(df['classification'].iloc[i], get_category(name, dictionaries), inplace=True)
                #df["classification"].iloc[i] = get_category(name, dictionaries)
        outfname = 'df_10000_cat_'+str(a)+'.csv'
        outpath = 'saved_files/' + outfname
        df.to_csv(outpath, index=False)
    print(df['classification'].head())
    

#with ThreadPoolExecutor(max_workers=3) as executor:
#    executor.submit(get_abstract)
#    executor.submit(get_category)
#    executor.submit(updating_classification)



        
   