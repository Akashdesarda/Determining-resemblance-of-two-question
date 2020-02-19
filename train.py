import warnings
warnings.filterwarnings('ignore')

import re
import pandas as pd
import numpy as np
np.random.seed(30)

from timeit import default_timer as timer
from datetime import datetime
now = datetime.now().strftime("%d-%m-%Y")

from sklearn.model_selection import train_test_split

import tensorflow as tf
import tensorflow_hub as hub
from keras.utils import to_categorical

from utils import clean_text, generate_embedding, visualize
from SimilarityNet import build
from callbacks import callbacks

data = pd.read_csv('./data/train_que.csv')
data.dropna(inplace = True)
data['question1'], data['question2'] = data['question1'].apply(clean_text), data['question2'].apply(clean_text)

# Tf GPU memory graph
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            print('[INFO]... ',len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)
        
# Building network
model = build(generate_embedding)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print("[INFO]...Model Build Completed")
# Preparing training & validation data
from sklearn.model_selection import train_test_split
x1 = data['question1']
x2 = data['question2']
y = data['is_duplicate']
# Using the sklearn to split data in question1 and question2 train and test in the ration 80-20 %
x1_train, x1_test, x2_train, x2_test, y_train, y_test = train_test_split(x1, x2, y, test_size=0.2, random_state=42)

train_q1 = x1_train.tolist()
train_q1 = np.array(train_q1, dtype=object)[:, np.newaxis]
train_q2 = x2_train.tolist()
train_q2 = np.array(train_q2, dtype=object)[:, np.newaxis]

#train_labels = np.asarray(pd.get_dummies(y_train), dtype = np.int8)
train_labels = to_categorical(y_train, num_classes=2)

test_q1 = x1_test.tolist()
test_q1 = np.array(test_q1, dtype=object)[:, np.newaxis]
test_q2 = x2_test.tolist()
test_q2 = np.array(test_q2, dtype=object)[:, np.newaxis]

test_labels = to_categorical(y_test, num_classes=2)

# Callbacks list
callbacks_list = callbacks()

session = tf.Session()
K.set_session(session)
session.run(tf.global_variables_initializer())
session.run(tf.tables_initializer())
history = model.fit([train_q1, train_q2],
                    train_labels,
                    validation_data=([test_q1, test_q2], test_labels),
                    epochs=20,
                    batch_size=512)

visualize(history,
          save_dir=f'./assets/logs/history-{now}.png')