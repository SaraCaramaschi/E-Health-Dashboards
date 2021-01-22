import numpy as np
import urllib.request
from Pubmed_functions import * 

query = 'Neurostimulators'

# Code needed to get all pmids. Runned once only and then saved the pmids on a .txt files
"""pmids_list_new = get_pmids(query)"""

# Opening the .txt file containing all the pmids
filename = 'pmid-Neurostimulators.txt'   
with open(filename) as f:
    pmids_list_new = f.readlines() 
    pmids_list_new = [x.strip() for x in pmids_list_new] 

# Code needed to save all of the XML files on local memory
"""       
papers = []
for i,pmid in enumerate(pmids_list_new):
    tmp = PubMedPaper(pmid)
    papers.append(tmp)
    print(str(tmp.pmid)+str(i))
    xml =  open("XML/"+str(tmp.pmid)+"_"+ str(i)+ ".xml", "w")
    xml.write(tmp.xml)
    xml.close() """
    
# Papers exploited to create ground truth relevance array
pmids_list = ['33157936','33129672','33038597','32989306','32746060','32722055','32716692','32709183','32690786','32689698','32689697',
'32689696','32606311','32581744','32532923','32516574','32462381','32427546','32353166','32348644','32333552','32329803','32313193',
'32302732','32297491','32271689','32180722','32158975','32139653','32112934','32076132','32072621','32037855','32032787','31965667',
'31946710','31946709','31946173','31923435','31899396', '31889312','31805511','31804975','31786379','31775407','31759615','31756502',
'31739771','31710411','31703815','31701891','31699912','31699407','31685241','31685239','31685237','31677739','31648825','31648824','31634136',
'31597122', '31587955', '31584846', '31574517', '31537819', '31536974', '31520484', '31508904', '31505718', '31498396', '31495733', 
 '31487526', '31484132', '31480034', '31466022', '31443868', '31442766', '31428199', '31419794', '31401488', '31399570', '31388779',
 '31377911', '31377743', '31368415', '31362277', '31358822', '31347955', '31336436', '31323175', '31322465', '31321763', '31321466',
 '31318829', '31310417', '31302380', '31295615', '31291123', '31288242', '31280257', '31265205', '31226620', '31219619', '31197426', 
 '31190100', '31157949', '31139864', '31133406', '31107559', '31096260', '31093277', '31084350', '31063589', '31062294', '31059853',
 '31054557', '31054337', '31053055', '31044466', '31042596', '31035839', '31034008', '31018908', '31018187', '30997509', '30985902',
 '30985873', '30970205', '30947360', '30941558', '30929666', '30923287', '30920919', '30915982', '30903858', '30892717', '30889467',
 '30878509', '30860268', '30860266', '30857472', '30851040', '30850259', '30849436', '30842036', '30834611', '30833216', '30809700',
 '30802868', '30799493', '30794909', '30790780', '30784113', '30771997', '30729252', '30729038', '30704683', '30690434', '30684944',
 '30667299', '30635485', '30629245', '30620935', '30599493', '30592526', '30588762', '30558717', '30553618', '30549045', '30526131',
 '30500485', '30487205', '30474259', '30473473', '30444276', '30444012', '30430373', '30403281', '30399090', '30360936', '30355456',
 '30350488', '30347509', '30346640', '30335761', '30320739', '30303994', '30295628', '30291521', '30270483', '30267724', '30249417',
 '30243756', '30242519', '30241957', '30238573', '30236810', '30220068'] 

# Removing ground truth articles papers from the new ones
count=0
for i,pmid in enumerate(pmids_list_new): 
    if pmid in pmids_list: 
        print(i)
        count = count+1
        del(pmids_list_new[i])

# Obtaining dictionaries of neurostimulators and of the different types of studies
dict_name_neuro = 'Neurostimulators_dictionary.txt'
neuro_dictionary = get_neuro_dict(dict_name_neuro)
study_dictionaries = get_study_dict()

# Obtaining information relative to every papers 
titles,abstracts,study_types, key_words, years = info_neurostimulators(pmids_list)
titles_new,abstracts_new,study_types_new,key_words_new, years_new = info_neurostimulators(pmids_list_new)

# Characterisation of the study type of every paper based on study type dictionaries
studies = characterisation(titles, abstracts, study_types, key_words, study_dictionaries)
studies_new = characterisation(titles_new,abstracts_new,study_types_new,key_words_new, study_dictionaries)

# Ground truth definition of relevance for 198 papers 
relevance_gt = [0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,0,0,0,0,0,1,1,0,1,0,1,0,1,1,0,0,0,1,1,0,1,0,
                  0,1,1,1,0,0,0,1,1,0,1,1,0,0,0,1,0,0,1,1,1,0,1,0,1,1,0,0,1,1,1,0,0,1,0,1,0,1,0,1,0,1,1,0,0,
                  1,0,1,1,0,1,1,1,0,0,1,1,1,0,1,1,1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 
                  0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 
                  1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                  0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

relevance_gt_new = [] 

# Validation of the identification algorithm 
relevance = identification(titles, abstracts, key_words, studies, neuro_dictionary)  
rel_df = pd.DataFrame(relevance) 
rel_gt_df = pd.DataFrame(relevance_gt) # corretto
c = confusion_matrixx(relevance_gt,relevance)
precision,sensitivity,accuracy = prec_rec(c)
print('GT\n',rel_gt_df[0].value_counts())
print('PRED\n',rel_df[0].value_counts())


# Application of the algorithm to the new data 
relevance_new = identification(titles_new,abstracts_new,key_words_new, studies_new, neuro_dictionary)

# Creating the dataframes 
df_papers = build_dataframe(pmids_list, titles,studies, key_words, years, relevance_gt, relevance)
df_papers.columns =['Pmid', 'Title','Study Type','Key Words','Pub year','Relevance GT','Relevance PRED'] 
 
df_papers_new =  build_dataframe(pmids_list_new, titles_new,studies_new, key_words_new, years_new, relevance_gt_new, relevance_new)
df_papers_new.columns =['Pmid', 'Title','Study Type','Key Words','Pub year','Relevance PRED'] 

# All of the papers together
df_papers_tot = pd.concat([df_papers, df_papers_new], ignore_index=True, sort=False)
# Mantaining information of papers considered 'relevant'
df_papers_rel = df_papers_tot[df_papers_tot['Relevance PRED']==1]

# Saving the dataframes
outfname = 'df_papers.csv'
outpath = 'datasources/' + outfname
df_papers_tot.to_csv(outpath, index=False)

outfname1 = 'df_papers1.csv'
outpath1 = 'datasources/' + outfname1
df_papers_rel.to_csv(outpath1, index=False)






