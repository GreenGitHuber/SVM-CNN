from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

from sklearn import svm

#X_train = preprocessing.scale(X_train)
#X_test = preprocessing.scale(X_test)

import tensorflow as tf
sess = tf.InteractiveSession()

import numpy as np

number_of_features = 128
batch_size = 55
batches_in_epoch = 1000
train_size = batches_in_epoch * batch_size
test_size = 10000

print("\n###################\nBegning the SVM experiment without using features from ConvNet\n###################")

train_features = np.zeros((train_size, 28*28), dtype=float)
train_labels = np.zeros(train_size, dtype=int)
converter = np.array([0,1,2,3,4,5,6,7,8,9])

for i in range(batches_in_epoch):
    train_batch = mnist.train.next_batch(batch_size)
    features_batch = train_batch[0]
    labels_batch = train_batch[1]
    for j in range(batch_size):
        for k in range(28*28):
            train_features[batch_size * i + j, k] = features_batch[j, k]
        train_labels[batch_size * i + j] = np.sum(np.multiply(converter, labels_batch[j, :]))

print("\ntrain_features")
print(train_features.shape)
print(type(train_features))
print(np.mean(train_features))
print(train_features)

print("\ntrain_labels")
print(train_labels.shape)
print(type(train_labels))
print(np.mean(train_labels))
print(train_labels)

test_features = np.zeros((test_size, 28*28), dtype=float)
test_labels = np.zeros(test_size, dtype=int)

test_features = mnist.test.images
for j in range(test_size):
    test_labels[j] = np.sum(np.multiply(converter, mnist.test.labels[j, :]))

print("\ntest_features")
print(test_features.shape)
print(type(test_features))
print(np.mean(test_features))
print(test_features)

print("\ntest_labels")
print(test_labels.shape)
print(type(test_labels))
print(np.mean(test_labels))
print(test_labels)

clf = svm.SVC()
clf.fit(train_features, train_labels)
accuracy = clf.score(test_features, test_labels)
print("\nACCURACY = ", accuracy)

print("\n###################\nBuilding the ConvNet to use as Feature Extractor\n###################")

x = tf.placeholder(tf.float32, shape=[None, 784])
y_ = tf.placeholder(tf.float32, shape=[None, 10])

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

x_image = tf.reshape(x, [-1,28,28,1])

W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])

W_fc1 = weight_variable([7*7*64, number_of_features])
b_fc1 = bias_variable([number_of_features])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

W_fc2 = weight_variable([number_of_features, 10])
b_fc2 = bias_variable([10])

y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

sess.run(tf.initialize_all_variables())
print()

for i in range(5*batches_in_epoch):
    batch = mnist.train.next_batch(batch_size)
    if i%batches_in_epoch == 0:
        train_accuracy = accuracy.eval(feed_dict={
            x: batch[0], y_: batch[1], keep_prob: 1.0})
        print("epoch %d, training accuracy %g" % (i / batches_in_epoch, train_accuracy))
    train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})

print("test accuracy %g"%accuracy.eval(feed_dict={
    x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))

print("\n###################\nBegning the SVM experiment using features from ConvNet\n###################")

train_features_cnn = np.zeros((train_size, number_of_features), dtype=float)
train_labels_cnn = np.zeros(train_size, dtype=int)
converter = np.array([0,1,2,3,4,5,6,7,8,9])

for i in range(batches_in_epoch):
    train_batch = mnist.train.next_batch(batch_size)
    features_batch = h_fc1.eval(feed_dict={x: train_batch[0]})
    labels_batch = train_batch[1]
    for j in range(batch_size):
        for k in range(number_of_features):
            train_features_cnn[batch_size * i + j, k] = features_batch[j, k]
        train_labels_cnn[batch_size * i + j] = np.sum(np.multiply(converter, labels_batch[j, :]))

print("\ntrain_features_cnn")
print(train_features_cnn.shape)
print(type(train_features_cnn))
print(train_features_cnn)

print("\ntrain_labels_cnn")
print(train_labels_cnn.shape)
print(type(train_labels_cnn))
print(train_labels_cnn)

test_features_cnn = h_fc1.eval(feed_dict={x: mnist.test.images})
test_labels_cnn = np.zeros(test_size, dtype=int)
for j in range(test_size):
    test_labels_cnn[j] = np.sum(np.multiply(converter, mnist.test.labels[j, :]))

print("\ntest_features_cnn")
print(test_features_cnn.shape)
print(type(test_features_cnn))
print(test_features_cnn)

print("\ntest_labels_cnn")
print(test_labels_cnn.shape)
print(type(test_labels_cnn))
print(test_labels_cnn)

clf = svm.SVC()
clf.fit(train_features_cnn, train_labels_cnn)
accuracy = clf.score(test_features_cnn, test_labels_cnn)
print("\nACCURACY = ", accuracy)

sess.close()

print("\n###################\nEnding the program\n###################\n")
