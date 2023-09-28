__author__ = "Pierluigi Gallo"
__copyright__ = "Copyright (c) 2017, CNIT"
__version__ = "0.1.0"
__email__ = "pierluigi.gallo@cnit.it"


# print(__doc__)

import itertools
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.pyplot import plot as plt, draw, show

from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
import time
from sklearn.externals import joblib

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        np.set_printoptions(precision=2)
        # from decimal import *
        # getcontext().prec = 2
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        # tmp = format(cm[i,j], '.2f')
        plt.text(j, i, cm[i,j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# set data source in
# - "iris"   (example dataset for flower classification on petals and sepals)
# - "matlab" (matlab mesh simulator written by P. Gallo)
# - "wilab"  (wilab experiment )
data_source = "matlab"

############################### data from example

# import some data to play with
if(data_source == "iris"):
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    print ("X = %s" %X)
    print ("y = %s" %y)
    class_names = iris.target_names
    # put the original column names in a python list
    original_headers = list(df.columns.values)
    # remove the non-numeric columns
    df = df._get_numeric_data()
    # put the numeric column names in a python list
    numeric_headers = list(df.columns.values)
    # create a numpy array with the numeric values for input into scikit-learn
    numpy_array = df.as_matrix()
    # set printing options to print all data rather than a selection
    np.set_printoptions(threshold=sys.maxint)
    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y.astype(int), random_state=0)

############################### data from matlab simulations
# header description
# 0 node_ident,             - not to be used
# 1 radius,                 - not to be used
# 2 max_busy,
# 3 busy_50,
# 4 busy_90,
# 5 max_idle,
# 6 idle_50,
# 7 idle_90,
# 8 tx_neigh_G,
# 9 tx_neigh_G2,
# 10 rx_neigh_G,
# 11 rx_neigh_G2,
# 12 num_of_cliques_tx,
# 13 nodes_in_cliques_tx,
# 14 num_of_cliques_rx,
# 15 nodes_in_cliques_rx,
# 16 succ_norm_all,         - not to be used
# 17 tx_norm_all,           - not to be used
# 18 output
elif data_source == "matlab":
    df = pd.read_csv('./matlab_simulation_data2.csv')
    # put the original column names in a python list
    original_headers = list(df.columns.values)
    # remove the non-numeric columns
    df = df._get_numeric_data()
    # put the numeric column names in a python list
    numeric_headers = list(df.columns.values)
    # create a numpy array with the numeric values for input into scikit-learn
    numpy_array = df.as_matrix()
    # set printing options to print all data rather than a selection
    # np.set_printoptions(threshold=sys.maxint)

    # print ("numpy_array [:,0] = %s" %(numpy_array[:, 0]))
    X = numpy_array[:, 2:16:1]
    y = numpy_array[:, 18]
    class_names = ['flow in the middle', 'hidden nodes', 'no-interf']

    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y.astype(int), random_state=0)

    # print ("X = %s" %numpy_array[0:3:1,2:16:1])
    # print ("y = %s" %numpy_array[0:3:1,17])



############################### data from wilab experiment
# header description
# 0 TIME
# 1 BUSY_TIME
# 2 tx_activity
# 3 num_tx
# 4 num_tx_success
elif data_source == "wilab":
    df = pd.read_json('wilab_measure.json')

    # print(df)
    # put the original column names in a python list
    # original_headers = list(df.columns.values)
    # remove the non-numeric columns
    # df = df._get_numeric_data()
    # print(df)
    # # put the numeric column names in a python list
    # numeric_headers = list(df.columns.values)
    # print(numeric_headers)
    # # create a numpy array with the numeric values for input into scikit-learn
    numpy_array = df.as_matrix()

    # now numpy_array follows this template:
    # [[[[1495465720.0857723, 15, 7, 116, 115]]                     ----->   192.168.0.1
    #   [[1495465720.0218935, 12592, 16, 73, 73]]                   ----->   192.168.0.3
    #   [[1495465720.004212, 11750663, 4085872, 2047131, 2163431]]] ----->   192.168.0.5

    # print (numpy_array)
    # set printing options to print all data rather than a selection
    np.set_printoptions(threshold=sys.maxint)
    # print ("numpy_array [:,0] = %s" %(numpy_array[:, 0]))

    dims = list(numpy_array.shape)
    num_readings = dims[0] # number of readings for each node
    num_nodes = dims[1] # number of nodes
    # print ("the json file has dims %s " %dims)

    # print (numpy_array)
    # print ("########")
    # print (numpy_array[0][0][0])
    # print (numpy_array[0][1][0])
    # print (numpy_array[0][2][0])
    #
    # print (numpy_array[1][0][0])
    # print (numpy_array[1][1][0])
    # print (numpy_array[1][2][0])
    #
    # print (numpy_array[2][0][0])
    # print (numpy_array[2][1][0])
    # print (numpy_array[2][2][0])

    print ("before reshape X dimension %s " % list(numpy_array.shape))

    X = [0, 0, 0, 0, 0]
    # group data by node (group by column, which represents the node)
    for jj in range(num_nodes):
        for ii in range(num_readings):
            row = numpy_array[ii][jj][0]
            X = np.vstack((X, row))
    # remove first line composed by zeros
    X = X[1:, :]
    # remove the first column, which is the timestamp (it is not a feature)
    X = X[:, 1:]

    print("#################")
    # first node
    print(X[0:60, :])

    print("#################")
    # second node
    print(X[60:120, :])

    print("#################")
    # third node
    print(X[120:180, :])

    y = np.array(180 * [1])
    y[1] = 2
    y[2] = 2
    y[3] = 3

    print (y)
    print ("types")
    type(X)
    type(y)

    class_names = ['flow in the middle', 'hidden nodes', 'no-interf']
    print (class_names)
    # Split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

