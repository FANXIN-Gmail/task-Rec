from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from gensim import corpora, models
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# akinwale 433/191/242

def LsiModel_vector(texts, technologies, platforms, num_topics=2, flag=False):

    corpus = []
    vector = []

    for index, value in texts.items():
        if flag:
            words = word_tokenize(value) + technologies[index] + platforms[index]
            corpus.append(words)
        else:
            words = word_tokenize(value)
            corpus.append(words)

    dictionary = corpora.Dictionary(corpus)
    corpus = [dictionary.doc2bow(words) for words in corpus]

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics)
    corpus_lsi = lsi[corpus_tfidf]

    for text in corpus_lsi:
        word_vector = []
        for word in text:
            word_vector.append(word[1])
        vector.append(word_vector)

    return vector

    # index = similarities.MatrixSimilarity(corpus_lsi)
    # sims = index[corpus_lsi[0]]
    # print(sims)
    #
    # sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
    # print(sort_sims)


def prizes_vector(prizes):

    prize_list = []
    for prize in prizes.values:
        prize = prize.replace("[", "")
        prize = prize.replace("]", "")
        prize_list.append(float(prize))
    return prize_list


def match_vector(matches):

    vector = []
    for match in matches.values:
        match = match.replace("[", "")
        match = match.replace("]", "")
        match = match.replace("'", "")
        vector.append(match.split(", "))
    return vector


def Distance(a, b):

    # X_technologies:45
    # X_platforms:14

    a_float = a[0:14].astype(float)
    b_float = b[0:14].astype(float)

    Challenge_Overview = pairwise_distances([a_float[0:10], b_float[0:10]], metric="cosine")
    name = pairwise_distances([a_float[10:12], b_float[10:12]], metric="cosine")
    prizes = abs(a_float[12] - b_float[12])
    duration = abs(a_float[13] - b_float[13])

    # technologies = np.append(a[14].split(", "), b[14].split(", "))
    # technologies_0 = np.sum(pd.value_counts(technologies).values == 2)
    # technologies_1 = np.array([len(a[14].split(", ")), len(b[14].split(", "))]).max()
    # technologies = technologies_0 / technologies_1

    result = Challenge_Overview[0][1] + name[0][1] + prizes + duration

    return result


# SAMPLES = pd.read_csv("SAMPLES.csv", encoding="utf-8")
# REGISTRANTS = SAMPLES["REGISTRANTS"]
# SUBMISSIONS = SAMPLES["SUBMISSIONS"]
# REGISTRANTS_list = []
# SUBMISSIONS_list = []
#
# for REGISTRANT in REGISTRANTS.values:
#     REGISTRANTS_list = REGISTRANTS_list + word_tokenize(REGISTRANT)
#
# for SUBMISSIONS in SUBMISSIONS.values:
#     SUBMISSIONS_list = SUBMISSIONS_list + word_tokenize(SUBMISSIONS)
#
# REGISTRANTS_Count = pd.Series(REGISTRANTS_list).value_counts()
# SUBMISSIONS_Count = pd.Series(SUBMISSIONS_list).value_counts()

# REGISTRANTS_Count[0:20].plot(kind='bar')
# plt.show()

# SUBMISSIONS_Count[0:20].plot(kind='bar')
# plt.show()

FEATURES = pd.read_csv("MULTICLASS_SAMPLES.csv", encoding="utf-8")
label = FEATURES["label"].values
Count = [0, 0]
index_train = []
index_test = []

for index, value in enumerate(label.tolist()):

    if Count[value] == 40:
        index_train.append(index)
        continue
    else:
        index_test.append(index)
        Count[value] += 1

y_train = label[index_train]
y_test = label[index_test]

X_technologies = np.array(match_vector(FEATURES["technologies"]))
X_platforms = np.array(match_vector(FEATURES["platforms"]))
X_Challenge_Overview = np.array(LsiModel_vector(FEATURES["Challenge_Overview"], X_technologies, X_platforms, 10))
X_name = np.array(LsiModel_vector(FEATURES["name"], X_technologies, X_platforms, 2, True))
X_prizes = np.array(prizes_vector(FEATURES["prizes"])).reshape(-1, 1)
X_duration = FEATURES["duration"].values.reshape(-1, 1)

X = np.hstack((X_Challenge_Overview, X_name, X_prizes, X_duration))

mms = MinMaxScaler()
X_norm = mms.fit_transform(X)

X_train = X_norm[index_train]
X_test = X_norm[index_test]

# X_train = X_train[:, 10:12]
# X_test = X_test[:, 10:12]

# knn = KNeighborsClassifier(n_neighbors=3, weights="distance", leaf_size=30, metric=Distance)
# knn.fit(X_train, y_train)
# print(knn.score(X_train, y_train))
# print(knn.score(X_test, y_test))

# knn = KNeighborsClassifier(n_neighbors=3, weights="uniform", leaf_size=30, algorithm="auto", metric="cosine")
# n_neighbors = [n + 1 for n in range(10)]
# weights = ["uniform", "distance"]
# leaf_size = [10, 20, 30, 40, 50]
# param_grid = {"n_neighbors": n_neighbors, "weights": weights, "leaf_size": leaf_size}
# GridSearch_lr = GridSearchCV(estimator=knn, param_grid=param_grid, cv=10, iid="False", scoring="accuracy")
# GridSearch_lr.fit(X_norm[:, 0:10], label)
# print(GridSearch_lr.best_score_)
# print(GridSearch_lr.best_params_)
# print(GridSearch_lr.best_estimator_)

# lr = LogisticRegression(C=1, solver="newton-cg", multi_class="auto", penalty='l2', random_state=0)
# lr.fit(X_train, y_train)
# print(lr.score(X_train, y_train))
# print(lr.score(X_test, y_test))

# lr = LogisticRegression(C=1, solver="newton-cg", multi_class="auto", max_iter=200, l1_ratio=0, random_state=0)
# C = [pow(10, c) for c in range(-10, 10)]
# solver_0 = ["newton-cg", "lbfgs", "sag", "saga"]
# penalty_0 = ["l2"]
# solver_1 = ["liblinear", "saga"]
# penalty_1 = ["l1"]
# solver_2 = ["saga"]
# penalty_2 = ["elasticnet"]
# param_grid = [{"C": C, "solver": solver_0, "penalty": penalty_0},
#               {"C": C, "solver": solver_1, "penalty": penalty_1},
#               {"C": C, "solver": solver_2, "penalty": penalty_2}]
# GridSearch_lr = GridSearchCV(estimator=lr, param_grid=param_grid, cv=10, iid="False", scoring="accuracy")
# GridSearch_lr.fit(X_norm, label)
# print(GridSearch_lr.best_score_)
# print(GridSearch_lr.best_params_)
# print(GridSearch_lr.best_estimator_)


# forest = RandomForestClassifier(n_estimators=1000, max_depth=3, random_state=0)
# forest.fit(X_train, y_train)
# print(forest.score(X_train, y_train))
# print(forest.score(X_test, y_test))
#
# importances = forest.feature_importances_
# indices = np.argsort(importances)[::-1]
# feat_labels = pd.DataFrame(X_train).columns[0:]
# plt.title("Feature Importances")
# plt.bar(range(X_train.shape[1]), importances, color="lightblue", align="center")
# plt.xticks(range(X_train.shape[1]), feat_labels, rotation=90)
# plt.xlim([-1, X_train.shape[1]])
# plt.show()
