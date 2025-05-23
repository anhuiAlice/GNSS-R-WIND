import argparse
from sklearn import preprocessing
import numpy
import numpy as np
import tensorflow as tf
import os
import pandas as pd
from tensorflow.keras import layers
import tensorflow_addons as tfa
# 1.652252268388138
# tf.Tensor(1.2460383745057, shape=(), dtype=float64)
# 19.302750424876145
min_max_scaler = preprocessing.MinMaxScaler()

parser = argparse.ArgumentParser(description="DF")
parser.add_argument('--batch_size', type=int, default=128, help='batch size for training')
parser.add_argument('--learning_rate', type=float, default=0.001, help='learning rate for training')
parser.add_argument('--weight_decay', type=float, default=0.001, help='weight decay for training')
parser.add_argument('--epochs', type=int, default=50, help='number of epochs for training')
parser.add_argument('--patience', type=int, default=6, help='early-stopping patience')
parser.add_argument('--num_workers', type=int, default=8, help='number of workers for the train loader')
parser.add_argument('--patch_size', type=int, default=1, help='DF patch size')
parser.add_argument('--num_patches', type=int, default=187, help='DF patch number')
parser.add_argument('--projection_dim', type=int, default=187, help='linear projection dimension')
parser.add_argument('--num_heads', type=int, default=11, help='number of heads')
parser.add_argument('--transformer_layers', type=int, default=2, help='number of transformer layers')
parser.add_argument('--mlp_head_units_0', type=int, default=512, help='mlp head 0 units')
parser.add_argument('--mlp_head_units_1', type=int, default=128, help='mlp head 1 units')
parser.add_argument('--mlp_head_units_2', type=int, default=32, help='mlp head 2 units')
parser.add_argument('--mlp_head_units_3', type=int, default=8, help='mlp head 3 units')
args = parser.parse_args()

# set random seed
np.random.seed(0)
tf.random.set_seed(0)

print("开始读取数据DDM和Label数据")

