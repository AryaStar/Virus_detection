import json

from keras.layers import Dense, Input, LSTM, Lambda, Embedding, Dropout, Activation, GRU, Bidirectional
from keras.layers import Conv1D, Conv2D, MaxPooling2D, GlobalAveragePooling1D, GlobalMaxPooling1D, MaxPooling1D, Flatten
from keras.layers.merge import concatenate, Concatenate, Average, Dot, Maximum, Multiply, Subtract, average
from keras.models import Model
# from keras.optimizers import RMSprop, Adam
# from keras.layers.normalization import BatchNormalization
from keras.preprocessing.text import Tokenizer
from sklearn.decomposition import TruncatedSVD, NMF, LatentDirichletAllocation
from keras.layers import SpatialDropout1D
from keras.layers.wrappers import Bidirectional
from sklearn.model_selection import StratifiedKFold, KFold
# from keras.optimizers import SGD
import jsonpath


# 获取每个文件对应的api序列
def get_sequence(df, period_idx):
    seq_list = []
    for _id, begin in enumerate(period_idx[:-1]):
        seq_list.append(df.iloc[begin:period_idx[_id + 1]]['api_idx'].values)
    seq_list.append(df.iloc[period_idx[-1]:]['api_idx'].values)
    return seq_list


# CNN 神经网络模型
def TextCNN(max_len, max_cnt, embed_size, num_filters, kernel_size, conv_action, mask_zero):
    _input = Input(shape=(max_len,), dtype='int32')
    _embed = Embedding(max_cnt, embed_size, input_length=max_len, mask_zero=mask_zero)(_input)
    _embed = SpatialDropout1D(0.15)(_embed)
    warppers = []

    for _kernel_size in kernel_size:
        conv1d = Conv1D(filters=num_filters, kernel_size=_kernel_size, activation=conv_action)(_embed)
        warppers.append(GlobalMaxPooling1D()(conv1d))

    fc = concatenate(warppers)
    fc = Dropout(0.5)(fc)
    # fc = BatchNormalization()(fc)
    fc = Dense(256, activation='relu')(fc)
    fc = Dropout(0.25)(fc)
    # fc = BatchNormalization()(fc)
    preds = Dense(8, activation='softmax')(fc)

    model = Model(inputs=_input, outputs=preds)

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


# 获取report中的API
def load_report(report_path):
    report = open(report_path)
    report_read = json.load(report)
    api = jsonpath.jsonpath(report_read, '$...api')
    return api
