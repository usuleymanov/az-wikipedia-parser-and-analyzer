# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 17:14:29 2019

@author: u.suleymanov

"""
from bs4 import BeautifulSoup
import xml.sax
import mwparserfromhell
import pandas as pd
import re
import pickle

data_path = './data/azwiki-20190620-pages-articles-multistream.xml'

def process_article(title, text):
    """Process a wikipedia article looking for template"""
    
    # Create a parsing object
    wikicode = mwparserfromhell.parse(text)
    
    # Search through templates for the template
    matches = wikicode.filter_templates()
    
    # Extract information from infobox (note itis manual look at first 5 templates if one of them is relevant to infobox template then add its properties)
    count = 0
    location_properties = {}
    extracted_properties = {}
    for template in matches:
        if count > 4:
            break
        count += 1
        if '\n' in str(template) and '|' in str(template) and  '=' in str(template):
            extracted_properties = {param.name.strip_code().strip(): param.value.strip_code().strip() 
                  for param in template.params
                  if param.value.strip_code().strip()}
            
            ## Locations in articles
            for param in template.params:            
                map_match = param.value.filter_templates(matches = 'Yer xəritəsi')
                if len(map_match)>=1:
                    for param in map_match[0].params:
                        if param.name == "1":
                            location_properties["Ölkə"] = param.value.strip_code().strip()
                        else:
                            location_properties[param.name.strip_code().strip()] = param.value.strip_code().strip()
                    break
            
            break
   
    categories = re.findall('\[\[Kateqoriya:.*\]\]' ,str(wikicode) )
    striped_categories = [x[13:-2] for x in categories]
    # Extract wikilinks
    wikilinks = [x.title.strip_code().strip() for x in wikicode.filter_wikilinks()]
    # Extract external links
    exlinks = [x.url.strip_code().strip() for x in wikicode.filter_external_links()]
    
    bodytext = wikicode.strip_code().strip()

    return [title, bodytext, extracted_properties, wikilinks, exlinks,
    striped_categories, location_properties]


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self._article_count = 0
        # self._raw_pages = []
              

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []
        
    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)
            
        if name == 'page':
            self._article_count += 1
            # Send the page to the process article function
            page = process_article(**self._values)
            # If article is a book append to the list of books
            if page:
                 self._pages.append(page)
#                 self._raw_pages.append([self._values['title'],
#                                         self._values['text']])
                 
                
# Object for handling xml
handler = WikiXmlHandler()
# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

for line in open(data_path, 'r', encoding='utf8'):
    parser.feed(line)
    """
    # Limiting Number of articles
    if len(handler._pages) > 2000:
        break
    """
    
with open('./data/wikipedia_parsed_v2.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(handler._pages, f, pickle.HIGHEST_PROTOCOL)
    

with open('./data/wikipedia_parsed_v2.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
    

###############################################################################
"""
wiki = mwparserfromhell.parse(handler._raw_pages[1][1])
wikilinks = [x.title.strip_code().strip() for x in wiki.filter_wikilinks()]
#print(wiki)
bodytext = wiki.strip_code().strip()

matches = wiki.filter_templates()
count = 0
extracted_properties = {}
for template in matches:
    if count > 4:
        break
    count += 1
    print(type(template))
    print(str(template))
    if '\n' in str(template) and '|' in str(template) and  '=' in str(template):
        print(True)
        extracted_properties = {param.name.strip_code().strip(): param.value.strip_code().strip() 
              for param in template.params
              if param.value.strip_code().strip()}
        break
    
    
categories = re.findall('\[\[Kateqoriya:.*\]\]' ,str(wiki) )
striped_categories = [x[13:-2] for x in categories]
wikilinks[:5]
"""
###############################################################################
"""
handler._pages[0][17]
handler._raw_pages[0]
#handler._pages[1]
#handler._pages[2]
#handler._pages[2000]
#handler._pages[400]
#handler._pages[401]
handler._pages[470]
data[470]
handler._pages[19990]
data[19990]

print("Overall articles: ", handler._article_count)
print("Articles on edebi eser: ", len(handler._pages))

"""
############### Converting to Dataframe #######################################

df = pd.DataFrame(handler._pages,
                  columns = ['title', 'bodytext','properties', 'wikipedia_links',
                             'external_links', 'kateqoriyalar', 'location'])
    
df.to_csv('./data/wikipedia_parsed_v2.csv', index = False)

wiki_parse = pd.read_csv('./data/wikipedia_parsed_v2.csv')

####################### External links ########################################
external_links = {}

for page in handler._pages:
    for link in page[4]:
        clean_link_index = link.find('/', 8)
        if clean_link_index == -1:
            external_links[link] = external_links.get(link, 0) + 1
        else:
            external_links[link[:clean_link_index]] = external_links.get(link[:clean_link_index], 0) + 1
        

external_links_statistics = pd.DataFrame.from_dict(external_links,
                                                   orient='index',
                                                   columns=['count'])

external_links_statistics.to_csv('./data/wikipedia_edebi_eserler_external_links_statistics.csv')


ax = external_links_statistics.plot.bar(x='lab', y='val', rot=0)

###################### Collecting All Property Names ##########################

all_properties_lower = set()
for item in data:
    for prop_name in item[2].keys():
        all_properties_lower.add(prop_name.strip().lower())

print("Umumilikde", len(all_properties_lower), "sayda muxtelif infobox parametrleri islenib")


articles_with_property_count = 0
for item in data:
    if len(item[2]) > 0:
        articles_with_property_count += 1
        
print("Yazilan", len(data), "artikllarin", articles_with_property_count, "-ində infobox template var.")


all_property_useage_distribution = {}

for item in data:
    for prop_name in item[2].keys():
        all_property_useage_distribution[prop_name.strip().lower()] = all_property_useage_distribution.get(prop_name.strip().lower(), 0) + 1


import matplotlib.pyplot as plt
import numpy as np
sorted_all_property_useage = sorted(all_property_useage_distribution.items(), key=lambda kv: kv[1], reverse=True)
# Make a fake dataset:

height = [n[1] for n in sorted_all_property_useage]
bars = [n[0] for n in sorted_all_property_useage]

height = height[:150]
bars = bars[:150]

y_pos = np.arange(len(bars))
 
# Create bars
plt.bar(y_pos, height)
 
# Create names on the x-axis
plt.xticks(y_pos, bars, rotation=90)
plt.text(120, 40000, "Yazilan 299142 artiklların 110668-ində infobox template var.", fontsize=9)
plt.text(120, 39000, "Ümumilikde 46887 sayda müxtəlif infobox parametrləri işlənib.", fontsize=9)
# Show graphic
plt.show()
