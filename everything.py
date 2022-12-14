 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 10:05:28 2022

@author: Junper
"""

import sqlite3  as sql
import urllib.request
import os
from automatic_translation import all_details
import time

current_dir = os.getcwd()

conn=sql.connect(current_dir + '/training2.db')
cursor = conn.cursor()

lg_code = ['en','fr','es','jp','ko','zh','de','nl','sv','ru','pt','pl',\
          'ro','cz','gr','tr','is','ar','it','na']

for x in lg_code:
    
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS '{x}'(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        UNIQUE (word)) 
        """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS trad(
    id_trad INTEGER PRIMARY KEY AUTOINCREMENT,
    la TEXT NOT NULL,
    lb TEXT NOT NULL,
    ida INTEGER NOT NULL,
    idb TEXT,
    groups TEXT,
    UNIQUE (la,lb,ida))
    """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats(
    id_trad INTEGER PRIMARY KEY,
    C_main TEXT NOT NULL,
    C_other INT NOT NULL,
    Total Int NOT NULL,
    Lastones TEXT NOT NULL,
    next_revision INT NOT NULL,
    status TEXT NOT NULL)
    """)

conn.commit()
conn.close()
#%%

def cut_first_charx(text, x = '\n', avoid = '\r'):
    """
    It cut in 2 a text at the first 'x' character while avoiding 
    all 'avoid' character
    """
    t = ['','']
    i = 0
    while text[i] != x:
        if text[i] != avoid:
            t[0] = t[0] + text[i]
        i += 1
    for j in range (i,len(text)):
        t[1] = text[j]
    return t

def add_word(w,L):
    """
    add the word w to the table for language L
    """
    conn = sql.connect(current_dir + '/training2.db')
    cursor = conn.cursor()
    cursor.execute("""
        Insert Into {}  (word) Values ('{}')
                   """.format(L,w))
    
    conn.commit()
    conn.close()
    pass

def Unique_error_handler(original_word,La,Lb,ida,idb):
    """

    Parameters
    ----------
    original_word : STR
        The word associated to ida in La language
    La : STR
        Code for the language of word you want translated.
    Lb : STR
        Code for the language of translations.
    ida : INT
        id of the word you want to translate in La language.
    idb : STR
        ids on csv string of the translated meaning in Lb language
        main translation should be the first id of idb.

    USE: It handle the case when you try to add a word which already have 
    a translation from La to Lb

    Returns
    -------
    None.

    """
    
    print(original_word,"""is already translated to :""")
    conn=sql.connect(current_dir + '/training2.db')
    cursor = conn.cursor()
    old_id_str = cursor.execute(f"""
                    Select idb from trad
                    Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                    """).fetchone()[0]
    conn.commit()
    conn.close()
    old_id = [ int(x) for x in old_id_str.split(',')]
    # we get id of the past translation for the word
    # we keep the original string for + section
    
    for i in range (0,len(old_id)) :
        conn = sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        word_id = cursor.execute(f"""
                        Select word from {Lb}
                        Where id = {old_id[i]}
                        """).fetchone()[0]
        conn.commit()
        conn.close()
        if i == 0:
            print(f'main past translation is {word_id}')
        elif i == 1:
            print('other past translation are :')
            print(f'{i}) {word_id}')
        else:
            print(f'{i}) {word_id}')
        # and we print the words associated to those ids
    print("if you want to add more translation write +",
          "if you want to replace write r",
          "everything else won't change anything",sep='\n')
    answer2 = str(input())
    # User make a choice
        
    if answer2 == 'r':
        # we want to replace old translation by the new ones
        conn=sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        cursor.execute(f"""
                        Update trad Set idb = '{idb}'
                        Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                        """)
        conn.commit()
        conn.close()
        new_trad = idb
        # we just replace the past idb by the new one
        
    elif answer2 == '+':
        # we keep old translation and add the new ones to them
        new_id = idb.split(',')
        
        print("by default we take new main tranlation as the main one",
              "if you want to keep old main translation write 1"
              ,sep = '\n')
        try :
            answer3 = int(input())
        except ValueError:
            answer3 = None
        # if user do not answer an integer it won't work and the
        # only useful value is 1 we don't use answer3 == '1' if the user put
        # a space it won't work
        
        print(old_id)
        new_trad_p2 = ''
        for i in range(len(old_id)) :
            if str(old_id[i]) not in new_id:
                new_trad_p2 = new_trad_p2 + str(old_id[i])
                if i != len(old_id)-1:
                    new_trad_p2 = new_trad_p2 + ','
        # new_trad_p2 contain the id of new translation for original_word
                
        if answer3 == 1:
            # here we keep past main translation
            if len(new_trad_p2)!=0:
                new_trad = old_id_str + ',' + new_trad_p2
            else:
                new_trad = old_id_str
        else :
            # here we take the new main translation
            if len(new_trad_p2)!=0:
                new_trad = idb + ',' + new_trad_p2
            else:
                new_trad = idb
                
        conn=sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        cursor.execute(f"""
                        Update trad Set idb = '{new_trad}'
                        Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                        """)
        # update of the values in the db
        conn.commit()
        conn.close()
    return new_trad,old_id_str

