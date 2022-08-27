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

lg_abvr = ['en','fr','es','jp','ko','zh','de','nl','sv','ru','pt','pl',\
           'ro','cz','gr','tr','is','ar','it','na']
lg = ['english','french','spainish','japanese','korean','chinese','german',\
      'dutch','swedish','russian','portuguese','polish','romanian','czech',\
      'greek','turkish','icelandic','arabic','italian','other']
# the languages and their abreviations
  
test_wrd = {'en': 'bord',
 'fr': 'table',
 'es': 'mesa',
 'jp': 'テーブル',
 'ko': '테이블',
 'chn': '桌子',
 'de': 'Tisch',
 'nl': 'tafel',
 'sv': 'bord',
 'ru': 'стол',
 'pt': 'mesa',
 'pl': 'stół',
 'ro': 'masă',
 'cz': 'stůl',
 'gr': 'τραπέζι',
 'tr': 'masa',
 'ice': 'borð',
 'ar': 'طاولة',
 'it': 'tavolo'}
# the word bord translated in each of the 19 languages supported by wordreference

def cut_first_charx(text, x = '\n', avoid = '\r'):
    """

    Parameters
    ----------
    text : STR
        The text we want to cut in 2 parts
    x : STR (len(x)==1 !!!), optional
        At the first occurence of x the text will be splitted in two parts.
        The default is '\n'.
    avoid : STR (len(x)==1 !!!), optional
        In the first part all avaiod character will be deleted. The default is '\r'.

    Returns
    -------
    t : List (2 STR)
        t[0] is the part of text before the first x without avoid charracter
        and t[1] is the end of the text after the first x.

    """
    t = ['','']
    i = 0
    while i < len(text) and text[i] != x:
        if text[i] != avoid:  
            t[0] = t[0] + text[i]
        i += 1
    t[1] = text[i+1:]
    return t

def suppr_parenthesis(text):
    '''
    Return text without all parenthesis 
    '''
    t=''
    for i in range (len(text)):
        if text[i] not in [')','(']:
            t = t + text[i]
    return t

default_dic = {'frword':'', 'toword':[], 'meaning':'', 'frex':'', 'toex':'', 'charac':{}}

def eng_toword_chn(containers):
    """

    Parameters
    ----------
    containers : webelement from selenium
        The node for a word translated to chinese.

    Returns
    -------
    None.
    
    Explanation
    -----------
    

    """
    Toword = containers.find_elements(by="xpath",\
        value="./td[@class='ToWrd']/span[@class='zhgroup']" )
    # chinese is separated between sinplified chinese pinyin and traditional one
    # so instead of single word translation there is multiple translation for the
    # exact same word, so word reference use a node with a class attribute of zhgroup
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
    # that's a script found on stackoverflow at 
    # https://stackoverflow.com/questions/12325454/how-to-get-text-of-an-element-in-selenium-webdriver-without-including-child-ele
    # it allow me to get the text on the node and not his child 
    # it's not needed whilde not in chinese due to the html structure
        try:
            pinyin = cut_multi_trad(x.find_element(by="xpath",\
                            value="./span[@class='pinyintxt']").text,sep='，')
            # we get the pinyin trad if there is one
        except:
            # if there is no pinyin therefore there is no simplified chinese
            for ind in range (len(chn_trad)):
                trads.append(f"TC: {chn_trad[ind]}")
        else:
            if len(chn_trad) == len(pinyin):
                # if each SC is "linked" to a pinyin word it's almost always the case
                for ind in range (len(chn_trad)):
                    trads.append(f"SC: {chn_trad[ind]}")
                    if pinyin[ind] != '': 
                        trads.append(f"Pinyin: {pinyin[ind]}")
            else:# there not linked
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
    """
    Return txt without all spaces ate the begining and the end of the word
    """
    temp = ''
    j = 0
    start = False
    end = ''
    while j < len(txt):
        if txt[j] != ' ':
            if not(start):   
                start = True # start is set to True at the first character which
                # is différent from ' '
                temp = temp + txt[j]
                end = ''
            else:# we keep the spaces which are in the words
                temp = temp + end
                temp = temp + txt[j]
                end = ''
        else:
            end = end + ' '
        j+=1
    return temp

