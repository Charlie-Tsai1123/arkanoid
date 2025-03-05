import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 1. 讀取所有 pickle 檔案
def load_pickle_data(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".pickle"):
            with open(os.path.join(directory, filename), "rb") as f:
                data.extend(pickle.load(f))
    return data

# 2. 數據預處理
def preprocess_data(data):
    X = []
    y = []
    for entry in data:
        # 特徵：球與平台的距離、球與地面的距離、球的位置、平台位置、球的方向、球的位移、碰撞標誌
        features = [
            entry["ball_platform_distance"],  # 球與平台的距離
            entry["ball_ground_y"],          # 球與地面的距離
            entry["ball_position"][0],       # 球的 x 位置
            entry["ball_position"][1],       # 球的 y 位置
            entry["platform_x"],             # 平台的位置
            entry["ball_direction"],         # 球的方向
            entry["ball_dx"],                # 球的水平位移
            entry["ball_dy"],                # 球的垂直位移
            entry["collision_with_brick"]    # 碰撞標誌
        ]
        X.append(features)
        # 標籤：平台移動指令
        y.append(entry["command"])
    return np.array(X), np.array(y)

# 3. 訓練 KNN 模型
def train_knn(X, y):
    # 將數據分為訓練集和測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 初始化 KNN 模型
    knn = KNeighborsClassifier(n_neighbors=5)

    # 訓練模型
    knn.fit(X_train, y_train)

    # 預測測試集
    y_pred = knn.predict(X_test)

    # 計算準確率
    accuracy = accuracy_score(y_test, y_pred)
    print(f"模型準確率: {accuracy * 100:.2f}%")

    return knn

# 主程式
if __name__ == "__main__":
    # 讀取數據
    data_directory = "log/"  # 存放 pickle 檔案的目錄
    data = load_pickle_data(data_directory)

    # 數據預處理
    X, y = preprocess_data(data)

    # 訓練 KNN 模型
    knn_model = train_knn(X, y)

    # 保存訓練好的模型
    with open("knn_model.pickle", "wb") as f:
        pickle.dump(knn_model, f)
    print("KNN 模型已保存為 knn_model.pickle")