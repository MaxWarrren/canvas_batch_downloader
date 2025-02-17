import os
import zipfile
import shutil

def extract_zip_files(zip_dir, extract_dir, delete_after_extraction=False):
    """
    Extracts all ZIP files from the specified directory to the extraction directory,
    placing each student's files into a separate folder named with their student_name.

    :param zip_dir: Path to the directory containing ZIP files.
    :param extract_dir: Path to the directory where contents will be extracted.
    :param delete_after_extraction: If True, delete ZIP files after extraction.
    """
    # Ensure the extraction directory exists
    os.makedirs(extract_dir, exist_ok=True)

    # Iterate over all files in the zip directory
    for filename in os.listdir(zip_dir):
        if filename.lower().endswith('.zip'):
            zip_path = os.path.join(zip_dir, filename)
            
            # Extract student_name from the filename
            student_name = filename[:-4]
            if not student_name:
                print(f"Warning: Could not extract student name from '{filename}'. Skipping this file.")
                continue

            # Define the folder where contents will be extracted
            student_extract_dir = os.path.join(extract_dir, student_name)
            
            # Ensure the student's extraction directory exists
            os.makedirs(student_extract_dir, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    print(f"Extracting '{filename}' to '{student_extract_dir}'...")
                    zip_ref.extractall(student_extract_dir)
                print(f"Successfully extracted: {filename} to {student_extract_dir}")
                
                if delete_after_extraction:
                    os.remove(zip_path)
                    print(f"Deleted ZIP file: {filename}")
                    
            except zipfile.BadZipFile:
                print(f"Error: '{filename}' is not a valid ZIP file or is corrupted.")
            except Exception as e:
                print(f"An unexpected error occurred while extracting '{filename}': {e}")
    
    remove_macosx_folders(extract_dir)

def remove_macosx_folders(unzipped_dir):
    """
    Removes __MACOSX folders from each student directory within the unzipped directory.

    :param unzipped_dir: Path to the unzipped directory containing student folders.
    """
    # Check if unzipped_dir exists
    if not os.path.isdir(unzipped_dir):
        print(f"The directory '{unzipped_dir}' does not exist. Skipping cleanup.")
        return

    # Iterate over each item in the unzipped directory
    for student_folder in os.listdir(unzipped_dir):
        student_path = os.path.join(unzipped_dir, student_folder)

        # Ensure we are dealing with a directory
        if os.path.isdir(student_path):
            macosx_path = os.path.join(student_path, '__MACOSX')
            if os.path.exists(macosx_path) and os.path.isdir(macosx_path):
                try:
                    shutil.rmtree(macosx_path)
                    print(f"Removed '__MACOSX' from '{student_folder}'.")
                except Exception as e:
                    print(f"Failed to remove '__MACOSX' from '{student_folder}': {e}")
            else:
                print(f"No '__MACOSX' folder found in '{student_folder}'.")
        else:
            print(f"Skipping non-directory item: '{student_folder}'.")
            
if __name__ == "__main__":
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths to the assignments/zip and assignments/unzipped folders
    assignments_dir = os.path.join(current_dir, 'ZombieOutbreakAssignments')
    zip_folder = os.path.join(assignments_dir, 'downloaded')
    unzipped_folder = os.path.join(assignments_dir, 'extracted')
    
    # Optional: If you want to clear the unzipped folder before extraction
    # Be cautious with this! It deletes all contents in the unzipped folder.
    # shutil.rmtree(unzipped_folder)
    # os.makedirs(unzipped_folder, exist_ok=True)
    
    # Extract ZIP files
    extract_zip_files(zip_folder, unzipped_folder, delete_after_extraction=False)