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

data_path = './raw_data/azwiki-20190620-pages-articles-multistream.xml'

def clean_the_article(body_text):
    """
    Cleans an article body and returns cleaned text
    """
    t = re.sub(r"\n","", body_text)
    t = re.sub(r'\t', '', t)
    t = re.sub(r' +', ' ', t)
    t = re.sub(r'<title>.*?</title>','',t)
    t = re.sub(r'=+.*?=+','',t)
    t = re.sub(r'<id>.*?</id>','',t)
    t = re.sub(r'<ns>.*?</ns>','',t)
    t = re.sub(r'<parentid>.*?</parentid>','',t)
    t = re.sub(r'<timestamp>.*?</timestamp>','',t)
    t = re.sub(r'<username>.*?</username>','',t)
    t = re.sub(r'<contributor>','',t)
    t = re.sub(r'</contributor>','',t)
    t = re.sub(r'<comment>.*?</comment>','',t)
    t = re.sub(r'<model>.*?</model>','',t)
    t = re.sub(r'<format>.*?</format>','',t)
    t = re.sub(r'\[\[Şəkil:.*?\]\]','',t)
    t = re.sub(r'&lt;.*?&gt;','',t)
    t = re.sub(r'<shal.*?shal>','',t)
    t = re.sub(r'<text.*?>','',t)
    t = re.sub(r'</text>','',t)
    t = re.sub(r'<page>','',t)
    t = re.sub(r'</page>','',t)
    t = re.sub(r'<minor.*?>','',t)
    t = re.sub(r'<revision>','',t)
    t = re.sub(r'</revision>','',t)
    t = re.sub(r'{{[^}]*}}','',t) #doesn't work {{İstifadəçi??
    t = re.sub(r'\{\|.*\|\}', '', t) #doesn't work with
    
    t = re.sub(r'\[http.*?\]+', '', t)
    t = re.sub(r'(\')+?', '', t)
    t = re.sub(r'^(\*)+.*', '', t)
    t = re.sub(r'^(\:)+.*', '', t)
    t = re.sub(r' +', ' ', t)
    return t


def process_article(title, text):
    """Process a wikipedia article looking for template"""
    
    # Create a parsing object
    wikicode = mwparserfromhell.parse(text)
    
    bodytext = wikicode.strip_code().strip()
    
    cleaned_body = clean_the_article(bodytext)
    
    return [title, bodytext, cleaned_body]


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self._article_count = 0
              

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
    
    # Limiting Number of articles
    if len(handler._pages) > 2000:
        break
    

df = pd.DataFrame(handler._pages,
                  columns = ['title', 'raw_bodytext', "cleaned_body_text"])
    
df.to_csv('./wikipedia_cleaned.csv', index = False)
df.to_excel("cleaned_wikipedia.xlsx")

wiki_parse = pd.read_csv('./wikipedia_cleaned.csv')


#################### Optional #################################################

# optioanlly putting your file as pickle
with open('./data/wikipedia_parsed_v2.pickle', 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(handler._pages, f, pickle.HIGHEST_PROTOCOL)
    

with open('./data/wikipedia_parsed_v2.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