else:
    print("please, choose in the code a valid data_source ")


# print ("y dimension %s " %list(y.shape))
# print ("X  %s " %X[1:3,:])
# print ("y  %s " %y[1:3])

# print ("X %s = %s" %(X.shape,X))
# print ("y %s = %s" %(y.shape,y))



chosen_classifiers = ["SVM", "Bagged KNeighbors", "Bagged Trees", "Tree"]
classifier_name = "Bagged Trees"

if (classifier_name == chosen_classifiers[0] ):
    # Run classifier, using a model that is too regularized (C too low) to see
    # the impact on the results
    classifier = svm.SVC(kernel='linear', C=0.01)
    print ("using SVM ... ")
elif (classifier_name == chosen_classifiers[1] ):
    classifier = BaggingClassifier(KNeighborsClassifier(), max_samples=0.5, max_features=0.5)
    print ("using Bagged kNeigh ... ")
elif (classifier_name == chosen_classifiers[2] ):
    classifier = BaggingClassifier(tree.DecisionTreeClassifier(), max_samples=0.5, max_features=0.5)
    print ("using Bagged Trees ... ")
elif (classifier_name == chosen_classifiers[3] ):
    classifier = tree.DecisionTreeClassifier()
    print ("using  Trees ... ")
    trained_classifier = classifier.fit(X_train, y_train)
    y_pred = trained_classifier.predict(X_test)
    print ("size X_train %s, size y_train %s size X_test %s" % (X_train.shape, y_train.shape, X_test.shape))

    # # print tree
    # with open("file.dot", 'w') as f:
    #     f = tree.export_graphviz(trained_classifier, out_file=f)
    #
    # print("please, run the following command (Graphviz has to be instsalled)")
    # print("dot -Tpdf file.dot -o file.pdf")


    # import os
    # os.unlink('baggedTree.dot')
    # import pydotplus
    #
    # dot_data = tree.export_graphviz(trained_classifier, out_file=None)
    # graph = pydotplus.graph_from_dot_data(dot_data)
    # graph.write_pdf("baggedTree.pdf")

else:
    print ("The chosen classifier is not configured!")


trained_classifier = classifier.fit(X_train, y_train)
print ("score obtained %f " %trained_classifier.score(X_train, y_train))



# now you can save it to a file
joblib.dump(trained_classifier, 'trained-interference-classifier.pkl')

# and later you can load it
trained_classifier = joblib.load('trained-interference-classifier.pkl')

y_pred = trained_classifier.predict(X_test)

print ("size X_train %s, size y_train %s size X_test %s" % (X_train.shape, y_train.shape, X_test.shape))

# Compute confusion matrix
cnf_matrix = confusion_matrix(y_test, y_pred)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, title='Confusion matrix, without normalization')
plt.savefig('confusion-matrix.pdf', format='pdf')
plt.draw()

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True, title='Normalized confusion matrix')
plt.savefig('normalized-confusion-matrix.pdf', format='pdf')

plt.draw()


####print ("X_test")


# # X_test = X_test[0:30,:]
# # X_test = np.array([[1.49, 4643, 4379, 2097, 2099]])
# # X_test.reshape((30,5))
#
# print (" X_test type %s, size X_test %s" % (type(X_test), X_test.shape))
# print(X_test)
#
X_test = np.array([[0.1,   3000,   3000, 2]]) # expected estimated class  2
# X_test = np.array([[4643.00000,   4,   5, 6]]) # 1
# X_test = np.array([[0.4,   1000,   1000, 2500]]) # 3
# X_test = np.array([[4643.00000,   118.000000,   0.00000000, 0.00000000e+00]])
#
# print (" X_test type %s, size X_test %s" % (type(X_test), X_test.shape))
# print(X_test)

y_pred = trained_classifier.predict(X_test)
print("predicted class %s" %y_pred)


plt.show()