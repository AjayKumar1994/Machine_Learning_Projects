import Search
import Genous_search_one
import spacy
#import docx
from spacy.lang.en import English

nlp = spacy.load('en_core_web_sm')

from bs4 import BeautifulSoup



# function to check casing in the file
def check_casing(line, i):
    print("Processing: {}".format(line))
    doc = nlp(line)
    tokenlist = [(token.text, token.tag_) for token in doc]
    #print(tokenlist)
# title casing :    
    if(i=="Title"):
       # Checks for the first word/token in title
        for index, token in enumerate(tokenlist):
            if token[0].isalpha():
                if index == 0:
                    if token[0] == token[0].title():
                           continue
                    else:
                        print("ERROR:",token[0],token[1],"is not capitalised")
                # checks for the rest of the tokens in title (articles and prepositions)
                else:
                    if ((token[1] == 'DT') or (token[1] =='IN') ):
                        if token[0] == token[0].title():
                            print("ERROR:",token[0],token[1],"is capitalised")
                    elif (str(doc[index]).isupper()==0):
                        print("ERROR:",token[0],token[1],"is not capitalised")
            else:
                continue

 # Sentence Casing       
    elif(i=="Sentence"):
        # Checks for the first word/token in sentence
        for index, token in enumerate(tokenlist):
            if token[0].isalpha():
                if index == 0:
                    if token[0] == token[0].title():
                        continue
                    else:
                        print("ERROR:",token[0],"is capitalised")
                # Checks for the rest tokens in sentence
                else:
                    if (token[0][0] == token[0][0].title()):
                        if Genous_search_one.Search_dict(token[0]):
                            continue
                        else:
                            print("ERROR:",token[0],"is capitalised")
                    else:
                        if Genous_search_one.Search_dict(token[0]):
                            print("ERROR:",token[0],"is not capitalised")
                        else:
                            continue
                    # condition for parts of speech (Noun, Verb or Adjective)
                    if (token[1] == ("NN" or "VB" or "JJ")) and  (token[0] != token[0].title()):
                        if Genous_search_one.Search_dict(token[0]):
                            print("WARNING:",token[0],"is not capitalised")
                        else:
                            continue
                    elif ((token[1] != 'NNP') and  (token[0] == token[0].title())):
                        print("WARNING:",token[0],"is capitalised")
                        
                    
            else:
                continue
# Using Beutiful Soup to read XML input files for the test cases(both section and title), output is the casing.
def unit_test(filename, case):
    with open(filename, "r",encoding="utf8") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
    for i in range(len(soup.find_all("ce:section-title"))):

    
        a = soup.find_all("ce:section-title")[i].text
        check_casing(a, case)
            
    
        