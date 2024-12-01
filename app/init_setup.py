import os

def create_project_structure():
    # Define the base directory
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Define directories to create
    directories = [
        os.path.join(base_dir, 'app', 'static'),
        os.path.join(base_dir, 'app', 'static', 'js'),
        os.path.join(base_dir, 'app', 'static', 'css'),
        os.path.join(base_dir, 'app', 'model'),
        os.path.join(base_dir, 'templates'),
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    create_project_structure() 