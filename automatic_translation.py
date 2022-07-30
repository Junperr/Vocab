# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 09:49:26 2022

@author: Junper
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options

website = 'https://www.wordreference.com/enfr/turkey'
path = 'C:/Users/Xtrem/OneDrive/Documents/~Info/chromedriver.exe'
option_driver = Options()
option_driver.add_argument("--headless")

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service, options=option_driver)

#%%

def cut_first_charx(text, x = '\n', avoid = '\r'):
    t = ['','']
    i = 0
    while i < len(text) and text[i] != x:
        if text[i] != avoid:
            t[0] = t[0] + text[i]
        i += 1
    t[1] = text[i+1:]
    return t

def suppr_parenthesis(text):
    t=''
    for i in range (len(text)):
        if text[i] not in [')','(']:
            t = t + text[i]
    return t

def lookfor_trads(website):
    
    driver.get(website)
    
    principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Principal Translations']/../../../*"
    
    other = "//table[@class='WRD']/*/tr[(@class='even' or @class='odd') and (@id)]/td[@class='FrWrd']/strong"
    
    containers = driver.find_elements(by="xpath",\
                    value=principal_trads + "/tr[(@class='even' or @class='odd') and (@id)]" )
    
    stock = {'frword':[],'meaning':[],'toword':[]}
        

    for container in containers:
        Frword = container.find_element(by="xpath",\
                                        value="./td[@class='FrWrd']/strong" ).text
        meaning = cut_first_charx(container.find_element(by="xpath",\
                                         value="./td[not(@class)]").text)[0]
        Toword = cut_first_charx(container.find_element(by="xpath",\
                value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0]
    
        stock['frword'].append(Frword)
        stock['meaning'].append(meaning)
        stock['toword'].append(Toword)
            
        print(f'{Frword}\n meaning {meaning} is translated to\n {Toword}\n')
        # print(too)

        
    return stock
        
website = 'https://www.wordreference.com/enfr/turkey'
# print(lookfor_trads(website))
# website = 'https://www.wordreference.com/enfr/mess'
# print(lookfor_trads(website))

default_dic = {'frword':'', 'toword':'', 'meaning':'', 'frex':'', 'toex':''}

def all_details(website):
    
    driver.get(website)
    
    principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Principal Translations']/../../../*"
    
    containers = driver.find_elements(by="xpath",\
                    value=principal_trads + "/tr[(@class='even' or @class='odd')]" )
    
    sep_trad = []
    
    current_trad = default_dic.copy()
    
    for i in range (len(containers)):
        
        is_new_trad = containers[i].get_attribute('id') != ''
        
        if is_new_trad and current_trad != default_dic:
            
            sep_trad.append(current_trad)    
            current_trad = default_dic.copy()
            
            Frword = containers[i].find_element(by="xpath",\
                                            value="./td[@class='FrWrd']/strong" ).text
            meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                             value="./td[not(@class)]").text)[0]
            Toword = cut_first_charx(containers[i].find_element(by="xpath",\
                    value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0]
        
            current_trad['frword'] = Frword
            current_trad['meaning'] = meaning
            current_trad['toword'] = Toword
            
        else:
            if is_new_trad:
                Frword = containers[i].find_element(by="xpath",\
                                                value="./td[@class='FrWrd']/strong" ).text
                meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                                 value="./td[not(@class)]").text)[0]
                Toword = cut_first_charx(containers[i].find_element(by="xpath",\
                        value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0]
            
                current_trad['frword'] = Frword
                current_trad['meaning'] = meaning
                current_trad['toword'] = Toword
            else:
                try:
                    Frex = containers[i].find_element(by="xpath",\
                                          value="./td[@class='FrEx']").text
                except: pass
                else: current_trad['frex'] = Frex
                try:
                    Toex = containers[i].find_element(by="xpath",\
                                          value="./td[@class='ToEx']").text
                except: pass
                else: current_trad['toex'] = Toex
                
                
            # print(current_trad)
    if current_trad != default_dic:
        sep_trad.append(current_trad)  
    
    for x in sep_trad:
        
        print(f'{x["frword"]} \nwith the meaning of {suppr_parenthesis(x["meaning"])}',
              f'is translated to {x["toword"]}',
              f'For example \n{x["frex"]} \nwould be translated to \n{x["toex"]}','',sep='\n')
        
    # print(default_dic)

all_details(website)
    