test_csv = current_dir + '/list_of_words.txt'
verif_csv = current_dir + '/test_words.txt'
verif_csv_kr = current_dir + '/test_words_korean.txt'

def stat_maindecomp(C_main):
    """
    Take the string for C_main and return it in a list of list 
    """
    trads = C_main.split(',')
    trad_stat = []
    if len(trads)%2 == 1:
        raise ValueError('C_main should have an even number of values')
    if len(trads) != 1:
        # seem to always append since len(trads) is odd
        current = [0,0]
        for i in range (len(trads)):
            try: 
                current[i%2] = int(trads[i])
            except:
                "C_main format isn't the good one (it was not an integer)"
            if i%2 == 1:
                trad_stat.append(current.copy())
    else:
        trad_stat.append([-1,0])
    return trad_stat

def stat_train_updater(original_word,La,Lb,ida,trad):
    """
    It update stats when a user want to add a trad to training
    """
    conn=sql.connect(current_dir + '/training2.db')
    cursor = conn.cursor()
    groups = cursor.execute(f"""
                    Select groups From trad 
                    Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                    """).fetchone()[0]
    conn.commit()
    conn.close()
    # we recup the groups (be aware that group isn't really working for the moment)
    if 'train' not in groups.split(','):
        # if the word was not part of training set we add it to it 
        conn = sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        cursor.execute(f"""
                    Update trad  set groups = 'train,{groups}'
                    Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                       """)
        id_trad = cursor.execute(f"""
                    Select id_trad From trad
                    Where ida = {ida} and la = '{La}' and lb = '{Lb}'
                       """).fetchone()[0]
                       
        C_main = cursor.execute(f"""
                        Select C_main From stats 
                        Where id_trad = {id_trad}
                       """).fetchone()
        conn.commit()
        conn.close()
    # as long as update groups we get C_main and id_trad
    main_trad = int(trad.split(',')[0])
    if C_main == None:
        # id the translation don't have stats associated to his id we
        # initialize them
        conn=sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        cursor.execute(f"""
                    Insert Into stats (id_trad,C_main,C_other,Total,Lastones,next_revision,status)
                    Values ({id_trad},'{main_trad},0',0,0,'',{int(time.time())},'to_learn')
                       """)
        conn.commit()
        conn.close()

    else:
        # there was already stat for this id_trad
        print(f'{original_word} from {La} to {Lb} is already in the training set.',
        'his stats will be updated',sep='\n')

        current_stats = stat_maindecomp(C_main)
        is_in = False
        new_stats = ''
        for x in current_stats:
            new_stats = new_stats + str(x[0]) + ',' +str(x[1]) + ','
            if x[0] == main_trad:
                is_in = True
        
        if is_in:
            new_stats = new_stats[:-1]
            # it suppress the last coma
        else:
            new_stats = new_stats + str(main_trad) + ',' + '0'
            # we add stat for current main_trad
            
        cursor.execute(f"""
                        Update stats 
                        Set C_main = '{new_stats}', next_revision = {int(time.time())}
                        Where id_trad = {id_trad}
                        """)
        # and finally we update stats with new C_main
        # there is an error there we always set_up the next_revision to now
        # whilde it's already it already got stats so it may not be to_learn
        conn.commit()
        conn.close()

