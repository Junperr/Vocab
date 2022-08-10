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
['eng','fr','spn','jp','kr','chn','gr','dth','sw','ru','prt','pl',\
          'rn','cz','grk','trk','ice','ar','na']
part_url = {
    "freng":'/enfr/',
    "engfr":'/enfr/',
    "spneng":'/es/en/translation.asp?spen=',
    "engspn":'/es/translation.asp?tranword=',
    "jpeng":'/jaen/',
    "engjp":'/enja/',
    "kreng":'/koen/',
    "engkr":'/enko/',
    "chneng":'/zhen/',
    "engchn":'/enzh/',
    "greng":'/deen/',
    "enggr":'/ende/',
    "dtheng":'/nlen/',
    "engdth":'/ennl/',
    "sweng":'/sven/',
    "engsw":'/ensv/',
    "rueng":'/ruen/',
    "engru":'/enru/',
    "prteng":'/pten/',
    "engprt":'/enpt/',
    "pleng":'/plen/',
    "engpl":'/enpl/',
    "rneng":'/roen/',
    "engrn":'/enro/',
    "czeng":'/czen/',
    "engcz":'/encz/',
    "grkeng":'/gren/',
    "enggrk":'/engr/',
    "trkeng":'/tren/',
    "engtrk":'/entr/',
    "iceeng":'/isen/',
    "engice":'/enis/',
    "areng":'/aren/',
    "engar":'/enar/'
}

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
        
website = 'https://www.wordreference.com/enfr/turkey'
# print(lookfor_trads(website))
# website = 'https://www.wordreference.com/enfr/mess'
# print(lookfor_trads(website))

default_dic = {'frword':'', 'toword':[], 'meaning':'', 'frex':'', 'toex':'', 'charac':{}}

def eng_toword_chn(containers):
    Toword = containers.find_elements(by="xpath",\
        value="./td[@class='ToWrd']/span[@class='zhgroup']" )
    trads = []
    for x in Toword:
        chn_trad = cut_multi_trad(driver.execute_script("""
var parent = arguments[0];
var child = parent.firstChild;
var ret = "";
while(child) {
    if (child.nodeType === Node.TEXT_NODE)
        ret += child.textContent;
    child = child.nextSibling;
}
return ret;
""", x),sep='，')
        try:
            pinyin = cut_multi_trad(x.find_element(by="xpath",\
                            value="./span[@class='pinyintxt']").text,sep='，')

        except:
            for ind in range (len(chn_trad)):
                trads.append(f"TC: {chn_trad[ind]}")
        else:
            if len(chn_trad) == len(pinyin):
                for ind in range (len(chn_trad)):
                    trads.append(f"SC: {chn_trad[ind]}")
                    if pinyin[ind] != '': 
                        trads.append(f"Pinyin: {pinyin[ind]}")
            else:
                for ind in range (len(chn_trad)):
                    trads.append(f"SC: {chn_trad[ind]}")
                for ind in range (len(pinyin)):
                    if pinyin[ind] != '': 
                        trads.append(f"Pinyin: {pinyin[ind]}")
    trads_txt = ""
    for i in range(len(trads)-1):
        trads_txt = trads_txt + trads[i] + ','
    return trads_txt + trads[-1]

def cut_spaces(txt):
    temp = ''
    j = 0
    start = False
    end = ''
    while j < len(txt):
        if txt[j] != ' ':
            if not(start):   
                start = True
                temp = temp + txt[j]
                end = ''
            else:
                temp = temp + end
                temp = temp + txt[j]
                end = ''
        else:
            end = end + ' '
        j+=1
    return temp

def cut_multi_trad(txt,sep=','):
    stock = txt.split(sep)
    for i in range (len(stock)):
        stock[i] = cut_spaces(stock[i])
    return stock

