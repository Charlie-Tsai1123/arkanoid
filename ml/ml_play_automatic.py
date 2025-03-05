import pickle
import os
from datetime import datetime

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.prev_ball_position = None  # store previous ball position
        self.movement = "NONE"  # store movement of the platform
        self.data = []  # store game data
        self.game_status = None  # store the status of the game
        self.prev_bricks = []  # store previous bricks for detecting disappeared bricks
        print(ai_name)

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        ball_x, ball_y = scene_info["ball"]
        platform_x = scene_info['platform'][0]
        current_bricks = scene_info["bricks"]  # 現在的磚塊列表

        # Game End
        if scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS":
            self.game_status = scene_info["status"]
            return "RESET"

        # Game Serve ball
        if not scene_info["ball_served"]:
            self.prev_ball_position = (ball_x, ball_y)
            self.prev_bricks = current_bricks  # 初始化磚塊狀態
            return "SERVE_TO_LEFT"

        # Calculate ball movement
        pre_ball_x, pre_ball_y = self.prev_ball_position
        self.prev_ball_position = (ball_x, ball_y)
        dx = ball_x - pre_ball_x
        dy = ball_y - pre_ball_y
        slope = dy / dx if dx != 0 else 0
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

        # Predict platform position
        predict_platform_x = ball_x + (400 - ball_y) * slope
        while predict_platform_x < 0 or predict_platform_x > 200:
            if predict_platform_x < 0:
                predict_platform_x = -predict_platform_x
            elif predict_platform_x > 200:
                predict_platform_x = 400 - predict_platform_x
        
        if platform_x + 20 < predict_platform_x - 2:
            command = "MOVE_RIGHT"
        elif platform_x + 20 > predict_platform_x + 2:
            command = "MOVE_LEFT"
        else:
            command = "NONE"

        # Detect disappeared bricks
        disappeared_brick = (-1, -1)  # 預設為 (-1, -1) 代表沒有磚塊消失
        collision_with_brick = 0  # Flag for brick collision (0: No collision, 1: Collision)
        if self.prev_bricks:
            for brick in self.prev_bricks:
                if brick not in current_bricks:  # 這個磚塊在上一幀有，這一幀沒有 → 被擊中消失
                    disappeared_brick = brick
                    collision_with_brick = 1  # Ball collided with a brick
                    break  # 只記錄第一個消失的磚塊，KNN 會比較好學習

        # Update previous bricks for next frame
        self.prev_bricks = current_bricks

        # change command_value
        if command == "MOVE_RIGHT":
            command_value = 1
        elif command == "MOVE_LEFT":
            command_value = -1
        else:
            command_value = 0

        # store data with numeric collision representation
        data_entry = {
            "command": command_value,
            "ball_platform_distance": ball_x - platform_x,
            "ball_ground_y": 400 - ball_y,
            "ball_position": scene_info["ball"],
            "platform_x": platform_x,
            "ball_direction": ball_direction,
            "ball_dx": dx,
            "ball_dy": dy,
            "collision_with_brick": collision_with_brick  # Numeric representation of collision
        }
        self.data.append(data_entry)

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.prev_ball_position = None
        self.prev_bricks = []  # 重置磚塊資訊

        # Ensure log directory exists
        filepath = "log/"
        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        # Save data only if the game was successful
        if self.game_status == "GAME_PASS":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_data_{timestamp}.pickle"

            # Store data to pickle file
            with open(os.path.join(filepath, filename), "wb") as f:
                pickle.dump(self.data, f)

            print(f"Game data saved to {filepath}{filename}")
        else:
            print("Game not successful, data not saved.")

        # Clear data for next game
        self.data = []