import codecs

def post(source):

    if type(source)==list:#if we have manually given the data (useful for small test)
        languages = source[0].split(',')
        words = source[1].split(',')
    else:# if we use a file in our directory
        source = cut_first_charx(codecs.open(source,'r',encoding='utf-8').read())
        languages = source[0].split(',')[:-1]
        words = source[1].split(',')
    La,Lb = languages[0],languages[1]
    
    # now we have the words we want to translate and the languages
    # La is the languages of the word and Lb the language of the translations
    
    print(words)
    for w in words:
        
        l_word = w.split('/')
        if len(l_word) == 1:
            # if the word don't already have translation
            trads = all_details(La,Lb,l_word[0])
            for trad in trads:
                l_word.append(trad)
            # we add main trads for wordreference
        # l_word[0] is the word in La and l_word[1:] is the translation we have in Lb
        try: 
            add_word(l_word[0],La)
        except:pass
        for i in range (1,len(l_word)):
            try:
                add_word(l_word[i],Lb)
            except:pass
        # we add each word in the the their language table
        print(l_word)
        
        if len(l_word) >= 2:# if there is 1 trad or more
        
            print(f'are you sure of main translation for {l_word[0]}\n(chose a number)')
            print(f'current main translation is {l_word[1]}')
            print('other translation are :')
            for i in range (2,len(l_word)) :
                print(f'{i}) {l_word[i]}') 
            
            try:
                answer1 = int(input())
            except ValueError:
                answer1 = None
                
            if answer1 in [x for x in range (2,len(l_word))]:
                # if we change main translation
                l_word[1],l_word[answer1]=l_word[answer1],l_word[1]
            
            # we put the main translation at the first place in the translations
            conn = sql.connect(current_dir + '/training2.db')
            cursor = conn.cursor()
            ida = cursor.execute(f"""
                                 Select id from {La} 
                                 Where word = '{l_word[0]}'
                                 """).fetchone()[0]
            conn.commit()
            conn.close()
            # we retreive in the db the id of the word we want to translate
            
            idb = ''
            for i in range (1,len(l_word)):
                print(f"""
                                 Select id from {Lb} 
                                 Where word = '{l_word[i]}'
                                     """)
                conn=sql.connect(current_dir + '/training2.db')
                cursor = conn.cursor()
                idb = idb + str(cursor.execute(f"""
                                 Select id from {Lb} 
                                 Where word = '{l_word[i]}'
                                     """).fetchone()[0])
                conn.commit()
                conn.close()
                if i != len(l_word)-1:
                    idb = idb + ','
            
            # we create a string containing the id for all the translation
            # we want to add
                    
            try:
                # we do not use add_trad because there was issues
                # with the closing of the db due to the error handling
                conn=sql.connect(current_dir + '/training2.db')
                cursor = conn.cursor()
                cursor.execute(f"""
                    Insert Into trad  (la,lb,ida,idb,groups) Values ('{La}','{Lb}',{ida},'{idb}','')
                               """)
                conn.commit()
                conn.close()
                trad = idb
                old_trad = idb
                
                # if the word isn't already translated we add it to the db
                
            except sql.IntegrityError:# if already translated
                conn.commit()
                conn.close()# is previous cursor.execute raise an error
                # the previous commit and close are not reached so we
                # close it now (without using the next fuction it
                # wasn't necessary but i don't know why)
                
                trad,old_trad = Unique_error_handler(l_word[0], La, Lb, ida, idb)
            
        print(trad)
        print(f'do you to add the translation for {l_word[0]} to training ?','(yes or anything else)',sep='\n')
        answer4 = str(input())
        if answer4 == 'yes':
            stat_train_updater(l_word[0], La, Lb, ida, idb)
        # we add stats to our translation for training

    pass 

