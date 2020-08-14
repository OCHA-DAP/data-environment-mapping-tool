# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 11:36:38 2020

Data Environment Mapping tool prototype

Description: This tool allows a user to upload a dataset and quickly see
            what other datasets on HDX (related to a particular country) it 
            shares variable names or HXL tags with. The interface can be found 
            by visiting http://127.0.0.1:8050/ in your browser.

Required: graph.html and graph.hexf (the existing data network, both created from 
         file named "create_graph") saved in a folder called 'assets' 

@author: cmcinerney
"""
    
import base64
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from collections import OrderedDict

import pandas as pd
import networkx as nx
from datetime import datetime
from flask import Flask
from flask_caching import Cache

from myFunctions import draw_graph3, parse_contents

# general configuration
graphName = 'Afghanistan_test'      # name for default/initial graph to load

# =============================================================================
# Setup Dash layout
# =============================================================================

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
cache.clear()

#define colours and formatting
colors = {
    'background': '#469bd8',
    'text': '#F37464'
}

df_typing_formatting = pd.DataFrame(OrderedDict([
    ('city', ['Vancouver', 'Toronto', 'Calgary', 'Ottawa', 'Montreal', 'Halifax', 'Regina', 'Fredericton']),
    ('average_04_2018', [1092000, 766000, 431000, 382000, 341000, 316000, 276000, 173000]),
    ('change_04_2017_04_2018', [0.143, -0.051, 0.001, 0.083, 0.063, 0.024, -0.065, 0.012]),
]))

#include components in the tool
app.layout = html.Div([
    html.H1(
        children='Data Environment Map',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

        html.Div(children='The data environment refers to the context in which the data sits, encompassing all relevant datasets, the relationships between those datasets, and the availability and properties of that data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div([  # modal div
        html.Div([  # content div
            html.Div([
                'Use this tool to visualise the data environment of your dataset. By dragging your file to the ‘drag and drop’ bar, your dataset will be added to the network and visualised as a red-coloured node. Blue nodes represent datasets already available on HDX and an edge connecting two nodes indicates that they share common variables (column headers or HXLs). You will also see a list of dataset names appear, these all share variables with your data.'
            ]),
            html.Div([
                'This network allows you to quickly see how your data may be linked to other datasets available on HDX. If two datasets have variables in common, there is potential for them to be linked and new information learnt. Linkage can occur when multiple datasets have one or more variables in common and the information contained within those variables refer to the same unit (e.g. district, month, household, etc). Learning new information by linking two or more datasets can be very useful for further informing humanitarian action but it also has the potential to be used by bad actors to do harm. By better understanding the environment in which your data sits, you can begin to assess the likelihood of potentially useful or dangerous links. You can find out more about how to increase the linkage potential of your data using HXL tags here and about how to assess the risk that linkages may be used to do harm here (link to blog).'
            ]),

            html.Hr(),
            html.Button('Close', id='modal-close-button')
        ],
            style={'textAlign': 'left', 'width': '98%'},
            className='modal-content',
        ),
    ],
        id='modal',
        className='modal',
        style={"display": "block"},
    ),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    
    html.Div(id = 'neighbours',
        children='This is where list of datasets will be', 
        style={
        'color': '#000000',
        'width': '18%',
        'display': 'inline-block',
        'vertical-align': 'top',
        "maxHeight": "800px", 
        "overflow": "scroll"
        }),
    #insert network graph
    html.Iframe(id = 'graph-iframe',
                height=2000,width=900,src=app.get_asset_url(graphName + ".html"),
        style={
            'width': '78%',
            'height': '800px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px', 
            'display': 'inline-block'
        }), 
    html.Div(id = 'meta_data',
        children='data for added dataset', 
        style={
        'color': '#000000',
        'width': '100%',
        'display': 'inline-block',
        'vertical-align': 'top'
        }),
    
    #uploaded dataset displayed at bottom
    html.Div(id='output-data-upload')
])




@app.callback(Output('modal', 'style'),
              [Input('modal-close-button', 'n_clicks')])
def close_modal(n):
    if (n is not None) and (n > 0):
        return {"display": "none"}
    


# =============================================================================
# Define callbacks
# =============================================================================

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

    
@app.callback([
              Output('graph-iframe', 'src'),
              Output('neighbours', 'children'),
              Output('meta_data', 'children')
              ],[Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_graph_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        hxls_weights = pd.read_excel('hxl_dictionary_weighted.xlsx', usecols = ['HXL', 'Weight'])
        hxls_weights = hxls_weights.set_index('HXL').T.to_dict('records')[0]
        vars_weights = pd.read_excel('var_dictionary_weighted.xlsx', usecols = ['Var_name', 'Weight'])
        vars_weights = vars_weights.set_index('Var_name').T.to_dict('records')[0]
        content_type, content_string = list_of_contents[0].split(',')
        decoded = base64.b64decode(content_string)
        #import graph of existing nodes/edges
        G = nx.read_gexf(".\\assets\\" + graphName + ".gexf")
        #extract first two rows of new file to find vars and hxls
        try:
            if "csv" in list_of_names[0].lower():
                vars_hxls = pd.read_csv(io.StringIO(decoded.decode('utf-8')),header=None,nrows=2)
            elif "xls" in list_of_names[0].lower():
                vars_hxls = pd.read_excel(io.BytesIO(decoded),header=None,nrows=2)
            else:
                print("Resource is not of appropriate filetype")
                return
        except:
            print('Resource not found')         
            return   
        #assuming vars in 1st row and hxls in 2nd row, extract them from new data
        h = vars_hxls.iloc[1,:].str.lower().str.replace(" ","")
        h = [n for n in h if str(n).lower() != 'nan']
        v = vars_hxls.iloc[0,:].str.lower().str.replace(" ","")
        v = [n for n in v if str(n).lower() != 'nan']
        G.add_node(9999, title = list_of_names[0], color=colors['text'],hxls=",".join(h),variables=",".join(v))
        #loop through hxls and vars attached to each node and find any in common with new file
        neighbours = []
        #array of data about the new data set [total cons, hxl cons, var cons, av hxl cons, avg var cons, total edge weight]
        meta_data = [0,0,0,0,0,0]         
        for n in G.nodes():
            if n != 9999:
                hxls = G.nodes()[n]['hxls'].split(",") 
                variables = G.nodes()[n]['variables'].split(",") 
                intersect_hxls = set(h).intersection(set(hxls))
                intersect_vars = set(v).intersection(set(variables))
                if len(intersect_hxls) + len(intersect_vars) > 0:
                    jud_weight = 0 
                    for hxl in intersect_hxls: 
                        #sum weights of each hxl if in dictionary, else +0.5 (default)
                        try:jud_weight += hxls_weights[hxl]
                        except:jud_weight += 0.5
                    for var in intersect_vars: 
                        #sum weights of each hxl if in dictionary, else +0.5 (default)
                        try:jud_weight += vars_weights[var]
                        except:jud_weight += 0.5
                    meta_data[5] += jud_weight
                    print(jud_weight)
                    G.add_edge(n,9999, weight = jud_weight, title = ', '.join(map(str, intersect_hxls)) + ', '.join(map(str, intersect_vars)),color=colors['text'])
                    # collect meta data
                    meta_data[0] += 1
                    if len(intersect_hxls) > 0:
                        meta_data[1] += 1
                        meta_data[2] += len(intersect_hxls)
                    if len(intersect_vars) > 0:
                        meta_data[3] += 1
                        meta_data[4] += len(intersect_vars)
                    #display the names of the datasets that the new data shares variables with
                    #needed to use html.Br() to get new line to display
                    neighbours.append(G.nodes()[n]['title'])                    
                    neighbours.append(html.Br())
        
        # update meta data
        if meta_data[1] > 0: 
            meta_data[2] = meta_data[2]/meta_data[1]
        if meta_data[3] > 0: 
            meta_data[4] = meta_data[4]/meta_data[3]
        
        # append meta data to html element
        data_readout = []
        data_readout.append('Total # of connected datasets: ')
        data_readout.append(meta_data[0])
        data_readout.append(html.Br())
        data_readout.append('# of datasets with HXL tags in common: ')
        data_readout.append(meta_data[1])
        data_readout.append(html.Br())
        data_readout.append('Average # of HXL tags in common: ')
        data_readout.append(meta_data[2])
        data_readout.append(html.Br())
        data_readout.append('# of datasets with variables in common: ')
        data_readout.append(meta_data[3])
        data_readout.append(html.Br())
        data_readout.append('Average # of variables in common: ')
        data_readout.append(meta_data[4])
        data_readout.append(html.Br())
        data_readout.append('Total edge weight:')
        data_readout.append(meta_data[5])
        data_readout.append(html.Br())
        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        draw_graph3(G,output_filename='.\\assets\\updatedgraph'+dt+'.html')
        nx.write_gexf(G, '.\\assets\\updatedgraph'+dt+'.gexf') 
        src=app.get_asset_url("updatedgraph"+dt+".html")
        neighbours.insert(0,html.Br())
        neighbours.insert(0,"Your data shares variables/HXL tags with these datasets: ")
        neighbours = html.P(neighbours)
        return src, neighbours, data_readout
    else:
        src=app.get_asset_url(graphName + ".html")
        return src, [], []


if __name__ == '__main__':
    app.run_server(debug=False)