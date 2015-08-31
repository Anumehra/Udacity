
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs


OSMFILE = "san-francisco_california.osm"

# Definition of re expressions
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
postcode_re = re.compile(r'[a-z=\+/&<>;\_\'"\?%#$@\,\. \t\r\n]', re.IGNORECASE)
name_re = re.compile(r'^[0-9]+$')

# List of expected street types
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle",  "Alley", "Terrace", "Path", "Highway", "Center", "Crescent", "Way", "Walk", "Plaza", "Loop", "View", "Mall", "Freeway", "Lane"]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def audit_state_name(state_names, state_name):
    if state_name != 'CA':
        state_names.append(state_name)

def audit_postcode(postcodes, postcode):
    m = postcode_re.search(postcode)
    if m:
        postcodes.append(postcode)

def audit_city_name(city_names, city_name):
    m = name_re.search(city_name)
    if m:
        city_names.append(city_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postcode_name(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_state_name(elem):
    return (elem.attrib['k'] == "addr:state")

def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")

def audit(osmfile):
    
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    state_names = []
    postcodes = []
    city_names = []
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                # Audit street type
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                # Audit postcode
                if is_postcode_name(tag):
                    audit_postcode(postcodes, tag.attrib['v'])
                # Audit state name
                if is_state_name(tag):
                    audit_state_name(state_names, tag.attrib['v'])
                # Audit city name
                if is_city_name(tag):
                    audit_city_name(city_names, tag.attrib['v'])

    return street_types, state_names, postcodes, city_names


def process_audit():
    street_types, state_names, postcodes, city_names = audit(OSMFILE)
    pprint.pprint(street_types)
    pprint.pprint(state_names)
    pprint.pprint(postcodes)
    pprint.pprint(city_names)



if __name__ == '__main__':
    process_audit()