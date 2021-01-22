import urllib.request
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from sklearn.metrics import confusion_matrix
import nltk 
 
stopwords = nltk.corpus.stopwords.words("english")

# Class definition for a single article
class PubMedPaper():                            # automatically extracts data from the paper
    def __init__(self, pmid):                   # method
        self.pmid = pmid                        # variable of self (input of the class) = pmid
        self.xml = self.__get_xml()
        
    def __get_xml(self):
        base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + self.pmid + '&retmode=xml'
        # http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=33157936&retmode=xml
        query_result = urllib.request.urlopen(base_url).read()
        query_str = query_result.decode('utf-8')       
        return query_str
 
# Function that provides pmids 
def get_pmids(query,pmids_list):
    base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    fetch_1 = 'esearch.fcgi?db=pubmed&term='
    fetch_2 = '&retmode=xml&RetMax=30000'

    final_query = ''

    query_list = query.split(' ')
    for word in query_list:
        final_query += word
        if word != query_list[-1]:
            final_query += '+'      # smartphone+app+heart

    url = base_url + fetch_1 + final_query + fetch_2
    query_result = urllib.request.urlopen(url).read()

    regex_res = re.findall('<Id>.*?</Id>', str(query_result))
    output = []

    for pmid in regex_res:
        tmp = re.sub('<.*?>', '', pmid)
        if tmp not in pmids_list:
            output.append(tmp)
            
    return output

# Function that loads the neurostimulators dictionary 
def get_neuro_dict(dict_name):
    path ="Dictionaries/"
    path_name = path + dict_name
    dictionary = []
    list_1 = []
    with open(path_name, 'r') as fp:
        dict_name = re.sub('.txt', '', dict_name)
        dictionary = fp.readlines()
        for term in dictionary: 
            term = re.sub('\n', '', term)
            term = utils_preprocess_text(term, flg_stemm=False, flg_lemm=False, lst_stopwords=None)
            list_1.append(term)            
    return list_1

# Function that loads the study types dictionaries 
def get_study_dict():
    path = "studyType_dictionaries/"
    dict_list = os.listdir(path)
    total_dict = {}
    #print(dict_list)
    for name in dict_list:
        list_0 = []
        list_1 =[]
        path_name = path + name
        with open(path_name, 'r') as fp:
            name = re.sub('.txt', '', name)
            list_0 = fp.readlines()
            del(list_0[0])
            for term in list_0: 
                term = re.sub('\n', '', term)
                list_1.append(term)
        total_dict[name] = list_1
    #total_dict['RCT'].append('Series')
    total_dict['ObservationalStudy'].append('Research')
    return total_dict

# Confusion matrix function
def confusion_matrixx(y_true,y_pred):
    matrix = confusion_matrix(y_true, y_pred)
    matrix = pd.DataFrame(matrix)
    print('True P - False P, sotto: False N, True N')
    print(matrix) 
    return pd.DataFrame(matrix)

# Other statistics 
def prec_rec(c): 
    #tp = c[0][0]
    tn = c[0][0]
    tp = c[1][1]
    fp = c[1][0]
    fn = c[0][1]
    precision = ( tp / (tp+fp) )*100            
    sensitivity = ( tp / (tp + fn) )*100  
    accuracy = ( (tp+tn) / (tp+tn+fp+fn) )*100
    print('prec', precision)
    print('acc', accuracy)
    print('sens', sensitivity)
    
    return precision, sensitivity, accuracy

# Score definition 
def get_score(ogg, dictionary):
    frequenze = []
    somma = 0
    for i,term in enumerate(dictionary):
        frequenze.append(ogg.count(term))
        somma = somma + frequenze[i]
    return somma

# Characterisation algorithm 
def characterisation(titles, abstracts, study_types, key_words, study_dictionaries):    
    
    combination = [] 
    for i,studio in enumerate(study_types):
        tmp = studio + titles[i] + abstracts[i] + key_words[i]
        #print(str(i)+','+tmp)
        combination.append(tmp)
     
    studies_multi = []
    for i,element in enumerate(combination):
        if study_types[i] == '\nJournal Article\n': 
            studies_multi.append('ObservationalStudy')
        else:
            studies_multi.append(single_type(element, study_dictionaries))
            
    for i,studio in enumerate(studies_multi): 
        cohort=0
        case=0
        if studio == 'ObservationalStudy':
            for term in study_dictionaries['CohortStudy']: 
                if term in combination[i]:
                    cohort+=1
            for term in study_dictionaries['CaseSeries']:
                if term in abstracts[i]:
                    case +=1 
                if term in titles[i]: 
                    case += 1
        if cohort>case: 
            studies_multi[i] = 'CohortStudy'
        elif cohort<case: 
            studies_multi[i] = 'CaseSeries'
            
    return studies_multi

# Definition of a single study type            
def single_type(ogg, dictionaries):
    score = []
    count = 0
    max = 0
    for dict_name in dictionaries:
        score.append(get_score(ogg, dictionaries[dict_name]))
        if score[-1] >= score[max]:
            max = count
        count += 1
    if score[max] == 0:
        ogg = None
    else:
        ogg = str((list(dictionaries))[max])
    return ogg

