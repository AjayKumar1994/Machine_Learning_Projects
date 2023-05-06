
# coding: utf-8

# In[1]:


from sklearn.preprocessing import OneHotEncoder
from keras.layers.core import Dense, Activation, Dropout
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.datasets import imdb

import pandas as pd
import numpy as np
import os


# In[2]:


maxlen = 30
labels = 3


# In[3]:


data = pd.read_csv("uk-us-cn.csv", header = None)
data.columns = ["Word", "Type"]
data["WordLen"] = [len(str(i)) for i in data["Word"]]
data_filtered = data[(data["WordLen"] >= 2)]
data_filtered = data_filtered[data_filtered["Word"] != "flyer / flier"]
data_filtered = data_filtered[data_filtered["Word"] != "flier / flyer"]


# In[4]:


data_filtered.groupby("Type")["Word"].count()


# In[5]:


words = data_filtered["Word"]
typeofWord = data_filtered["Type"]
vocab = set(' '.join([str(i) for i in words]))
vocab.add('END')
len_vocab = len(vocab)


# In[6]:


print(vocab)
print("vocab length is ",len_vocab)
print ("length of data_filtered is ",len(data_filtered))


# In[7]:


char_index = dict((c, i) for i, c in enumerate(vocab))
print(char_index)
len(char_index)


# In[8]:


msk = np.random.rand(len(data_filtered)) < 0.8
train = data_filtered[msk]
test = data_filtered[~msk]


# In[9]:


train_X = []
trunc_train_words = [str(i)[0:30] for i in train.Word]
for i in trunc_train_words:
    tmp = [char_index[j] for j in str(i)]
    for k in range(0,maxlen - len(str(i))):
        tmp.append(char_index["END"])
    train_X.append(tmp)


# In[10]:


def set_flag(i):
    tmp = np.zeros(28);
    tmp[i] = 1
    return(tmp)


# In[11]:


train_X = []
train_Y = []
trunc_train_name = [str(i)[0:maxlen] for i in train.Word]

for i in trunc_train_name:
    tmp = [set_flag(char_index[j]) for j in str(i)]
    for k in range(0, maxlen - len(str(i))):
        tmp.append(set_flag(char_index["END"]))
    train_X.append(tmp)

for i in train.Type:
    if i == 'UK':
        train_Y.append([1,0,0])
    elif i== "US":
        train_Y.append([0,1,0])
    else:
        train_Y.append([0,0,1])

l = np.asarray(train_X)
l2 = np.asarray(train_Y)


# In[12]:


type(train_X)


# ## Building LSTM Model

# In[27]:


print('Build model...')
model = Sequential()
model.add(LSTM(512, return_sequences=True, input_shape=(maxlen, len_vocab)))
model.add(Dropout(0.2))
model.add(LSTM(512, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(3))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam',metrics=['accuracy'])


# In[28]:


len_vocab


# In[29]:


test_X = []
test_Y = []
trunc_test_name = [str(i)[0:maxlen] for i in test.Word]

for i in trunc_test_name:
    tmp = [set_flag(char_index[j]) for j in str(i)]
    for k in range(0, maxlen - len(str(i))):
        tmp.append(set_flag(char_index["END"]))
    test_X.append(tmp)

for i in test.Type:
    if i == 'UK':
        test_Y.append([1,0,0])
    elif i == "US":
        test_Y.append([0,1,0])
    else:
        test_Y.append([0,0,1])

print(np.asarray(test_X).shape)
print(np.asarray(test_Y).shape)


# In[30]:


batch_size = 250
model.fit(l, l2, batch_size = batch_size, nb_epoch=100, validation_data = (np.asarray(test_X), np.asarray(test_Y)))


# In[51]:


#model.fit(l, l2, batch_size = batch_size, nb_epoch=50, validation_data = (np.asarray(test_X), np.asarray(test_Y)))


# In[47]:


score, acc = model.evaluate(np.asarray(test_X), np.asarray(test_Y))
print('Test score:', score)
print('Test accuracy:', acc)


# In[50]:


name=["Anodizes".lower()]
X=[]
trunc_name = [i[0:maxlen] for i in name]
for i in trunc_name:
    tmp = [set_flag(char_index[j]) for j in str(i)]
    for k in range(0, maxlen - len(str(i))):
        tmp.append(set_flag(char_index["END"]))
    X.append(tmp)
pred=model.predict(np.asarray(X))
pred