def cut_multi_trad(txt,sep=','):
    """
    Return a list containing each element of txt separated by a coma
    each of them without begining and end spaces
    """
    stock = txt.split(sep)
    for i in range (len(stock)):
        stock[i] = cut_spaces(stock[i])
    return stock

# https://www.wordreference.com/isen/drasl
# is a good example of why should i implemente reverse translation
# no translation is to en but many en to is while the is word is exactly the same

def recup_elem(La,Lb,containers):
    """
    For a case with id attribute it take principal elements 
    """
    current_trad = default_dic.copy()
    current_trad["toword"] = []
    current_trad["charac"] = {}
    # initialisation of current_trad
    Frword = containers.find_element(by="xpath",\
                                    value="./td[@class='FrWrd']/strong" ).text
    # Frword contain the word we translate
    try:# wordreference is not structured the exact same ways,
        # with some languages
        meaning = cut_first_charx(containers.find_element(by="xpath",\
                                     value="./td[not(@class)]").text)[0]
    except:
        meaning = cut_first_charx(containers.find_element(by="xpath",\
                                     value="./td[@class='ltr']").text)[0]
    # meaning contain the context where the word is used
    if La == 'zh' or Lb == 'zh' :
        # Due to the multiple chinese dialect the site is structured differently
        Toword = cut_multi_trad(eng_toword_chn(containers))
    else:
        Toword = cut_multi_trad(cut_first_charx(containers.find_element(by="xpath",\
            value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0])
        # this way get all the inner html of the node and cut it at the first <
        # it's way simpler than the chinese version for it but do not work
        # on the other structure 
    current_trad['frword'] = Frword
    current_trad['meaning'] = meaning
    for x in Toword:
        current_trad['toword'].append(x)
        
    return current_trad


def all_details(La,Lb,word): 
    """

    Parameters
    ----------
    La : STR
        One of the abreviation of lg_abvr.(other than na)
    Lb : STR
        One of the abreviation of lg_abvr.(other than na)
    word : STR
        A word in La which we want to translate in Lb.

    Returns
    -------
    None.
    
    Explanation
    -----------
    Print all the main translation recorded by wordreference 
    for word in La to Lb with the meaning possibe nuance and possible example.
    
    """
    
    t = '/'+La+Lb+'/'
    website = f'https://www.wordreference.com{t}{word}'
    driver.get(website)
    # we create the url and reach the webpage with our driver
    
    
    if La == 'is' or Lb == 'is':
        # Each wordreference page has 2 version, local one and english one,
        # for some all page are by default in english except for the icelandic ones
        principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Aðalþýðingar']/../../tr[@class='langHeader']/td[@class='ToWrd']/span"
    else:
        principal_trads = "//table[@class='WRD']/*/tr[@class='wrtopsection']/td[@title='Principal Translations']/../../tr[@class='langHeader']/td[@class='ToWrd']/span"
    # wordreference got many translation we limit ourself to the main ones
    
    temp_main = driver.find_elements(by="xpath",value = principal_trads)
    # we retreive all elements for main translations
    good_main = []
    inv_main = []
    try: 
        first_lg = temp_main[0].text
        # temp_main is empty if wordreference don't have data 
    except:
        print(f"Wordreference doesn't have any data concerning {word} from {lg[lg_abvr.index(La)]} to {lg[lg_abvr.index(Lb)]}")
    for i in range (len(temp_main)):
        if temp_main[i].text == first_lg:
            good_main.append(temp_main[i]) 
        else:
            inv_main.append(temp_main[i])
    ind_switch = len(good_main)
    # good_main and inv_main contain node for principal translation sections
    
    containers = []
    for x in good_main:
        for elem in x.find_elements(by="xpath",\
                            value = "./../../../tr[(@class='even' or @class='odd')]"):
            containers.append(elem)
    ind_switch = len(containers)
    for x in inv_main:
        for elem in x.find_elements(by="xpath",\
                            value = "./../../../tr[(@class='even' or @class='odd')]"):
            containers.append(elem)
    

    # we get every line in main translation section
    sep_trad = []
    # return containers
    current_trad = default_dic.copy()
    current_trad["toword"] = []
    current_trad["charac"] = {}
        
    for i in range (len(containers)):
        if i < ind_switch:
            is_new_trad = containers[i].get_attribute('id') != ''
            # to know when when we change from a translation to another we check
            # if it contain an id attribute if it got one is_new_trad is True
            if is_new_trad :#and current_trad != default_dic:# if not the first trad
                if current_trad != default_dic:
                    sep_trad.append(current_trad)
                    current_trad = recup_elem(La, Lb, containers[i])
                else:
                    current_trad = recup_elem(La, Lb, containers[i])
            else:# if it's complement on the trad 
            # (examples of sentences using the words or other translation with
            # the same meaning but with nuances)

                try:# no error if it is other translation with the same meaning
                    if La == 'zh' or Lb == 'zh':
                        add_toword = cut_multi_trad(eng_toword_chn(containers[i]))
                        
                    else:
                        add_toword = cut_multi_trad(cut_first_charx(containers[i].find_element(by="xpath",\
                                            value="./td[@class='ToWrd']" ).get_attribute("innerHTML"), x='<', avoid = '\r')[0])
                    # get the differents translation on this line 
                    # (therefore with the same nuance)
                except:
                    try:# no error if it is an example in La
                        Frex = cut_spaces(containers[i].find_element(by="xpath",\
                                              value="./td[@class='FrEx']").text)
                    except:
                        try:# no error if it is an example in Lb
                            Toex = cut_spaces(containers[i].find_element(by="xpath",\
                                                  value="./td[@class='ToEx']").text)
                        except: pass
                        else:# if it is an example in Lb
                            current_trad['toex'] = Toex
                    else:# if it is an example in La
                        current_trad['frex'] = Frex
                    
                else:# if there is other translation with the same meaning
                    
                    try:
                        characs = containers[i].find_element(by="xpath",\
                                                    value="./td[@class='To2']/span" ).text
                        # we get the nuance of the translation
                    except:pass
                    else:
                        for x in add_toword:
                            current_trad['charac'][len(current_trad["toword"])] = characs
                            current_trad["toword"].append(x)
                            # x is added to the translation and it nuance
                            # is stored in current_trad['charac'] at the ind
                            # of x in current_trad['toword]
                
            

    if current_trad != default_dic:
        sep_trad.append(current_trad)
    # we need to add the last translation
    
    for x in sep_trad:
        # this part is just the "front part" which consist of print in a console
        if x['meaning'] == '':
            x['meaning'] = 'not specified by wordreference'
            # to avoid 2 case if there is a meaning or not i made it
        if len(x["toword"]) == 1:# if there is only one translation
        
            print(f'{x["frword"]} \nwith the meaning of {suppr_parenthesis(x["meaning"])}',
              f'is translated to {x["toword"][0]}',sep='\n')
            
            if x["frex"] != '' or x["toex"] != '':# if we have an example
                print(f'For example \n{x["frex"]}\nwould be translated to \n{x["toex"]}\n')
            else:
                print("Word reference do not provide example for this translation\n")
        
        else:# if there is many translation
        
            print(f'{x["frword"]} \nwith the meaning of {suppr_parenthesis(x["meaning"])}',
              'is translated to:',sep='\n')
            
            for t in range(len(x["toword"])):
                if x["charac"].get(t) != None:
                    print(f"{t+1}) {x['toword'][t]} with the nuance of {x['charac'].get(t)}")
                else:
                    print(f"{t+1}) {x['toword'][t]}")
            # we show all the translations
            
            if x["frex"] != '' or x["toex"] != '':
                print(f'For example \n{x["frex"]}\nwould be translated to \n{x["toex"]}\n')
            else:
                print("Wordreference do not provide example for this translation\n")

    