import csv
import os
import numpy as np
import pandas as pd
from keras_preprocessing.sequence import pad_sequences
from keras import backend as K
from Functions import TextCNN, load_report
from numba import cuda

max_len = 6000
max_cnt = 300
embed_size = 256
num_filters = 64
kernel_size = [2, 4, 6, 8, 10, 12, 14]
conv_action = 'relu'
mask_zero = False
TRAIN = True


def predict(report_path):
    # 读取API
    weight_path = 'NN/'
    map_path = 'map.csv'
    with open(map_path, 'r') as f:
        reader = csv.reader(f)
        api2index = {rows[0]: rows[1] for rows in reader}

    api = load_report(report_path)
    X_test = pd.DataFrame({'api':api})
    X_test['api_idx'] = X_test['api'].map(api2index)
    X_test.fillna(0, inplace=True)
    test_seq = pad_sequences([X_test['api_idx'].values.tolist()], maxlen=6000)

    # 预测
    y = 0
    model = TextCNN(max_len, max_cnt, embed_size, num_filters, kernel_size, conv_action, mask_zero)
    for weight in os.listdir(weight_path):
        weight = os.path.join(weight_path, weight)
        model.load_weights(weight)
        y += model.predict(test_seq)
        K.clear_session()

    cuda.select_device(0)
    cuda.close()
    y /= 5
    index = np.argmax(y).astype(int)
    type_dic = {0: '正常', 1: '勒索病毒', 2: '挖矿程序', 3: 'DDoS木马',
                4: '蠕虫病毒', 5: '感染型病毒', 6: '后门程序', 7: '木马程序'}

    result = type_dic[index]
    return result
