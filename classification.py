"""
@author: han0305
"""

import pandas as pd
import numpy as np


df = pd.read_table('SMSSPamCollection', header=None, encoding='utf-8')
print(df.info())
print(df.head())

classes = df[0]
print(classes.value_counts())

from sklearn.preprocessing import LabelEncoder


encoder = LabelEncoder()
Y = encoder.fit_transform(classes)

print(Y[:10])

text_messages = df[1]
print(text_messages[:10])

processed = text_messages.str.replace(r'^.+@[^\.].*\.[a-z]{2,}$','emailaddress')


processed = processed.str.replace(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$','webaddress')


processed = processed.str.replace(r'£|\$', 'moneysymb')
    
processed = processed.str.replace(r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$','phonenumbr')
    
processed = processed.str.replace(r'\d+(\.\d+)?', 'numbr')

processed = processed.str.replace(r'[^\w\d\s]', ' ')

processed = processed.str.replace(r'\s+', ' ')

processed = processed.str.replace(r'^\s+|\s+?$', '')

processed = processed.str.lower()
print(processed)

from nltk.corpus import stopwords


stop_words = set(stopwords.words('english'))

processed = processed.apply(lambda x: ' '.join(term for term in x.split() if term not in stop_words))

ps = nltk.PorterStemmer()

processed = processed.apply(lambda x: ' '.join(ps.stem(term) for term in x.split()))

from nltk.tokenize import word_tokenize


all_words = []

for message in processed:
    words = word_tokenize(message)
    for w in words:
        all_words.append(w)
        
all_words = nltk.FreqDist(all_words)

print('Number of words: {}'.format(len(all_words)))
print('Most common words: {}'.format(all_words.most_common(15)))

word_features = list(all_words.keys())[:1500]

def find_features(message):
    words = word_tokenize(message)
    features = {}
    for word in word_features:
        features[word] = (word in words)

    return features


features = find_features(processed[0])
for key, value in features.items():
    if value == True:
        print key


messages = zip(processed, Y)

seed = 1
np.random.seed = seed
np.random.shuffle(messages)


featuresets = [(find_features(text), label) for (text, label) in messages]
from sklearn import model_selection


training, testing = model_selection.train_test_split(featuresets, test_size = 0.25, random_state=seed)
print(len(training))
print(len(testing))


from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC

model = SklearnClassifier(SVC(kernel = 'linear'))


model.train(training)

accuracy = nltk.classify.accuracy(model, testing)*100
print("SVC Accuracy: {}".format(accuracy))

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


names = ["K Nearest Neighbors", "Decision Tree", "Random Forest", "Logistic Regression", "SGD Classifier","Naive Bayes", "SVM Linear"]

classifiers = [
    KNeighborsClassifier(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    LogisticRegression(),
    SGDClassifier(max_iter = 100),
    MultinomialNB(),
    SVC(kernel = 'linear')
]

models = zip(names, classifiers)

for name, model in models:
    nltk_model = SklearnClassifier(model)
    nltk_model.train(training)
    accuracy = nltk.classify.accuracy(nltk_model, testing)*100
    print("{} Accuracy: {}".format(name, accuracy))

from sklearn.ensemble import VotingClassifier

names = ["K Nearest Neighbors", "Decision Tree", "Random Forest", "Logistic Regression", "SGD Classifier",
         "Naive Bayes", "SVM Linear"]

classifiers = [
    KNeighborsClassifier(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    LogisticRegression(),
    SGDClassifier(max_iter = 100),
    MultinomialNB(),
    SVC(kernel = 'linear')
]

models = zip(names, classifiers)

nltk_ensemble = SklearnClassifier(VotingClassifier(estimators = models, voting = 'hard', n_jobs = -1))
nltk_ensemble.train(training)
accuracy = nltk.classify.accuracy(nltk_model, testing)*100
print("Voting Classifier: Accuracy: {}".format(accuracy))

txt_features, labels = zip(*testing)

prediction = nltk_ensemble.classify_many(txt_features)

print(classification_report(labels, prediction))

pd.DataFrame(
    confusion_matrix(labels, prediction),
    index = [['actual', 'actual'], ['ham', 'spam']],
    columns = [['predicted', 'predicted'], ['ham', 'spam']])