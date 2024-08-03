import numpy as np
from sklearn.ensemble import BaggingRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd
from sklearn import preprocessing
# 假设你的数据集包含X和y，其中X是输入特征，y是目标变量（二分类标签）

#读取数据集
train_data = pd.read_csv("D:/研究生代码/训练数据/3-23/2019-05-07-train.csv",encoding='gbk')
test_data = pd.read_csv("D:/研究生代码/训练数据/3-23/2",encoding='gbk')

y_train = np.array(train_data["fengsu"])

x_trian = train_data[['lon', 'lat', 'les', 'brcs', 'noise_floor', 'SNR', 'sp_angle', 'RCG','PRN','sp_az_body','sp_az_orbit']]
min_max_scaler = preprocessing.MinMaxScaler()
scaledX = min_max_scaler.fit_transform(x_trian)
x_train = scaledX

y_test = np.array(test_data["fengsu"])

x_test = test_data[['lon', 'lat', 'les', 'brcs' , 'noise_floor', 'SNR', 'sp_angle', 'RCG','PRN','sp_az_body','sp_az_orbit']]
min_max_scaler = preprocessing.MinMaxScaler()
scaledX = min_max_scaler.fit_transform(x_test)
x_test = scaledX

# 创建袋装决策树模型
model = BaggingRegressor(n_estimators=5)

# 在训练集上拟合模型
model.fit(x_train, y_train)

# 在测试集上进行预测
y_pred = model.predict(x_test)
df = pd.read_csv("D:/研究生代码/训练数据/3-23/2019-5-7-test-3-22.csv")
df['bt-predict'] = y_pred
df.to_csv('D:/研究生代码/预测结果/3-23/2019-5-7-Bagged-Tree.csv', index=False)

# 计算均方误差
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)