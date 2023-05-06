from spellchecker import SpellChecker
import Search
#import docx
import spacy
from spacy.lang.en import English
from collections import Counter
from bs4 import BeautifulSoup
nlp = spacy.load("en_core_web_sm")

# Beautiful soup to extract paragraphs from XML files
def check(filename):
    print("Processing: {}".format(filename))
    with open(filename, "r",encoding="utf8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
    a = ""
    for i in range(len(soup.find_all("ce:para"))):
         k = soup.find_all("ce:para")[i].text
         a = a+" "+k

    
    doc = nlp(a)
    tokenList = [token.text for token in doc]

    lower=[]
    for i in tokenList:
        if i.isalpha():
            lower.append(i.lower())
        else:
            continue

    counts = Counter(lower)
    
    spell = SpellChecker()
    misspelled  = spell.unknown(lower)
    
    kp = Search.KeywordProcessor()
    trie_dict = kp.add_keyword_from_file("ScientificDictionary.txt")
    
    final_misspell = []
    for i in misspelled:
        if kp.extract_keywords(i) == []:
            final_misspell.append(i)
        else:
            continue
    
    final_list = {}
    
    for i in final_misspell:
        final_list[i] = dict(counts)[i]
        
        '''
        if dict(counts)[i]==1:
            print()
            final_list.append(i)
        else:
            continue
        '''
    return final_list