def all_details(La,Lb,word):
    
    t = part_url[La+Lb]
    website = f'https://www.wordreference.com{t}{word}'
    
    driver.get(website)
    if La == 'ice' or Lb == 'ice':
        principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Aðalþýðingar']/../../../*"
    else:
        principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Principal Translations']/../../../*"
    # wordreference got many translation we limit ourself to main one only
    containers = driver.find_elements(by="xpath",\
                    value = principal_trads + "/tr[(@class='even' or @class='odd')]" )
    # we get every line in main translation section
    sep_trad = []
    # return containers
    current_trad = default_dic.copy()
    current_trad["toword"] = []
    current_trad["charac"] = {}
    
    for i in range (len(containers)):
        # print("check 2")
        is_new_trad = containers[i].get_attribute('id') != ''
        # to know when when we change from a translation to another we check
        # if it contain an id attribute
        if is_new_trad and current_trad != default_dic:# if not the first trad
            # print("check 1")
            sep_trad.append(current_trad)    
            current_trad = default_dic.copy()
            current_trad["toword"] = []
            current_trad["charac"] = {}
            Frword = containers[i].find_element(by="xpath",\
                                            value="./td[@class='FrWrd']/strong" ).text
            # Frword contain the word we translate
            try:# wordreference is not structured the exact same ways,
                # with some languages
                meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                             value="./td[not(@class)]").text)[0]
            except:
                meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                             value="./td[@class='ltr']").text)[0]
                # meaning contain the context where the word is used
            if La == 'chn' or Lb == 'chn' :
                Toword = cut_multi_trad(eng_toword_chn(containers[i]))
                # return Toword
            else:
                Toword = cut_multi_trad(cut_first_charx(containers[i].find_element(by="xpath",\
                    value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0])
            current_trad['frword'] = Frword
            current_trad['meaning'] = meaning
            for x in Toword:
                current_trad['toword'].append(x)
            
        else:
            # print("check 3")
            if is_new_trad:# if it's the first trad
                Frword = containers[i].find_element(by="xpath",\
                                                value="./td[@class='FrWrd']/strong" ).text
                try:
                    meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                                 value="./td[not(@class)]").text)[0]
                except:
                    meaning = cut_first_charx(containers[i].find_element(by="xpath",\
                                                 value="./td[@class='ltr']").text)[0]
                if La == 'chn' or Lb == 'chn':
                    Toword = cut_multi_trad(eng_toword_chn(containers[i]))
                
                else:
                    Toword = cut_multi_trad(cut_first_charx(containers[i].find_element(by="xpath",\
                        value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0])

                current_trad['frword'] = Frword
                current_trad['meaning'] = meaning
                for x in Toword:
                    current_trad['toword'].append(x)
            else:# if it's complement on the tard (examples of sentences using the words)
                try:
                    if La == 'chn' or Lb == 'chn':
                        add_toword = cut_multi_trad(eng_toword_chn(containers[i]))
                    
                    else:
                        add_toword = cut_multi_trad(cut_first_charx(containers[i].find_element(by="xpath",\
                                            value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0])
                except:pass
                else:
                    
                    try:
                        characs = containers[i].find_element(by="xpath",\
                                                    value="./td[@class='To2']/span" ).text
                    except:pass
                    else:
                        for x in add_toword:
                            current_trad['charac'][len(current_trad["toword"])] = characs
                            current_trad["toword"].append(x)
                try:
                    Frex = cut_spaces(containers[i].find_element(by="xpath",\
                                          value="./td[@class='FrEx']").text)
                except: pass
                else: current_trad['frex'] = Frex
                try:
                    Toex = cut_spaces(containers[i].find_element(by="xpath",\
                                          value="./td[@class='ToEx']").text)
                except: pass
                else: current_trad['toex'] = Toex
                
            # print(current_trad)
    if current_trad != default_dic:
        sep_trad.append(current_trad)  
    
    for x in sep_trad:
        if len(x["toword"]) == 1:
            print(f'{x["frword"]} \nwith the meaning of {suppr_parenthesis(x["meaning"])}',
              f'is translated to {x["toword"][0]}',sep='\n')
            if x["frex"] != '' or x["toex"] != '':
                print(f'For example \n{x["frex"]}\nwould be translated to \n{x["toex"]}\n')
            else:
                print("Word reference do not provide example for this translation\n")
        else:
            print(f'{x["frword"]} \nwith the meaning of {suppr_parenthesis(x["meaning"])}',
              'is translated to:',sep='\n')
            for t in range(len(x["toword"])):
                if x["charac"].get(t) != None:
                    print(f"{t+1}) {x['toword'][t]} with the nuance of {x['charac'].get(t)}")
                else:
                    print(f"{t+1}) {x['toword'][t]}")
            if x["frex"] != '' or x["toex"] != '':
                print(f'For example \n{x["frex"]}\nwould be translated to \n{x["toex"]}\n')
            else:
                print("Wordreference do not provide example for this translation\n")
    # print(default_dic)

# all_details(website)
    