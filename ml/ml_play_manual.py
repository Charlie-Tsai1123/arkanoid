import pygame
import pickle
import os
from datetime import datetime

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.ball_served = False
        self.prev_ball_position = None  # store previous ball position
        self.game_status = None  # store the status of the game
        self.movement = "NONE"  # store movement of the platform
        self.data = []  # store game data
        self.prev_bricks = []  # store previous bricks for detecting disappeared bricks

    def update(self, scene_info, keyboard=None, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        ball_x, ball_y = scene_info["ball"]
        platform_x = scene_info['platform'][0]
        current_bricks = scene_info["bricks"]  # The current brick state

        # Make the caller invoke `reset()` for the next round.
        if keyboard is None:
            keyboard = []
        if (scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS"):
            self.game_status = scene_info["status"]
            return "RESET"

        # Game Serve ball
        if not scene_info["ball_served"]:
            self.prev_ball_position = (ball_x, ball_y)
            self.prev_bricks = current_bricks  # Initialize brick state
            return "SERVE_TO_LEFT"
        
        # Calculate ball movement
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

        # Detect collision with brick
        collision_with_brick = 0  # Flag for brick collision (0: No collision, 1: Collision)
        disappeared_brick = (-1, -1)  # Default value if no brick disappears

        # Detect disappeared bricks
        if self.prev_bricks:
            for brick in self.prev_bricks:
                if brick not in current_bricks:  # Brick was in previous state but not in current state → hit
                    disappeared_brick = brick
                    collision_with_brick = 1  # Collision with a brick
                    break  # Only record the first disappeared brick

        # Update previous bricks for next frame
        self.prev_bricks = current_bricks

        # Platform control logic
        if pygame.K_LEFT in keyboard or pygame.K_a in keyboard:
            command = "MOVE_LEFT"
        elif pygame.K_RIGHT in keyboard or pygame.K_d in keyboard:
            command = "MOVE_RIGHT"
        else:
            command = "NONE"

        # Change command value to numeric
        if command == "MOVE_RIGHT":
            command_value = 1
        elif command == "MOVE_LEFT":
            command_value = -1
        else:
            command_value = 0

        # Store data with collision_with_brick
        data_entry = {
            "command": command_value,
            "ball_platform_distance": ball_x - platform_x,
            "ball_ground_y": 400 - ball_y,
            "ball_position": scene_info["ball"],
            "platform_x": platform_x,
            "ball_direction": ball_direction,
            "ball_dx": dx,
            "ball_dy": dy,
            #"collision_with_brick": collision_with_brick  # Numeric representation of brick collision
        }
        self.data.append(data_entry)

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.prev_ball_position = None
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
