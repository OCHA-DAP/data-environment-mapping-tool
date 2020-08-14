# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 15:01:43 2020

Descrption: Case study record linkage attempt for 3 datasets relating to
            Afghanistan

REquirements: recordlinkage, pandas
@author: cmcinerney
"""


import pandas as pd
import recordlinkage


from recordlinkage.preprocessing import clean, phonetic

#Import datasets
PATH_REACH_DATASET = "C:/Users/cmcinerney/Desktop/UNOCHA Fellowship/Afghanistan_microdata/Case study datasets/Harmonised/reach_afg_dataset_protection_assessment_of_conflict_affected_populations_may2018_harmonised.xlsx"

PATH_REACH17_DATASET = "C:/Users/cmcinerney/Desktop/UNOCHA Fellowship/Afghanistan_microdata/Case study datasets/Harmonised/reach_afg_dataset_mcna_aug2017_harmonised.xlsx"

PATH_SDC_DATASET = "C:/Users/cmcinerney/Desktop/UNOCHA Fellowship/Afghanistan_microdata/Case study datasets/Harmonised/sdc-afg-msna-microdata-harmonised.xlsx"



df_reach18 = pd.read_excel(PATH_REACH_DATASET)
df_reach17 = pd.read_excel(PATH_REACH17_DATASET)
df_sdc = pd.read_excel(PATH_SDC_DATASET)

# =============================================================================
# Preprocessing the data to increase likelihood of finding linkages
# =============================================================================
#string variables to clean
df_reach18.province = clean(df_reach18.province, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach18.district = clean(df_reach18.district, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach18.origin_country = clean(df_reach18.origin_country, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach18.origin_province = clean(df_reach18.origin_province, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach18.hoh_sex = clean(df_reach18.hoh_sex, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach18.hoh_dis = clean(df_reach18.hoh_dis, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')

df_sdc.province = clean(df_sdc.province, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_sdc.district = clean(df_sdc.district, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_sdc.hoh_sex = clean(df_sdc.hoh_sex, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')

df_reach17.province = clean(df_reach17.province, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach17.district = clean(df_reach17.district, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach17.hoh_sex = clean(df_reach17.hoh_sex, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach17.hoh_dis = clean(df_reach17.hoh_dis, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach17.origin_country = clean(df_reach17.origin_country, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')
df_reach17.origin_province = clean(df_reach17.origin_province, lowercase=True, replace_by_none='[^ \\-\\_A-Za-z0-9]+', replace_by_whitespace='[\\-\\_]', strip_accents=None, remove_brackets=True, encoding='utf-8', decode_error='strict')


#phonetic encoding for place names
# df_reach18.province = phonetic(df_reach18.province, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')
# df_reach18.district = phonetic(df_reach18.district, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')
# df_reach17.province = phonetic(df_reach17.province, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')
# df_reach17.district = phonetic(df_reach17.district, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')
# df_sdc.province = phonetic(df_sdc.province, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')
# df_sdc.district = phonetic(df_sdc.district, method = 'soundex', concat=True, encoding='utf-8', decode_error='strict')



# =============================================================================
# Subset data so that it only contains Pakistani refugees (this is a type of blocking?)
# =============================================================================

df_reach18_ref = df_reach18[df_reach18.displacement_status == 'Refugee']
df_reach17_ref = df_reach17[df_reach17['displacement/are_displaced_afghan'] == 'no'] 
df_sdc_ref = df_sdc[df_sdc.refugees == 'yes']



# =============================================================================
# Indexing - make record pairs
# =============================================================================

#start with two reach datasets
print(len(df_reach18_ref)* len(df_reach17_ref))
# =516,060 possible pairs

# df_reach18_ref['province'].value_counts()
# df_reach17_ref['province'].value_counts()

# df_reach18_ref['district'].value_counts()
# df_reach17_ref['district'].value_counts()


#Blocking - only comparing pairs of records that are identical on some attributes
indexer = recordlinkage.Index()
blocking_vars = ["province", "displacement_year"] #, 'displacement_month','arrival_month','hoh_sex','hoh_age','hh_size','hh_families'
indexer = recordlinkage.BlockIndex(on=blocking_vars)
candidate_links = indexer.index(df_reach18_ref, df_reach17_ref)
print (len(candidate_links))
# = 134,220

# =============================================================================
# Compare records
# =============================================================================

# initialise class
comp = recordlinkage.Compare()

# initialise similarity measurement algorithms
#displacement info
comp.string('district', 'district', method='jarowinkler', label = 'district')
comp.numeric('displacement_month', 'displacement_month', label = 'displacement_month')
comp.numeric('arrival_month', 'arrival_month', label = 'arrival_month')
comp.numeric('arrival_year', 'arrival_year', label = 'arrival_year')
comp.string('origin_province', 'origin_province', method='jarowinkler', label = 'origin_province')



#household head attributes
comp.exact('hoh_sex', 'hoh_sex', label = 'hoh_sex')
comp.numeric('hoh_age', 'hoh_age', offset  = 2, label = 'hoh_age') #if age is =- 2 years then exact match
comp.string('hoh_dis', 'hoh_dis', method='jarowinkler', label = 'hoh_dis')

#household attributes
comp.exact('hh_families', 'hh_families', label = 'hh_families')
comp.numeric('hh_size', 'hh_size', label = 'hh_size')
comp.numeric('female_children', 'female_children', label = 'female_children')
comp.numeric('male_children', 'male_children', label = 'male_children')
comp.numeric('female_adults', 'female_adults', label = 'female_adults')
comp.numeric('male_adults', 'male_adults', label = 'male_adults')
comp.numeric('female_elders', 'female_elders', label = 'female_elders')
comp.numeric('male_elders', 'male_elders', label = 'male_elders')



# the method .compute() returns the DataFrame with the feature vectors.
features = comp.compute(candidate_links, df_reach18_ref, df_reach17_ref)


# =============================================================================
# Classification step
# =============================================================================

# Classification step
matches = features[features.sum(axis=1) > 15]
print(len(matches))

#write out matches to a html file
#render dataframe as html
html = matches.to_html()

#write html to file
text_file = open("index.html", "w")
text_file.write(html)
text_file.close()



df_reach18_ref_subset = df_reach18_ref[["province", "district", "displacement_year", 'displacement_month', "origin_province", 'arrival_month','hoh_sex','hoh_age', "hoh_dis", 'hh_size','hh_families','female_children','female_adults','female_elders','male_children','male_adults','male_elders']]
df_reach17_ref_subset = df_reach17_ref[["province", "district", "displacement_year", 'displacement_month', "origin_province", 'arrival_month','hoh_sex','hoh_age', "hoh_dis", 'hh_size','hh_families','female_children','female_adults','female_elders','male_children','male_adults','male_elders']]



recordlinkage.write_annotation_file(
    "annotation_carol.json",
    candidate_links[0:51],
    df_reach18_ref_subset,
    df_reach17_ref_subset,
    dataset_a_name="df_reach18_ref",
    dataset_b_name="df_reach17_ref"
)


result = recordlinkage.read_annotation_file('annotation_carol_result.json')
print(result.links)

poss_link18 = df_reach18_ref.loc[10407,:]
poss_link17 = df_reach17_ref.loc[6432,:]
