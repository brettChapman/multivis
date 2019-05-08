import json
#from operator import itemgetter

#Note: forked from https://riptutorial.com/pandas/example/16715/dataframe-into-nested-json-as-in-flare-js--files-used-in-d3-js
def df_to_flareJson(df_edges):
    """Convert dataframe into nested JSON as in flare files used for D3.js"""
    flare = dict()
    d = {"name": "flare", "children": []}

    for index, row in df_edges.iterrows():

        parent_index = row[0]
        parent_color = row[1]
        parent = row[2]
        parent_group = row[3]
        child_index = row[4]
        child_color = row[5]
        child = row[6]
        child_group = row[7]
        link_corrCoeff = row[8]
        link_pvalue = row[9]
        link_color = row[10]

        # Make a list of keys
        key_list = []
        for item in d['children']:
            key_list.append(item['keyname'])

        # if parent index is NOT a key in flare.JSON, append it
        if not parent_index in key_list:
            d['children'].append(
                {"keyname": parent_index, "name": parent, "node_color": parent_color, "group": parent_group,
                 "children": [{"keyname": child_index, "name": child, "node_color": child_color,
                               "link_corrCoeff": link_corrCoeff, "link_pvalue": link_pvalue, "group": child_group,
                               "link_color": link_color}]})

        # if parent index IS a key in flare.json, add a new child to it
        else:
            d['children'][key_list.index(parent_index)]['children'].append(
                {"keyname": child_index, "name": child, "node_color": child_color, "link_corrCoeff": link_corrCoeff,
                 "link_pvalue": link_pvalue, "group": child_group, "link_color": link_color})

    flare = d

    return flare

def df_to_Json(df_edges):

    flare = df_to_flareJson(df_edges);

    flareString = ""

    bundleJsonArray = []
    completeChildList = []

    for key, value in flare.items():

        if isinstance(value, str):
            flareString = value
        elif isinstance(value, list):

            for idx, val in enumerate(value):
                dParent = {"keyname": "", "name": "", "node_color": "", "group": "", "imports": {}}

                parent_index = str(value[idx]['keyname'])
                parentName = str(value[idx]['name'])
                parentColor = str(value[idx]['node_color'])
                parentGroup = str(value[idx]['group'])

                flareParentIndex = flareString + "#" + parentGroup + "#" + parent_index

                dParent["keyname"] = flareParentIndex
                dParent["name"] = parentName
                dParent["node_color"] = parentColor
                dParent["group"] = parentGroup

                childList = value[idx]['children']

                for child in childList:
                    link_corrCoeff = float(child['link_corrCoeff'])
                    link_pvalue = float(child['link_pvalue'])
                    link_color = str(child['link_color'])

                    dChild = {"keyname": "", "name": "", "node_color": "", "group": "", "imports": {}}

                    child_index = str(child['keyname'])
                    childName = str(child['name'])
                    childColor = str(child['node_color'])
                    childGroup = str(child['group'])

                    flareChildIndex = flareString + "#" + childGroup + "#" + child_index

                    dParent["imports"][flareChildIndex] = {"link_corrCoeff": link_corrCoeff, "link_pvalue": link_pvalue,
                                                       "link_color": link_color}

                    dChild["keyname"] = flareChildIndex
                    dChild["name"] = childName
                    dChild["node_color"] = childColor
                    dChild["group"] = childGroup

                    dChild["imports"][flareParentIndex] = {"link_corrCoeff": link_corrCoeff, "link_pvalue": link_pvalue,
                                                       "link_color": link_color}

                    completeChildList.append(dChild)

                bundleJsonArray.append(dParent)
    bundleJsonArray.extend(completeChildList)

    return bundleJsonArray;