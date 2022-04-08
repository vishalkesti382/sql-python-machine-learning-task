#!/usr/bin/env python
# coding: utf-8

# In[16]:


# Importing Sqlite3 Module
import sqlite3
import pandas as pd

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn import metrics


# ## Task 1

# In[26]:


try:

    # Making a connection between sqlite3
    # database and Python Program
    sqliteConnection = sqlite3.connect('database.db')

    # If sqlite3 makes a connection with python
    # program then it will print "Connected to SQLite"
    # Otherwise it will show errors
    print("Connected to SQLite")

    # Getting all tables from sqlite_master
    sql_query = """SELECT post_id,
                text,
                topic,
                forum_id,
                case
                    when (birth_year % 10) in (0, 1) then 'test'
                    else 'train'
                end as partition
            from posts
            left join subforums using (forum_id)
            left join users using (user_id)"""

    # Creating cursor object using connection object
    cursor = sqliteConnection.cursor()

    # executing our sql query
    cursor.execute(sql_query)
    print("List of tables\n")
    
    #Create dataframe from SQL table
    complete_data = pd.DataFrame(cursor.fetchall(), columns = ['id', 'text', 'forum', 'forum_id', 'partition'])
    print (complete_data.head())

except sqlite3.Error as error:
    print("Failed to execute the above query", error)

finally:

    # Inside Finally Block, If connection is
    # open, we need to close it
    if sqliteConnection:

        # using close() method, we will close
        # the connection
        sqliteConnection.close()

        # After closing connection object, we
        # will print "the sqlite connection is
        # closed"
        print("the sqlite connection is closed")


# In[32]:


complete_data.shape


# In[33]:


complete_data.isna().sum()


# ## Task 2

# In[28]:


train_df = complete_data[complete_data['partition']=='train'] 


# In[29]:


train_df.head()


# In[246]:


#Separating text and labels
train_x = train_df['text']
train_y = train_df['forum_id']


# In[247]:


#Separating the data into validation dataset. For sake of interpretability we will call this as Validation dataset instead
# of test
val_df = complete_data[complete_data['partition']=='test'] 


# In[248]:


val_df.head()


# In[249]:


#Separating text and labels
val_x = val_df['text']
val_y = val_df['forum_id']


# In[250]:


# Initialize Tf-Idf Vectorizer
vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5, stop_words='english')


# In[251]:


#Vectorize text and extract features
print("Extracting features from the train data using the same vectorizer")
X_train = vectorizer.fit_transform(train_x)
print("Extracting features from the validation data using the same vectorizer")
X_val = vectorizer.transform(val_x)


# In[253]:


#Linear Support Vector for Classification
clf = LinearSVC()


# In[254]:


clf.fit(X_train, train_y)


# ## Task 3

# In[258]:


pred = clf.predict(X_val)
score = metrics.accuracy_score(val_y, pred)
print("accuracy:   %0.3f" % score)


# In[259]:


target_names = ['0','1','2','3','4']


# In[260]:


print("classification report:")
print(metrics.classification_report(val_y, pred, target_names=target_names))


# ## Task 4
# 
# I noticed that the json data has some unexpected data which was causing error while loading the data directly in the pandas dataframe. Hence I had to clean the data before using it further.

# In[237]:


import json
import ast
ast.literal_eval
with open('new_posts.json') as datafile:
    data = datafile.read()


# In[238]:


row_list = [row for row in data.split('\n') if row != '']


# In[261]:


#Unexpected text between the json data on row 2001
row_list[2001]


# In[241]:


row_dict_list = []
for index,row in enumerate(row_list):
    try:
        row_dict_list.append(json.loads(row))
    except:
        pass


# In[242]:


len(row_dict_list)


# In[243]:


#Converting the json data to pandas dataframe
test_df = pd.DataFrame.from_dict(row_dict_list)


# In[244]:


test_df


# In[263]:


#Vectorize text and extract features
test_x = test_df['text']
print("Extracting features from the test data using the same vectorizer")
X_test = vectorizer.transform(test_x)


# In[264]:


#Predict on test data
final_pred = clf.predict(X_test)


# In[265]:


final_pred


# In[267]:


test_df['predicted_forum_id'] = final_pred


# In[268]:


def check_forum(x):
    if x['forum_id']!= x['predicted_forum_id']:
        return x['predicted_forum_id']
    else:
        return None
    


# In[269]:


test_df['reassign'] = test_df.apply(check_forum, axis=1)


# In[270]:


test_df


# In[233]:


test_df.dtypes


# In[271]:


test_df.to_csv('result.csv')


# In[ ]:




