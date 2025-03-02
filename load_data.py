import pickle
import os

def load_game_data():
    filepath = "log/"
    
    # List all pickle files in the log directory
    pickle_files = [f for f in os.listdir(filepath) if f.endswith('.pickle')]
    
    # If there are pickle files, prompt the user to select one
    if pickle_files:
        print("Available pickle files:")
        
        # List all the available pickle files with index
        for idx, filename in enumerate(pickle_files):
            print(f"{idx + 1}. {filename}")
        
        # Prompt the user to choose a file by index
        try:
            choice = int(input("Enter the number of the pickle file to load: ")) - 1
            if choice < 0 or choice >= len(pickle_files):
                print("Invalid choice, exiting.")
                return None
            
            selected_file = pickle_files[choice]
            with open(os.path.join(filepath, selected_file), "rb") as f:
                game_data = pickle.load(f)
            
            print(f"Loaded game data from {selected_file}")
            
            # Print game data with each entry on a new line
            for entry in game_data:
                print(entry)  # Each entry will be printed on a new line
            
            return game_data
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return None
        
    else:
        print("No pickle files found.")
        return None

# Example usage:
game_data = load_game_data()

# You can now inspect the loaded data with each entry printed on a new line.
