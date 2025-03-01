"""
The template of the main script of the machine learning process
"""

class MLPlay:
    def __init__(self,ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.prev_ball_position = None # store previous ball position
        self.movement = "NONE" # store movement of the platform
        print(ai_name)

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """

        ball_x, ball_y = scene_info["ball"]
        platform_x = scene_info['platform'][0]

        # Make the caller to invoke `reset()` for the next round.
        # Game End
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        
        # Game Serve ball
        if not scene_info["ball_served"]:
            self.prev_ball_position = (ball_x, ball_y)
            return "SERVE_TO_LEFT"
        
        # Game Start
        pre_ball_x, pre_ball_y = self.prev_ball_position
        self.prev_ball_position = (ball_x, ball_y)
        dx = ball_x - pre_ball_x
        dy = ball_y - pre_ball_y
        slope = dy/dx if dy != 0 else 0

        
        predict_platform_x = ball_x + (400 - ball_y)*slope
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


        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