#归一化ddm矩阵
def normalize_to_0_255(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    normalized_arr = (arr - min_val) * (255 / (max_val - min_val))
    return normalized_arr.astype(np.uint8)

def ddm_data(path):
    df = pd.read_csv(path, encoding='utf-8')
    df = df[(df['les'] >= 0) & (df['brcs'] >= 0)]

    #获取dmm的四个分量的df地址文件
    df_brcs = df['path-brcs']
    df_eff_brcs = df['path-eff-brcs']
    df_raw_counts = df['path-raw-counts']
    # df_power_analog = df['path-power-analog']

    #将df地址文件转换为地址列表
    path_brcs = df_brcs.values.tolist()
    path_eff_brcs = df_eff_brcs.values.tolist()
    path_raw_counts = df_raw_counts.values.tolist()
    # path_power_analog = df_power_analog.values.tolist()

    #获取图片的数量
    d = len(path_brcs)
    #建立新的列表存放ddm数据
    data = numpy.empty((d, 17, 11, 3))
    i = 0
    while d > 0:
        brcs_data = np.loadtxt(path_brcs[i])
        eff_brcs_data = np.loadtxt(path_eff_brcs[i])
        raw_counts_data = np.loadtxt(path_raw_counts[i])
        # power_analog_data = np.loadtxt(path_power_analog[i])

        # brcs_data = normalize_to_0_255(brcs_data)
        # eff_brcs_data = normalize_to_0_255(eff_brcs_data)
        # raw_counts_data = normalize_to_0_255(raw_counts_data)

        # 合并为一个 (17, 11, 4) 的数组
        ddm = np.stack((brcs_data, eff_brcs_data, raw_counts_data), axis=-1)

        data[i] = ddm  # 将图像的矩阵形式保存到data中
        d = d - 1
        i = i + 1

    return data

x_data = ddm_data(path="D:/研究生代码/训练数据/8-4/2019-5-7-train-high.csv")
# x_test = ddm_data(path="D:/研究生代码/训练数据/3-23/2019-5-7-test-low.csv")

def load_data(path):

    df = pd.read_csv(path, encoding='utf-8')
    df = df[(df['les'] >= 0) & (df['brcs'] >= 0)]
    # 读取CSV文件，包含图片地址和一维变量
    # 提取需要归一化的列
    columns_to_normalize = ['lon', 'lat', 'les', 'brcs', 'SNR', 'noise_floor', 'sp_angle', 'RCG', 'PRN','sp_az_body',
                            'sp_az_orbit']

    # 对每一列进行归一化处理
    for column in columns_to_normalize:
        max_value = df[column].max()
        min_value = df[column].min()
        df[column] = (df[column] - min_value) / (max_value - min_value)

    y_data = np.array(df['fengsu'])
    X = df[['lon', 'lat', 'les', 'brcs', 'SNR', 'noise_floor','sp_angle', 'RCG','PRN','sp_az_body','sp_az_orbit']]
    # min_max_scaler = preprocessing.MinMaxScaler()
    # scaledX = min_max_scaler.fit_transform(X)
    epi_data = X

    return (epi_data, y_data, df)

x2_data,y_data, df = load_data(path="D:/研究生代码/训练数据/8-4/2019-5-7-train-high.csv")
# x2_test, y_test, df_test = load_data(path="D:/研究生代码/训练数据/3-23/2019-5-7-test-low.csv")

from sklearn.model_selection import train_test_split

# 划分数据集
(seq_train, seq_val, y_train, y_val, epi_train, epi_val) = train_test_split(x_data, y_data, x2_data, test_size=0.3,random_state=42)

# load dataset
x_train = seq_train
x2_train = epi_train
y_train = y_train # training label
print(f"x_train shape: {x_train.shape} - y_train shape: {y_train.shape}")

x_valid =  seq_val# validation DDMs
y_valid =  y_val# validation label
x2_valid = epi_val
print(f"x_valid shape: {x_valid.shape} - y_valid shape: {y_valid.shape}")

# model save directory
weights_dir = 'logs_DF_High/weights/'
if not os.path.exists(weights_dir):
    os.makedirs(weights_dir)

board_dir = 'logs_DF_High/events/'
if not os.path.exists(board_dir):
    os.makedirs(board_dir)

# tr block setup
transformer_units = [args.projection_dim * 3, args.projection_dim]
mlp_head_units = [args.mlp_head_units_0, args.mlp_head_units_1]
initializer = tf.keras.initializers.GlorotUniform()


# mlp sublayer
def mlp(x, hidden_units, dropout_rate):
    for units in hidden_units:
        x = layers.Dense(units, activation=tf.nn.gelu, kernel_initializer=initializer)(x)
        x = layers.Dropout(dropout_rate)(x)
    return x


# pixel-wise tokenization
class Patches(layers.Layer):
    def __init__(self, patch_size, **kwargs):
        super(Patches, self).__init__()
        self.patch_size = patch_size

    def call(self, images, **kwargs):
        batch_size = tf.shape(images)[0]
        patches = tf.image.extract_patches(
            images=images,
            sizes=[1, self.patch_size, self.patch_size, 1],
            strides=[1, self.patch_size, self.patch_size, 1],
            rates=[1, 1, 1, 1],
            padding="VALID",
        )
        patch_dims = patches.shape[-1]
        patches = tf.reshape(patches, [batch_size, -1, patch_dims])
        return patches

    def get_config(self):
        config = super().get_config()
        config.update({
            "patch_size": self.patch_size,
        })
        return config

# DDA token
class DDAToken(layers.Layer):
    def __init__(self, patch_size, **kwargs):
        super(DDAToken, self).__init__()
        dda_init = tf.zeros_initializer()
        self.hidden_size = patch_size * patch_size * 3
        self.dda = tf.Variable(
            name="dda",
            initial_value=dda_init(shape=(1, 1, self.hidden_size), dtype="float32"),
            trainable=True,
        )

    def call(self, inputs, **kwargs):
        batch_size = tf.shape(inputs)[0]
        dda_broadcasted = tf.cast(
            tf.broadcast_to(self.dda, [batch_size, 1, self.hidden_size]),
            dtype=inputs.dtype,
        )
        concat = tf.concat([dda_broadcasted, inputs], 1)
        return concat

    def get_config(self):
        config = super().get_config()
        config.update({
            "hidden_size": self.hidden_size,
        })
        return config


class PatchEncoder(layers.Layer):
    def __init__(self, num_patches, projection_dim, **kwargs):
        super(PatchEncoder, self).__init__()
        self.num_patches = num_patches + 1
        self.projection = layers.Dense(units=projection_dim, kernel_initializer=initializer)
        self.position_embedding = layers.Embedding(
            input_dim=num_patches, output_dim=projection_dim
        )

    def call(self, patch, **kwargs):
        positions = tf.range(start=0, limit=self.num_patches, delta=1)
        encoded = self.projection(patch) + self.position_embedding(positions)
        return encoded

    def get_config(self):
        config = super().get_config()
        config.update({
            "num_patches": self.num_patches,
            "projection_dim": self.projection,
        })
        return config


# msa sublayer
@tf.keras.utils.register_keras_serializable()
class MultiHeadSelfAttention(layers.Layer):
    def __init__(self, *args, num_heads, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_heads = num_heads

    def build(self, input_shape):
        hidden_size = input_shape[-1]
        num_heads = self.num_heads
        if hidden_size % num_heads != 0:
            raise ValueError(
                f"embedded dimension not divisible by number of heads"
            )
        self.hidden_size = hidden_size
        self.projection_dim = hidden_size // num_heads
        self.query_dense = tf.keras.layers.Dense(hidden_size, name="query")
        self.key_dense = tf.keras.layers.Dense(hidden_size, name="key")
        self.value_dense = tf.keras.layers.Dense(hidden_size, name="value")
        self.combine_heads = tf.keras.layers.Dense(hidden_size, name="out")

    def attention(self, query, key, value):
        score = tf.matmul(query, key, transpose_b=True)
        dim_key = tf.cast(tf.shape(key)[-1], score.dtype)
        scaled_score = score / tf.math.sqrt(dim_key)
        weights = tf.nn.softmax(scaled_score, axis=-1)
        output = tf.matmul(weights, value)
        return output, weights

    def separate_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.projection_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, inputs):
        batch_size = tf.shape(inputs)[0]
        query = self.query_dense(inputs)
        key = self.key_dense(inputs)
        value = self.value_dense(inputs)
        query = self.separate_heads(query, batch_size)
        key = self.separate_heads(key, batch_size)
        value = self.separate_heads(value, batch_size)

        attention, weights = self.attention(query, key, value)
        attention = tf.transpose(attention, perm=[0, 2, 1, 3])
        concat_attention = tf.reshape(attention, (batch_size, -1, self.hidden_size))
        output = self.combine_heads(concat_attention)
        return output, weights

    def get_config(self):
        config = super().get_config()
        config.update({"num_heads": self.num_heads})
        return config

    @classmethod
    def from_config(dda, config):
        return dda(**config)

def ddm_former():
    inputs_patches = layers.Input(shape=(17, 11, 3))
    inputs_variable = layers.Input(shape=(11))
    # create patches
    patches = Patches(args.patch_size)(inputs_patches)
    dda = DDAToken(args.patch_size)(patches)
    # encode patches
    encoded_patches = PatchEncoder(args.num_patches, args.projection_dim)(dda)
    # create tr block
    for _ in range(args.transformer_layers):
        # LN
        x1 = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
        # msa
        attention_output, _ = MultiHeadSelfAttention(num_heads=args.num_heads)(x1)
        # skip connection
        x2 = layers.Add()([attention_output, encoded_patches])
        # LN
        x3 = layers.LayerNormalization(epsilon=1e-6)(x2)
        # mlp
        x3 = mlp(x3, hidden_units=transformer_units, dropout_rate=0.1)
        # skip connection
        encoded_patches = layers.Add()([x3, x2])

    out_repre = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
    out_repre = layers.Flatten()(out_repre)
    out_repre = layers.Dropout(0.5)(out_repre)
    # mlp
    out_repre = mlp(out_repre, hidden_units=mlp_head_units, dropout_rate=0.5)
    # print(out_repre.shape,inputs_variable.shape)
    # # ws
    concatted = tf.concat([out_repre, inputs_variable],1)

    # print(concatted.shape)
    # # our final FC layer head will have two dense layers, the final one
    # # being our regression head
    ws = layers.Dense(128, activation="tanh")(concatted)
    ws = layers.Dropout(0.5)(ws)
    ws = layers.Dense(64, activation="relu")(ws)
    ws = layers.Dropout(0.5)(ws)
    ws = layers.Dense(32, activation="relu")(ws)
    ws = layers.Dense(1, activation="linear")(ws)    # create model
    model = tf.keras.Model(inputs=[inputs_patches, inputs_variable], outputs=ws)
    return model


# x_test = tf.random.normal(shape=[1, 17, 11, 3])
# x2_test = tf.random.normal(shape=[1, 11])
df_model = ddm_former()
# print(df_model([x_test,x2_test]))
# #
# x_train = tf.random.normal(shape=[500, 17, 11, 3])
# x2_train = tf.random.normal(shape=[500, 11])
# y_train = tf.random.normal(shape=[500, 1])
#
# x_valid = tf.random.normal(shape=[100, 17, 11, 3])
# x2_valid = tf.random.normal(shape=[100, 11])
# y_valid = tf.random.normal(shape=[100, 1])
# print('---------Training----------')

optimizer = tfa.optimizers.AdamW(learning_rate=args.learning_rate,weight_decay=args.weight_decay)
df_model.compile(optimizer=optimizer,
                loss="mse",
                metrics=[tf.keras.metrics.MeanSquaredError(name='MSE')])
callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                            patience=args.patience)
model_ckt = tf.keras.callbacks.ModelCheckpoint(filepath=os.path.join(weights_dir, 'weights.h5'),
                            verbose=1,
                            save_best_only=True)
tfboard = tf.keras.callbacks.TensorBoard(log_dir=board_dir,
                        write_graph=True,
                        write_images=True)
df_model.fit([x_train, x2_train], y_train, batch_size=args.batch_size, epochs=args.epochs,
            callbacks=[model_ckt, tfboard, callback],
            validation_data=([x_valid, x2_valid], y_valid),
            shuffle=True, workers=args.num_workers)

df_model.save_weights('logs_DF_High/ckpt/weights.ckpt')
print('保存权重...')
#
# # 恢复权重
# network = ddm_former()
# network.compile(optimizer=optimizer,
#                 loss="mse",
#                 metrics=[tf.keras.metrics.MeanSquaredError(name='MSE')])
#
# network.load_weights('ckpt/weights.ckpt')
#
# print('读取权重，重新评估...')
#
# pred = network.predict([x_test,x2_test])
#
# df_test['M-Trans'] = pred
# df_test.to_csv("M-Transformer-100000.csv",index=False)
# print(pred)