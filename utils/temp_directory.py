import os
import tempfile

class TempDirManager:
    def __init__(self):
        self.temp_dir = None  # Temporary directory instance
    
    def create_temp_directory(self):
        if self.temp_dir is None:
            self.temp_dir = tempfile.TemporaryDirectory()  # Create the temp directory
        return self.temp_dir.name  # Return the path of the temp directory
    
    def create_subfolder(self, subfolder_name):
        temp_dir_path = self.create_temp_directory()  # Ensure the temp directory exists
        subfolder_path = os.path.join(temp_dir_path, subfolder_name)  # Create subfolder path
        
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)  # Create the subfolder if it doesn't exist
        
        return subfolder_path  # Return the path to the subfolder
    
    def close_temp_directory(self):
        if self.temp_dir is not None:
            self.temp_dir.cleanup()  # Clean up the temp directory
            self.temp_dir = None  # Reset the instance
    
    def get_temp_directory(self):
        return self.create_temp_directory()