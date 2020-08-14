# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 14:09:22 2020

Description: creates a graph and visualises it, saving a gexf and html file in
            specified location. The nodes of the graph represent one dataset
            and an edge between two nodes indicates if those datasets have 
            variables (column headers) and/or hxls in common. The datasets can
            be downloaded from HDX for a specified country and/or tag or can 
            be from a specified directory containing all datasets to be
            compared. Weights can be added to particular variables or hxls 
            using the var_dictionary_weighted.xls and 
            hxl_dictionary_weighted.xlsx respectively. These can also be
            altered according to expert judgement. 
            
Requirements: myFunctions.py

Optional: var_dictionary_weighted.xlsx, hxl_dictionary_weighted.xlsx


@author: cmcinerney
"""

# =============================================================================
# User inputs
# =============================================================================

# general configuration
graphName = 'Afghanistan_test'      # name for gexf & html graphs
graphPath = 'C:/Users/cmcinerney/Desktop/UNOCHA Fellowship/python output/'  # where to save graphs
dataPath = 'C:/Users/cmcinerney/AppData/Local/HDXdata/Afghanistan'     # download & load data here or just load data from this folder
fileTypes = ['csv', 'xls', 'xlsx']      # valid filetypes for loading (note: only able to download files of type csv, xls or xlsx)
countryOfInterest = 'Afghanistan'       # filter HDX results by country
tagOfInterest = ''                      # filter HDX results by tag
numOfDataSets = 400                     # process this many datasets, make large (1000) to process all
downloadFromHDX = False                 # search the HDX and download data, otherwise just load the data already in dataPath
include_weights = True                  #include weights specified in excel doc, otherwise edges have equal weights of 1

# =============================================================================
# Import libs and configure
# =============================================================================

import pandas as pd # for data wrangling
#import hxl # for accessing the databases
import networkx as nx
import os
import sys

# Setup Config for HDX
from hdx.utilities.easy_logging import setup_logging
from hdx.hdx_configuration import Configuration
from hdx.data.dataset import Dataset
from collections import Counter

from myFunctions import filterListbyCountry, filterListbyTag, draw_graph3
setup_logging()

# =============================================================================
# Download from HDX
# =============================================================================
if downloadFromHDX:
    # We only need to read data
    try:
        Configuration.create(hdx_site='prod', user_agent='A_Quick_Example', hdx_read_only=True)
    except:
        print("Configuration exists already")

    # =============================================================================
    # Filter Results from HDX
    # =============================================================================

    queryResult = Dataset.search_in_hdx(countryOfInterest)

    filteredResults = filterListbyCountry(queryResult, [countryOfInterest])
    #filteredResults = filterListbyTag(filteredResults, ['hxl'])


    # =============================================================================
    # Download all (filtered) dataset resources to local machine
    # =============================================================================
    resources = Dataset.get_all_resources(filteredResults)


    #loop through all resources and identify all csv or xlsx then download the file from the url
    resources_csv = []
    num_of_datasets = 0    
    for x in resources:        
        if x['format'].lower() in fileTypes:
            # if the file isn't already there, try to download it
            if not os.path.isfile(dataPath + x['name'] + '.' + x['format']):
                try:
                    print('Downloading ',dataPath + x['name'] + '.' + x['format'])
                    url, path = x.download(folder=dataPath)
                except:
                    print('Download failed: ', sys.exc_info()[0])
        
            # if file already existed or has downloaded successfully
            if os.path.isfile(dataPath + x['name'] + '.' + x['format']):                           
                num_of_datasets += 1
                resources_csv.append({"name" : x['name'], "format" : x['format']})

# =============================================================================
# Load data from local folder
# =============================================================================
else:
    files = [f for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f))]
    resources_csv = [{"name" : os.path.splitext(f)[0], "format" : os.path.splitext(os.path.join(dataPath, f))[1][1:]} for f in files]
    num_of_datasets = len(resources_csv)

print("Found " + str(len(resources_csv)) + " resources, using " + str(min(len(resources_csv),numOfDataSets)))

# =============================================================================
# loop through all datasets (resources) and build graph 
# =============================================================================
#create empty lists, empty graphs, empty sets in the matrices   
dict_of_hxls = {}
set_of_all_hxls = []
matrix_intersect_hxls = [[{} for x in range(num_of_datasets)] for y in range(num_of_datasets)]
matrix_intersect_hxls_num = [[0 for x in range(num_of_datasets)] for y in range(num_of_datasets)]
dict_of_vars = {}
set_of_all_vars = []
matrix_intersect_vars = [[{} for x in range(num_of_datasets)] for y in range(num_of_datasets)]
matrix_intersect_vars_num = [[0 for x in range(num_of_datasets)] for y in range(num_of_datasets)]
G=nx.Graph()

#import file containing weights for particular vars/hxls
hxls_weights = pd.read_excel('hxl_dictionary_weighted.xlsx', usecols = ['HXL', 'Weight'])
hxls_weights = hxls_weights.set_index('HXL').T.to_dict('records')[0]
vars_weights = pd.read_excel('var_dictionary_weighted.xlsx', usecols = ['Var_name', 'Weight'])
vars_weights = vars_weights.set_index('Var_name').T.to_dict('records')[0]

#loop through all resources, adding nodes for datasets and
#edges if they share variables or hxls
for ind_x, x in enumerate(resources_csv[0:min(numOfDataSets,len(resources_csv))]):
        #import first 2 rows from each csv
        file_name = dataPath + '/' + x['name'] + '.' + x['format']
        print("Adding resource to graph: " + x['name'])
        print(file_name)
        try:
            if x['format'].lower() == 'csv':
                vars_hxls = pd.read_csv(file_name,header=None,nrows=2)
            elif x['format'].lower() == 'xlsx' or x['format'].lower() == 'xls':
                vars_hxls = pd.read_excel(file_name,header=None,nrows=2)
            else:
                print("Can\'t load " + x['format'] + " files")
                continue
        except:
            print('Couldn\'t load resource: ', sys.exc_info()[0])
            continue
        # check if it got any actual data
        if vars_hxls.size == 0:
            print('Resource is empty')
            continue
        #extract the first row of each file and append to list of variables
        #remove spaces and nans
        v = [str(n).replace(" ","") for n in vars_hxls.iloc[0,:] if str(n).lower() != 'nan']
        #v = [x.replace(" ","") for x in v]     
        dict_of_vars.update({ind_x : v})
        #extract the second row of each file and append to list of hxls
        #remove spaces and nans
        h = [str(n).replace(" ","") for n in vars_hxls.iloc[1,:] if str(n).lower() != 'nan']
        #check for # in string before adding
        h = [n for n in h if '#' in str(n).lower()]
        dict_of_hxls.update({ind_x : h})
        #create list of all resource names (datasets) for graph
        G.add_node(ind_x, title = x['name'], hxls = ",".join(h), variables = ",".join(v))
        
        # =============================================================================
        # loop through array of hxls and add edges to graph           
        # =============================================================================
        for index, (ind_j, j) in enumerate(dict_of_hxls.items()):
            # don't check a node against itself
            if ind_j == ind_x:
                continue
            for ind_e, e in enumerate(j):
                set_of_all_hxls.append(j[ind_e])
            #intersection of set of hxls of current node with previous                        
            intersect_hxls = set(j).intersection(set(dict_of_hxls[ind_x]))
            matrix_intersect_hxls[ind_x][ind_j] = intersect_hxls
            matrix_intersect_hxls_num[ind_x][ind_j] = len(intersect_hxls)
            if len(intersect_hxls) > 0:
                #check if edges should be weighted, if not all edges have weight 1
                if include_weights == True:
                    count = len(intersect_hxls)
                    #proportion of hxls in common (denominator: total hxls in smaller dataset)
                    prop = round(len(intersect_hxls)/min(len(set(j)), len(set(dict_of_hxls[ind_x]))), 2)
                    #use "expert judgement" weights 
                    jud_weight = 0 
                    for hxl in intersect_hxls: 
                        #sum weights of each hxl if in dictionary, else +0.5 (default)
                        try:jud_weight += hxls_weights[hxl]
                        except:jud_weight += 0.5
                else:
                    jud_weight = 1
                G.add_edge(ind_x, ind_j, weight = jud_weight, title = '<br> '.join(map(str, matrix_intersect_hxls[ind_x][ind_j])), prop = prop, count = count)

        # =============================================================================
        # loop through array of vars and fill in empty matrix with intersecting sets            
        # =============================================================================
        for index, (ind_j, j) in enumerate(dict_of_vars.items()):
            # don't check a node against itself
            if ind_j == ind_x:
                continue
            for ind_e, e in enumerate(j):
                set_of_all_vars.append(j[ind_e])
            #intersection of set of vars of current node with previous                        
            intersect_vars = set(j).intersection(set(dict_of_vars[ind_x]))
            matrix_intersect_vars[ind_x][ind_j] = intersect_vars
            matrix_intersect_vars_num[ind_x][ind_j] = len(intersect_vars)
            if len(intersect_vars) > 0:
                count = len(intersect_vars)
                prop = round(len(intersect_vars)/min(len(set(j)), len(set(dict_of_vars[ind_x]))), 2)
                #use "expert judgement" weights 
                jud_weight = 0 
                for var in intersect_vars:
                    #sum weights of each var if in dictionary, else +0.5 (default)
                    try:jud_weight += vars_weights[var]
                    except:jud_weight += 0.5
                #if edge already exists add var names and sum with existing weight
                if G.has_edge(ind_x, ind_j):
                    G.edges[ind_x,ind_j]['weight'] = G.edges[ind_x,ind_j]['weight'] + jud_weight
                    G.edges[ind_x,ind_j]['title'] = G.edges[ind_x,ind_j]['title'] + '<br> '+'<br> '.join(map(str, matrix_intersect_vars[ind_x][ind_j]))
                else:
                    G.add_edge(ind_x, ind_j, weight = jud_weight, title = '<br> '.join(map(str, matrix_intersect_vars[ind_x][ind_j])), prop = prop, count = count)
        
#count number of times hxls/vars occur in all datasets
set_of_all_hxls = Counter(set_of_all_hxls)
set_of_all_vars = Counter(set_of_all_vars)

#write graph file 
nx.write_gexf(G, graphPath + graphName + ".gexf")        
        
#visualise the graph
draw_graph3(G,graphPath + graphName + ".html")