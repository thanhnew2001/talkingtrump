import os

def delete_files_in_named_directories(root_directory, target_dir_names):
    """
    Delete all files in directories with specific names.

    :param root_directory: The root directory to start the search from.
    :param target_dir_names: List of directory names whose files are to be deleted.
    """
    for root, dirs, files in os.walk(root_directory):
        # Check if the current directory's name is in the list of target directory names
        if os.path.basename(root) in target_dir_names:
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}    ")
    files = os.listdir(root_directory)
    for file in files:
            if not os.path.isdir(file):
                if file.startswith("input_"):
                    file_path = os.path.join(root_directory, file)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
    

if __name__ == "__main__":
    target_dir_names = ['mp3', 'mp4','wavs']

    delete_files_in_named_directories('.', target_dir_names)
