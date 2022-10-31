# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 11:13:09 2019

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
    
    extracted_properties = []
    for template in matches:
        if '\n' in str(template) and '|' in str(template) and  '=' in str(template):
            extracted_properties_dict = {param.name.strip_code().strip(): param.value.strip_code().strip() 
                  for param in template.params
                  if param.value.strip_code().strip()}
            extracted_properties_dict["template_name"] = template.name.strip()
            extracted_properties.append(extracted_properties_dict)
            '''
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
            '''
   
    categories = re.findall('\[\[Kateqoriya:.*\]\]' ,str(wikicode) )
    striped_categories = [x[13:-2] for x in categories]
    # Extract wikilinks
    wikilinks = [x.title.strip_code().strip() for x in wikicode.filter_wikilinks()]
    # Extract external links
    exlinks = [x.url.strip_code().strip() for x in wikicode.filter_external_links()]
    
    bodytext = wikicode.strip_code().strip()

    return [title, bodytext, extracted_properties, wikilinks, exlinks,
    striped_categories, text]


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
    '''
    # Limiting Number of articles
    if len(handler._pages) > 2000:
        break
    '''

    
with open('./data/wikipedia_parsed_v3.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(handler._pages, f, pickle.HIGHEST_PROTOCOL)
    
#### Reading file ############
    
with open('./data/wikipedia_parsed_v3.pickle', 'rb') as f:
    # Note that the column names are as follows for the data:
    """
    ['title', 'bodytext','properties', 'wikipedia_links', 'external_links', 'kateqoriyalar', 'raw_text']
    I included additional "raw_text" column which is the raw text of each page (the same text as we see in redaktə)
    """
    data = pickle.load(f)
    

# Optionally dataframe:
df = pd.DataFrame(data, columns = ['title', 'bodytext','properties', 
                                   'wikipedia_links', 'external_links',
                                   'kateqoriyalar', 'raw_text'])
    

# Getting all tamplates for a particular title
for title, bodytext, properties, wikipedia_links, external_links, kateqoriyalar, raw_text in data:
    if title == 'İçərişəhər':
        # print(title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar)
        prop = properties
        break
"""
Note that templates are formed as list of dictionaries where keys and values are
template parameters and values respectively.
I also added a "template_name" key to each dictionary (template) which reflects
the name of the template.
"""   
# print(prop)

for temp in prop:
    print("Template Name:", temp["template_name"])
    for k,v in temp.items():
        print("   ", k, "  :  ", v)
    print("-"*50)
    print()

        