def settings():
    pass

import random

def score_1(l):
    # it will need an update for qcm integration in history and maybe groups
    """

    Parameters
    ----------
    l : STR
        lastones attribute in stats table

    Returns
    -------
    INT
        Score on a translation
    
    """
    l=l.split(',')[:-1][::-1] #[:-1:-1] do not work 
    s=[0]
    streak = 0
    in_streak = True
    for i in range (len(l)):
        if bool(l[i]):
            s.append(s[i]+1/((i+1)**0.5))
        else:
            s.append(s[i] -1/(i+1))
            in_streak = False
        if in_streak:
            streak+=1
    if max(s)<=1:
        return s[-1],streak
    return max(s),streak

def status_gestion(history):
    # it will need an update for qcm integration in history and maybe groups
    """
    it return the status and the next advised revision using history
    """
    next_revision = time.time()
    score,streak = score_1(history)
    if score > 3.23:
        status = 'well_known'
        next_revision += 2620800 # a month
    elif score > 2.28:
        status = 'known'
        next_revision += 604800 # a week
    elif score > 1:
        status = 'learning'
        next_revision += 86400 # a day
    elif score == 1:
        status = 'learning'
    else:
        status = 'not_known'
        
    if status == 'well_known' and streak > 4:
        status = 'mastered'
        next_revision += 5241600 # 2 month (3 with first update)
    if status == 'mastered' and streak > 5:
        status = 'ancient'
        next_revision += 7862400 # 3 month (6 with first updates)
    
    return status,next_revision

def right_update(current,ind_trad):
    """

    Parameters
    ----------
    current : List
        [0]: STR,La
        [1]: STR,Lb
        [2]: INT,ida
        [3]: STR,idb
        [4]: STR,C_main
        [5]: INT,C_other
        [6]: INT,Total
        [7]: STR,Lastones
        [8]: STR,status
        
    ind_trad : INT
        index of the given translation

    Returns
    -------
    current : List
        updated version of current while answered correctly
        (with next_revision on ninth index)

    """
    current[7] = current[7] + ' ,'
    
    if ind_trad == 0:
        # the main trad was answered
        l_stats = current[4].split(',')
        ind_trad = l_stats.index(current[3].split(',')[0])
        # ind_trad is now the index of the current main trad in l_stats
        l_stats[ind_trad + 1] = str(int(l_stats[ind_trad + 1]) + 1)
        # we update the number of correct answer for current main trad
        
        u_stats = l_stats[0] + ','
        for i in range (1,len(l_stats)-1):
            u_stats = u_stats + l_stats[i] + ','
        current[4] =  u_stats + l_stats[-1]
        # current[4] is now the new C_main 
    else:
        # another trads was answered
        current[5] += 1
        # we only increase other good answers
        
    current[8],next_revision = status_gestion(current[7])
    current.append(next_revision)
    
    return current

def false_update(current):
    """
    Update of stats while answered incorrectly
    only history status and next_revision is updated
    """
    current[7] = current[7] + ','
    current[8],next_revision = status_gestion(current[7])
    current.append(next_revision)
    return current