# Identification algorithm 
def identification(titles, abstracts, key_words, studies, neuro_dictionary):
    relevance = []

    combination = [] 
    for i,studio in enumerate(studies):
        if type(studio) == str:
            tmp = studio +' '+ abstracts[i] + ' ' + abstracts[i] + ' ' + abstracts[i]+ ' ' + titles[i] + ' ' + abstracts[i] + ' ' +key_words[i]
            tmp_cleaned = utils_preprocess_text(tmp, flg_stemm=False, flg_lemm=True, lst_stopwords=stopwords)
        else: 
            tmp = abstracts[i] + ' ' + abstracts[i] + ' ' + titles[i] + ' ' + abstracts[i] + ' ' + key_words[i] + ' ' + abstracts[i]
            tmp_cleaned = utils_preprocess_text(tmp, flg_stemm=False, flg_lemm=True, lst_stopwords=stopwords)
        combination.append(tmp_cleaned)
        
    studi= {'RCT':2,'CohortStudy':0,'CaseControl':0,'CaseSeries':0,'ObservationalStudy':0,
                     'Other':0,'SystematicReview':2,'MetaAnalysis':2}
                      
    soglia = 2
    for i,elemento in enumerate(combination): 
        score = 0 
        
        for term in neuro_dictionary:
            if term in elemento: 
                score += 1
        if type(studies[i])==str:
           score += studi[studies[i]]
            
        print(score)
        if score > soglia: 
            relevance.append(1)
        else: relevance.append(0)
        

    return relevance


# Function gathering information from the XML of the papers   
def info_neurostimulators(pmids_list) :
    xml_files = []
    for i,pmid in enumerate(pmids_list): 
        path ='XML/'
        path_name = path + pmid + "_" + str(i) + ".xml"
        #print(path_name)
        with open(path_name, 'r') as f: 
            tmp = f.read()
            xml_files.append(tmp)    
           
    titles=[]
    abstracts=[]
    study_types=[]
    key_words = []
    years = []
    
    for i,xml in enumerate(xml_files): 
        #print(i)
        tmp = xml
        soup = BeautifulSoup(tmp, 'html.parser')   
        
        title = soup.articletitle
        try:
            title = title.get_text()
            titles.append(title)
        except: 
            titles.append('')
        
        abstract = soup.abstract
        try:
            abstract = abstract.get_text()
            abstracts.append(abstract)
        except: 
            abstracts.append('')
            
        study_type = soup.publicationtypelist
        try:
            study_type = study_type.get_text()
            study_types.append(study_type)
        except: 
            study_types.append('')
            
        key_word = soup.keyword
        try:
            key_word = key_word.get_text()
            key_words.append(key_word)
        except: 
            key_words.append('')
        
        try: 
            date = soup.pubdate.year
        except: years.append('')
        try:
            date = date.get_text()
            years.append(date)
        except: 
            years.append('')
    
    return titles, abstracts, study_types, key_words, years 


# Function that processes text  
# source of the code: 
# https://towardsdatascience.com/text-analysis-feature-engineering-with-nlp-502d6ea9225d
def utils_preprocess_text(text, flg_stemm=False, flg_lemm=True, lst_stopwords=stopwords):
    '''
    Preprocess a string.
    :parameter
    :param text: string - name of column containing text
    :param lst_stopwords: list - list of stopwords to remove
    :param flg_stemm: bool - whether stemming is to be applied
    :param flg_lemm: bool - whether lemmitisation is to be applied
    :return: cleaned text
        '''

    ## clean (convert to lowercase and remove punctuations and characters and then strip)
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
            
    # Tokenize (convert from string to list)
    lst_text = text.split()
    
    # Removing Stopwords
    if lst_stopwords is not None:
        lst_text = [word for word in lst_text if word not in 
                    lst_stopwords]
                
    # Stemming (remove -ing, -ly, ...)
    if flg_stemm == True:
        ps = nltk.stem.porter.PorterStemmer()
        lst_text = [ps.stem(word) for word in lst_text]
                
    # Lemmatisation (convert the word into root word)
    if flg_lemm == True:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) for word in lst_text]
            
    # back to string from list
    text = " ".join(lst_text)
    return text
    
# Function that builds the dataframe  
def build_dataframe(pmids_list,titles,studies,key_words,years,relevance_gt,relevance_pred):
    df_pmid = pd.DataFrame(pmids_list)
    df_tit = pd.DataFrame(titles)
    df_stud = pd.DataFrame(studies)
    df_key = pd.DataFrame(key_words)
    df_year = pd.DataFrame(years)
    df_rel_gt = pd.DataFrame(relevance_gt)
    df_pred = pd.DataFrame(relevance_pred)
    df_paper = pd.concat([df_pmid,df_tit,df_stud,df_key,df_year,df_rel_gt, df_pred], axis=1)
    
    return df_paper
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    