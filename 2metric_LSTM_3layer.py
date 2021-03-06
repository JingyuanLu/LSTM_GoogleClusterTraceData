import numpy as np
import matplotlib
from time import time
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd 
import math
import keras
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.callbacks import TensorBoard, EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# def create_dataset(dataset, look_back=1):
# 	dataX, dataY = [], []
# 	for i in range(len(dataset)-look_back-1):
# 		a = dataset[i:(i+look_back), 0]
# 		dataX.append(a)
# 		dataY.append(dataset[i + look_back, 0])
# 	return np.array(dataX), np.array(dataY)

# tbCallBack = keras.callbacks.TensorBoard(log_dir='Graph/test.png', histogram_freq=0,  write_graph=True, write_images=True)
tensorboard = TensorBoard(log_dir="logs/{}".format(time()))
# df = read_csv('/home/nguyen/learnRNNs/international-airline-passengers.csv', usecols=[1], engine='python', skipfooter=3)

colnames = ['cpu_rate','mem_usage','disk_io_time','disk_space'] 
df = read_csv('data/Fuzzy_data_sampling_617685_metric_10min_datetime_origin.csv', header=None, index_col=False, names=colnames, usecols=[0,1], engine='python')

dataset = df.values

# normalize the dataset
length = len(dataset)
scaler = MinMaxScaler(feature_range=(0, 1))
RAM_nomal = scaler.fit_transform(dataset.T[1])
CPU_nomal = scaler.fit_transform(dataset.T[0])


data = []
for i in range(length-2):
	a=[]
	for j in range(2):
		a.append(CPU_nomal[i+j])
		a.append(RAM_nomal[i+j])
	data.append(a)
data = np.array(data)
print 'data'
print data
# split into train and test sets

# split into train and test sets
train_size = int(length * 0.67)
test_size = length - train_size
batch_size_array = [8,16,32,64,128]
trainX, trainY = data[0:train_size], CPU_nomal[2:train_size+2]
testX = data[train_size:length-2]
testY =  dataset.T[0][train_size+2:length]
print 'trainX'
print trainX
# reshape input to be [samples, time steps, features]

trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 1))
print 'trainX'
print trainX

# create and fit the LSTM network
for batch_size in batch_size_array: 
	print "batch_size= ", batch_size
	model = Sequential()
	model.add(LSTM(4, return_sequences=True, activation = 'relu',input_shape=(4, 1)))
	# model.add(LSTM(32, return_sequences=True, activation = 'relu'))
	# model.add(LSTM(16, return_sequences=True, activation = 'relu'))
	model.add(LSTM(2))
	model.add(Dense(1))
	model.compile(loss='mean_squared_error' ,optimizer='adam' , metrics=['mean_squared_error'])
	history = model.fit(trainX, trainY, epochs=2000, batch_size=batch_size, verbose=2,validation_split=0.1,
	 							callbacks=[EarlyStopping(monitor='loss', patience=20, verbose=1),tensorboard])
	# make predictions
	# list all data in history
	print(history.history.keys())
	# summarize history for accuracy
	# summarize history for loss
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'test'], loc='upper left')
	# plt.show()
	plt.savefig('results/6layers64-32-16/history_batchsize=%s.png'%(batch_size))
	testPredict = model.predict(testX)

	print testPredict
	# invert predictions
	testPredictInverse = scaler.inverse_transform(testPredict)
	print testPredictInverse
	# calculate root mean squared error

	testScoreRMSE = math.sqrt(mean_squared_error(testY, testPredictInverse[:,0]))
	testScoreMAE = mean_absolute_error(testY, testPredictInverse[:,0])
	print('Test Score: %.2f RMSE' % (testScoreRMSE))
	print('Test Score: %.2f MAE' % (testScoreMAE))
	testNotInverseDf = pd.DataFrame(np.array(testPredict))
	testNotInverseDf.to_csv('results/6layers64-32-16/testPredict_batchsize=%s.csv'%(batch_size), index=False, header=None)
	testDf = pd.DataFrame(np.array(testPredictInverse))
	testDf.to_csv('results/6layers64-32-16/testPredictInverse_batchsize=%s.csv'%(batch_size), index=False, header=None)
	errorScore=[]
	errorScore.append(testScoreRMSE)
	errorScore.append(testScoreMAE)
	errorDf = pd.DataFrame(np.array(errorScore))
	errorDf.to_csv('results/6layers64-32-16/error_batchsize=%s.csv'%(batch_size), index=False, header=None)