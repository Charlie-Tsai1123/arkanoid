import pickle
import os
from datetime import datetime

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.prev_ball_position = None  # 儲存球的上一幀位置
        self.movement = "NONE"  # 儲存平台的移動指令
        self.data = []  # 儲存遊戲數據
        self.game_status = None  # 儲存遊戲狀態
        self.prev_bricks = []  # 儲存上一幀的磚塊狀態
        self.knn_model = self.load_knn_model("knn_model.pickle")  # 加載訓練好的 KNN 模型
        print(ai_name)

    def load_knn_model(self, model_path):
        """
        加載訓練好的 KNN 模型
        """
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                return pickle.load(f)
        else:
            raise FileNotFoundError(f"模型檔案 {model_path} 不存在")

    def update(self, scene_info, *args, **kwargs):
        """
        根據當前的遊戲狀態生成指令
        """
        ball_x, ball_y = scene_info["ball"]
        platform_x = scene_info['platform'][0]
        current_bricks = scene_info["bricks"]  # 當前的磚塊列表

        # 遊戲結束
        if scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS":
            self.game_status = scene_info["status"]
            return "RESET"

        # 發球
        if not scene_info["ball_served"]:
            self.prev_ball_position = (ball_x, ball_y)
            self.prev_bricks = current_bricks  # 初始化磚塊狀態
            return "SERVE_TO_LEFT"

        # 計算球的位移和方向
        pre_ball_x, pre_ball_y = self.prev_ball_position
        self.prev_ball_position = (ball_x, ball_y)
        dx = ball_x - pre_ball_x
        dy = ball_y - pre_ball_y
        if dx > 0 and dy > 0:
            ball_direction = 1  # Right-Up
        elif dx > 0 and dy < 0:
            ball_direction = 0  # Right-Down
        elif dx < 0 and dy > 0:
            ball_direction = 3  # Left-Up
        elif dx < 0 and dy < 0:
            ball_direction = 2  # Left-Down
        else:
            ball_direction = 4  # No movement

        # 檢測消失的磚塊
        collision_with_brick = 0  # 預設為 0（未碰撞）
        if self.prev_bricks:
            for brick in self.prev_bricks:
                if brick not in current_bricks:  # 這個磚塊在上一幀有，這一幀沒有 → 被擊中消失
                    collision_with_brick = 1
                    break  # 只記錄一次碰撞

        # 更新上一幀的磚塊列表
        self.prev_bricks = current_bricks

        # 提取特徵
        features = [
            ball_x - platform_x,  # 球與平台的距離
            400 - ball_y,        # 球與地面的距離
            ball_x,              # 球的 x 位置
            ball_y,              # 球的 y 位置
            platform_x,          # 平台的位置
            ball_direction,      # 球的方向
            dx,                  # 球的水平位移
            dy,                  # 球的垂直位移
            collision_with_brick  # 碰撞標誌
        ]

        # 使用 KNN 模型預測平台移動指令
        command_value = self.knn_model.predict([features])[0]

        # 將預測的指令轉換為遊戲指令
        if command_value == 1:
            command = "MOVE_RIGHT"
        elif command_value == -1:
            command = "MOVE_LEFT"
        else:
            command = "NONE"

        # 記錄數據
        data_entry = {
            "command": command_value,
            "ball_platform_distance": ball_x - platform_x,
            "ball_ground_y": 400 - ball_y,
            "ball_position": scene_info["ball"],
            "platform_x": platform_x,
            "ball_direction": ball_direction,
            "ball_dx": dx,
            "ball_dy": dy,
            "collision_with_brick": collision_with_brick  # 碰撞標誌
        }
        self.data.append(data_entry)

        return command

    def reset(self):
        """
        重置狀態
        """
        self.ball_served = False
        self.prev_ball_position = None
        self.prev_bricks = []  # 重置磚塊資訊

        # 確保 log 目錄存在
        filepath = "log/"
        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        # 只有在遊戲成功時保存數據
        if self.game_status == "GAME_PASS":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_data_{timestamp}.pickle"

            # 將數據保存到 pickle 檔案
            with open(os.path.join(filepath, filename), "wb") as f:
                pickle.dump(self.data, f)

            print(f"遊戲數據保存到 {filepath}{filename}")
        else:
            print("遊戲未成功，數據未保存。")

        # 清除數據，準備下一局遊戲
        self.data = []