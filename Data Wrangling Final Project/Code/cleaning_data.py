#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


# Definition of re expressions
lower_re = re.compile(r'^([a-z]|_)*$')
lower_colon_re = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars_re = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
postcode_re = re.compile(r'[a-z=\+/&<>;\_\'"\?%#$@\,\. \t\r\n]', re.IGNORECASE)
name_re = re.compile(r'^[0-9]+$')

# Created dict keys
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


# Mapping for street types
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Rd": "Road",
            "Ave": "Avenue", 
            "Ave.": "Avenue", 
            "Ct": "Court",
            "Ln.": "Lane",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Dr": "Drive",
            "Ctr": "Center",
            "Hwy": "Highway",
            "Dr.": "Drive",
            "Cres": "Crescent",
            "Plz": "Plaza"
            }


def islower(attr):
    return lower_re.search(attr)
     
def islower_colon(attr):
    return lower_colon_re.search(attr)

def isproblemchars(attr):
    return problemchars_re.search(attr)

def is_address(tag_key):
    return tag_key.startswith('addr:')

def is_street_name(attr):
    return attr == "addr:street"

def is_postcode(attr):
    return attr == "addr:postcode"

def is_city_name(attr):
    return attr == "addr:city"

def is_state_name(attr):
    return attr == "addr:state"

def is_country_name(attr):
    return attr == "addr:country"

def is_tag_key_postal_code(tag_key):
    return tag_key == "postal_code"

def update_type_title(name):
    # Get the street type
    last_string = name.rsplit(None, 1)[-1]
    # Convert the street type to title case
    name = name.replace(last_string, last_string.title()) 
    return name

def update_street_type(name, mapping):
    keys = mapping.keys()
    # Get the street type
    last_string = name.rsplit(None, 1)[-1] 
    for each_key in keys:
        if last_string == each_key:
            # Update the street type based on mapping
            name = name.replace(each_key, mapping[each_key]) 
    
    return name

def update_postcode(postcode):
    # Replace the alphabets or special charaters to '' in postcode
    postcode = postcode_re.sub('',postcode)
    if postcode:
      return postcode
    return None

def update_city(name):
    # Remove whitespaces and update to title case
    name = name.strip().title()
    if name_re.search(name):
        return None
    return name

def shape_element(element):
    node_dict = {}

    if element.tag != "node" and element.tag != "way":
      return None

    # Parse node attributes
    for attr_name, attr_value in element.items():
        # Create the 'created' dictionary
        if attr_name in CREATED:
            node_dict.setdefault('created', {})[attr_name] = attr_value
        # Add lattitude and longitude to the 'pos' array 
        elif attr_name == "lat":
            node_dict.setdefault('pos', []).insert(0, float(attr_value))
        elif attr_name == "lon":
            node_dict.setdefault('pos', []).insert(1, float(attr_value))
        # Add other items to node dictionary
        else:
            node_dict[attr_name] = attr_value
      

    # Parse child elements of node
    for child_element in list(element):
        is_postcode_in_address = False
        
        if child_element.tag == 'tag':

            tag_key = child_element.get('k')
            tag_value = child_element.get('v')

            # Create the 'address' dictionary 
            if islower_colon(tag_key) and is_address(tag_key):

                addr_key = tag_key.rsplit(":", 1)[-1] # e.g. get 'housenumber' from 'addr:housenumber'

                # Add items in 'address' dictionary
                node_dict.setdefault('address', {})[addr_key] = tag_value

                # Update the street type 
                if is_street_name(tag_key):
                    street_type = update_type_title(tag_value)
                    node_dict.setdefault('address', {})[addr_key] = update_street_type(street_type, mapping)
              
                # Update city name
                if is_city_name(tag_key):
                    #if update_city(tag_value):
                    node_dict.setdefault('address', {})[addr_key] = update_city(tag_value)

                # Update state name to 'CA'
                if is_state_name(tag_key):
                    node_dict.setdefault('address', {})[addr_key] = 'CA'
              
                # Update country name to 'US'
                if is_country_name(tag_key):
                    node_dict.setdefault('address', {})[addr_key] = 'US'
              
                # Update postcode 
                if is_postcode(tag_key):
                    if update_postcode(tag_value):
                        is_postcode_in_address = True
                    node_dict.setdefault('address', {})[addr_key] = update_postcode(tag_value)

                # If postcode doesn't exist, assign postcal_code tag value to postcode
                if is_tag_key_postal_code(tag_key) and not is_postcode_in_address:
                    node_dict.setdefault('address', {})['postcode'] = update_postcode(tag_value)
            
            # Add other items to node decitionary, except 'address' and 'postal_code'
            elif (islower_colon(tag_key) or islower(tag_key)) and tag_key not in ['address', 'postal_code']:
                node_dict[tag_key] = tag_value

        # Check 'nd' tags and add 'ref' values to the 'node_refs' array
        elif child_element.tag == 'nd':
            node_dict.setdefault('node_refs', []).append(child_element.get('ref'))

    # Assign the 'type' at the end, to avoid getting reassigned later. 
    node_dict['type'] = element.tag

    return node_dict


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w", encoding="utf8") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2, ensure_ascii=False)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


if __name__ == "__main__":
    process_map('san-francisco_california.osm', True)