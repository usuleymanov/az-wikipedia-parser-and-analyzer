# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:15:58 2019

@author: u.suleymanov
"""
import pandas as pd
import re
import pickle
import matplotlib.pyplot as plt
import numpy as np

with open('./data/wikipedia_parsed_v2.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    # Note that the column names are as follows:
    """
    ['title', 'bodytext','properties', 'wikipedia_links', 'external_links', 'kateqoriyalar', 'location']
    """
    data = pickle.load(f)
    

############### Reading as Dataframe ##########################################
    
wiki_parse = pd.read_csv('./data/wikipedia_parsed_v2.csv')

wiki_parse.loc[34521]

##################### Infobox Properties ######################################

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

sorted_all_property_useage = sorted(all_property_useage_distribution.items(), key=lambda kv: kv[1], reverse=True)

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

print("150 most frequent Infobox Property:")
print(sorted_all_property_useage[:150])

####################### External links ########################################
external_links = {}

for page in data:
    for link in page[4]:
        clean_link_index = link.find('/', 8)
        if clean_link_index == -1:
            external_links[link] = external_links.get(link, 0) + 1
        else:
            external_links[link[:clean_link_index]] = external_links.get(link[:clean_link_index], 0) + 1
        

external_links_statistics = pd.DataFrame.from_dict(external_links,
                                                   orient='index',
                                                   columns=['count'])

sorted_external_links_statistics = sorted(external_links.items(), key=lambda kv: kv[1], reverse=True)

height = [n[1] for n in sorted_external_links_statistics]
bars = [n[0] for n in sorted_external_links_statistics]

height = height[:100]
bars = bars[:100]

y_pos = np.arange(len(bars))
 
# Create bars
plt.bar(y_pos, height)
 
# Create names on the x-axis
plt.xticks(y_pos, bars, rotation=90)
# Show graphic
plt.show()

print("150 most frequent External Links:")
print(sorted_external_links_statistics[:100])


##################### Categories ##############################################

all_categories_lower = set()
for item in data:
    for cat in item[5]:
        all_categories_lower.add(cat.strip().lower())

print("Umumilikde", len(all_categories_lower), "sayda muxtelif kateqoriya islenib")

articles_with_category_count = 0
for item in data:
    if len(item[5]) > 0:
        articles_with_category_count += 1
        
print("Yazilan", len(data), "artikllarin", articles_with_category_count, "-ində kateqoriya var.")


all_category_useage_distribution = {}

for item in data:
    for prop_name in item[5]:
        all_category_useage_distribution[prop_name.strip().lower()] = all_category_useage_distribution.get(prop_name.strip().lower(), 0) + 1

sorted_all_category_useage = sorted(all_category_useage_distribution.items(), key=lambda kv: kv[1], reverse=True)

height = [n[1] for n in sorted_all_category_useage]
bars = [n[0] for n in sorted_all_category_useage]

height = height[:150]
bars = bars[:150]

y_pos = np.arange(len(bars))
 
# Create bars
plt.bar(y_pos, height)
 
# Create names on the x-axis
plt.xticks(y_pos, bars, rotation=90)
plt.text(120, 2700, "Yazilan 299142 artiklların 211173-ində kateqoriya var.", fontsize=9)
plt.text(120, 2600, "Ümumilikde 134564 sayda müxtəlif kateqoriya işlənib.", fontsize=9)
# Show graphic
plt.show()

print("150 most frequent kateqory:")
print(sorted_all_category_useage[:150])


############################## Long Lat #######################################
xudaferin = []
a = {}

for title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar, location in data:
    if kateqoriyalar == 'Xudafərin körpüləri':
        print(title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar)
        a = properties
        b = bodytext
        break
    
###############################################################################
        
def select_not_empty_locations(wiki_parse):
    a = wiki_parse.copy()
    a['loc_length'] = wiki_parse['location'].apply(lambda x: len(x))
    a = a[a['loc_length'] > 2]
    return a

f = select_not_empty_locations(wiki_parse)


f
f.iloc[1]

######################### Movie Year for Interview ############################

count = 0
prop_az = []
for title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar, location_properties in data:
    if 'azərbaycan filmləri' in [ i.lower() for i in kateqoriyalar]:
        count += 1
        prop_az.append(properties)
        

prop_us =[]
count1 = 0
for title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar, location_properties in data:
    if 'abş filmləri' in [ i.lower() for i in kateqoriyalar]:
        count1 += 1
        prop_us.append(properties)
        
        
        
az_movie_years = []

for i in prop_az:
    if i.get('İl', None):
        az_movie_years.append(re.findall(r'\d+',i.get('İl', None))[0])
        
        
us_movie_years = []

for i in prop_us:
    if i.get('İl', None):
        us_movie_years.append(re.findall(r'\d{4}',i.get('İl', None))[0])
        


year = [i for i in range(1910, 2030, 10)]
annual_azeri = [ int(int(i) / 10)*10+10  for i in az_movie_years]
annual_azeri_count = [annual_azeri.count(i) for i in year]

annual_us = [ int(int(i) / 10)*10+10  for i in us_movie_years]
annual_us_count = [annual_us.count(i) for i in year]

p1 = plt.plot(year, annual_azeri_count, color='g')
p2 = plt.plot(year, annual_us_count, color='orange')
plt.xlabel('Years')
plt.ylabel('Number of Articles')
plt.title('Azerbaijani vs US Movie Occurances in Azerbaijani Wikipedia from 1910 till 2019')
plt.yticks(np.arange(0, 500, 10))
plt.xticks( year)
plt.legend((p1[0], p2[0]), ('Azerbaijani', 'US'))
plt.show()

############ Bar Plot #########################################


ind = np.arange(len(annual_azeri_count))  # the x locations for the groups
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind - width/2, annual_azeri_count, width,
                label='Azerbaijani')
rects2 = ax.bar(ind + width/2, annual_us_count, width,
                label='US')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Number of Articles')
ax.set_xlabel('Year Intervals')
ax.set_title('The Number of Azerbaijani Wikipedi Articles about Azerbaijani vs US Movies shot from 1900 till 2019')
ax.set_xticks(ind)
ax.set_xticklabels(('1900-1910', '1910-1920','1920-1930','1930-1940','1940-1950',
                    '1950-1960','1960-1970','1970-1980','1980-1990','1990-2000',
                    '2000-2010', '2010-2020'))
ax.legend()


def autolabel(rects, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0, 'right': 1, 'left': -1}

    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(offset[xpos]*3, 3),  # use 3 points offset
                    textcoords="offset points",  # in both directions
                    ha=ha[xpos], va='bottom')


autolabel(rects1, "center")
autolabel(rects2, "center")

fig.tight_layout()

plt.show()

############################## Icherisheher ####################################

import pandas as pd
import re
import pickle
import matplotlib.pyplot as plt
import numpy as np

with open('./data/wikipedia_parsed_v2.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    # Note that the column names are as follows:
    """
    ['title', 'bodytext','properties', 'wikipedia_links', 'external_links', 'kateqoriyalar', 'location']
    """
    data = pickle.load(f)

for title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar, location in data:
    if title == 'İçərişəhər':
        print(title, bodytext,properties, wikipedia_links, external_links, kateqoriyalar, location)
        prop = properties
        cate = kateqoriyalar