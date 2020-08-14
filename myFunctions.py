import pandas as pd # for data wrangling
import json # for cleaning the data entrys
import base64
import io
import dash_html_components as html
import dash_table


from datetime import datetime

def filterListbyCountry(aList=[],country=['World']):
    '''
    Filters a list of HDX Dataset objects (lists) and returns the ones that match a specified country of interest.
    
    Input:
        - HDX Dataset objects (lists) and a string for a country of interest.
    
    Output:
        - Filtered list
        
    Requires:
        - pandas
        - json
    '''
    filteredList = []
    
    for item in aList:
        # Returns a 1–n length list of countries that the dataset relates to
        itemCountry = pd.Series(json.loads(item['solr_additions'])['countries'])
        
        # Checks if any of the 1–n countries are `countryOfInterest`
        if itemCountry.isin(country).any():
            # Append datasets that include our country of interest
            filteredList.append(item)
            
    return filteredList

def filterListbyTag(aList, tag):
    '''
    Filters a list of HDX Dataset objects (lists) by some tag and return the list items that match as a list.
    
    Input:
        - HDX Dataset objects (lists)
        - Tag names (list of strings)
    Output:
        - Filtered list
        
    Requires:
        - Pandas
    '''
    filteredList = []
    
    for item in aList:
        # Returns a 1–n length list of all tags
        itemTags = item['tags']
        
        if len(itemTags) == 0:
            continue
        else:
            itemTagNames = pd.Series([entry['name'] for entry in itemTags])
        
        # Checks if any of the tags are the ones given
        if itemTagNames.isin(tag).any():
            # Append these datasets to our filtered list
            filteredList.append(item)
            
    return filteredList


def draw_graph3(networkx_graph,output_filename,notebook=False):
    """
    This function accepts a networkx graph object,
    converts it to a pyvis network object preserving its node and edge attributes,
    and both returns and saves a dynamic network visualization.
    
    Valid node attributes include:
        "size", "value", "title", "x", "y", "label", "color".
        
        (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_node)
        
    Valid edge attributes include:
        "arrowStrikethrough", "hidden", "physics", "title", "value", "width"
        
        (For more info: https://pyvis.readthedocs.io/en/latest/documentation.html#pyvis.network.Network.add_edge)
        
    
    Args:
        networkx_graph: The graph to convert and display
        notebook: Display in Jupyter?
        output_filename: Where to save the converted network
        show_buttons: Show buttons in saved version of network?
        only_physics_buttons: Show only buttons controlling physics of network?
    """    
    # import
    from pyvis import network as net
    
    # make a pyvis network
    pyvis_graph = net.Network(height="750px", width="100%", bgcolor="#222222", font_color="white",notebook=notebook)
    
    # for each node and its attributes in the networkx graph
    for node,node_attrs in networkx_graph.nodes(data=True):
        pyvis_graph.add_node(str(node),**node_attrs)
        
    # for each edge and its attributes in the networkx graph
    for source,target,edge_attrs in networkx_graph.edges(data=True):
        # if value/width not specified directly, and weight is specified, set 'value' to 'weight'
        if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
            # place at key 'value' the weight of the edge
            edge_attrs['value']=edge_attrs['weight']
        # add the edge
        pyvis_graph.add_edge(str(source),str(target),**edge_attrs)
    
    #pyvis_graph.show_buttons(filter_=['physics'])
     
    #use the repulsion solver
    # pyvis_graph.hrepulsion(node_distance=420, central_gravity=0.8, spring_length=420, spring_strength=1, damping=0)
    pyvis_graph.set_options("""
        var options = {
            "configure": {
                "enabled": true,
                "filter": [
                    "physics"
                    ]
            },
            "edges": {
                "color": {
                    "inherit": true
                },
                "smooth": {
                    "enabled": false,
                    "type": "continuous"
                }
            },
            "interaction": {
                "dragNodes": true,
                "hideEdgesOnDrag": false,
                "hideNodesOnDrag": false
            },
            "physics": {
                "enabled": true,
                "barnesHut": {
                    "springLength": 300,
                    "damping": 0.6
                },
                "minVelocity": 0.75,
                "stabilization": {
                    "enabled": true,
                    "fit": true,
                    "iterations": 1000,
                    "onlyDynamicEdges": false,
                    "updateInterval": 50
                }
            }
        }"""
)
      
    # return and also save
    return pyvis_graph.save_graph(output_filename)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename.lower():
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename.lower():
            # Assume that the user uploaded an excel file (.xls or .xlsx)
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])