def train(n):
    """

    Parameters
    ----------
    n : INT
        The number of word we want to train.

    Returns
    -------
    None
        
    Description
    -----------
    
    
    """
    conn = sql.connect(current_dir + '/training2.db')
    cursor = conn.cursor()
    rows1 = cursor.execute(f"""
        Select la,lb,ida,idb,C_main,C_other,Total,Lastones,status,t.id_trad
        from trad As t Join stats As s 
        On t.id_trad = s.id_trad
        Where next_revision < {time.time()}
                   """).fetchall()
    # trads with past advise revision
    rows2 = cursor.execute(f"""
        Select la,lb,ida,idb,C_main,C_other,Total,Lastones,status,t.id_trad
        from trad As t Join stats As s 
        On t.id_trad = s.id_trad
        Where next_revision > {time.time()}
        Order By next_revision 
                   """).fetchall()
    # trads we will use when there is no longer trads with past advise revision
    
    conn.commit()
    conn.close()
    random.shuffle(rows1)
    rows = rows1 + rows2
    i=0
    while i < n:
        if i == len(rows1):
            # while we arrive at the end of the past advise
            conn=sql.connect(current_dir + '/training2.db')
            cursor = conn.cursor()
            still_pasttime = cursor.execute(f"""
                Select la,lb,ida,idb,C_main,C_other,Total,Lastones,status,t.id_trad
                from trad As t Join stats As s 
                On t.id_trad = s.id_trad
                Where next_revision < {time.time()}
                           """).fetchall()
            if still_pasttime != []:
                print("there is more urgent one")
                return train(n-i)
            # is there is new past time advise we restart the function
            conn.commit()
            conn.close()
        if i >= len(rows):
            print("not enough word in the db")
            return train (n-i) 
        # if we want to train on more word than there is in training
        current = list(rows[i])
        conn = sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        original_word = cursor.execute(f"""
                Select word From {current[0]}
                Where id = {current[2]}
                       """).fetchone()[0]
        # original_word is the word associated to ida in La
        print(f"give a translation of {original_word} in {current[1]}")
        answer = str(input())
        words = current[3].split(',')
        t_words = []
        for w in words:
            
            t_w = cursor.execute(f"""
                        Select word From {current[1]}
                        Where id = {w}
                                  """).fetchone()[0]
            t_words.append(t_w)
        conn.commit()
        conn.close()
        # t_words contains all the words in idb in Lb
        try:
            current[6] += 1
            ind_trad = t_words.index(answer)
        # we increase total and get the index of answer in t_words if the answer
        # is a right one
        except ValueError:
            # if the user is wrong
            print("wrong spelling","the translations where :",sep='\n')
            for j in range(len(t_words)):
                print(f"{j+1}) {t_words[j]}")
            print("select a number if you were correct, anything else will count as an error")
            try:
                answer1 = int(input())
            except ValueError:
                # if not an int
                answer1 = None
                current = false_update(current)
                print(current)
            else:
                if answer1 in range (1,len(t_words)+1):
                    current = right_update(current, answer1 - 1)
                    print(current)
                else:
                    # if the int is not associated with a proposed translation
                    answer1 = None
                    current = false_update(current)
                    print(current)
            
        else:
            # is the user was right with the spelling
            current = right_update(current, ind_trad)
            print(current)
        conn=sql.connect(current_dir + '/training2.db')
        cursor = conn.cursor()
        cursor.execute(f"""
                Update stats 
                Set C_main = '{current[4]}', C_other = {current[5]}, Total = {current[6]},
                    Lastones = '{current[7]}', next_revision = {current[10]}, status = '{current[8]}'
                Where id_trad = {current[9]}
                """)
        # we updates the stats
        conn.commit()
        conn.close()
        print('\n')
        i+=1
    print('training ended')
    return None

#%%
# this cell show current state of the db (the 5 first row of each table)
conn=sql.connect(current_dir + '/training2.db')
cursor = conn.cursor()

table = {}

for x in ['eng','fr','trad','stats']:
    table[x] = cursor.execute("""
                              Select * from {}
                              """.format(x)).fetchmany(5)
    
    print(f'\ntable {x} :')
    print(table[x])
    

conn.commit()
conn.close()