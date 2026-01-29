from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QApplication
from PyQt6.QtCore import QThread, pyqtSignal
import os
import urllib.request
import shutil  # Import shutil for file operations
import zipfile
import threading
import tempfile

            
class GitHubDownloader:
    """
    @breif Class deals with downloading files from Github
    """
    
    repo_url = "https://raw.githubusercontent.com/GS-A1/DM-Program/main"
    downloaded_repo_path = ""
    zip_path = ""
    downloaded_repo = False  # Flag to indicate if the repo has been downloaded this session
    
    def git_download_file(self, file = "", outputPath = "", silent=False):
        """
        @brief Update the the conditions/spell effects file from github
        @param file The specific file to dowload. Must include the whole path from the repo root
        @param outputPath The local path to save the downloaded file. If blank, uses the same path as in the repo.
        @param silent If True, suppresses UI dialogs.
        @return False if there was an error, True otherwise.
        """
        file_path, separator, file_name = file.rpartition('/')   #find just the file name from the string
        
        #create the message box early so we can close it on an error
        messageBox = QProgressDialog("Downloading files...", None, 0, 100)
        messageBox.setWindowTitle("Downloading")
        messageBox.setAutoClose(False)
        messageBox.setRange(0, 100)
        messageBox.setValue(0)
        messageBox.setLabelText("Downloading files...")
        
        try:
            #Try to download the default file from the GitHub repository
            if file != "":
                #check to see if the folder exists, if not create it
                if file_path != "":
                    os.makedirs(file_path, exist_ok=True)
                
                repo_raw_url = f"{self.repo_url}/{file}"
                
                #if they have not specified an output path, use the file name
                if outputPath == "":
                    local_path = file
                else:
                    local_path = outputPath #otherwise use the specified output path
                
                os.makedirs(local_path, exist_ok=True) #create the output folder if it does not exist
                file_local_path = os.path.join(local_path, file_name) #full path to the local file

                # Download and save the file
                #urllib.request.urlretrieve(repo_raw_url, local_path)

                #create a message box to show download progress
                if not silent:
                    messageBox.show()
                #need to call process events to show the dialog. If this fails, add a small delay between calls
                QApplication.processEvents()
                QApplication.processEvents()
                
                #download with progress updates using a thread to keep everything alive
                download_error = [False]  # Use list to capture error in thread
                progress_data = {'percent': 0}  # Thread-safe progress tracking
            
                def download_with_progress():
                    """Download function to run in thread"""
                    try:
                        def download_progress(blocknum, blocksize, totalsize):
                            """Collect progress data (called from worker thread)"""
                            if totalsize > 0:
                                downloaded = blocknum * blocksize
                                percent = min(int((downloaded / totalsize) * 100), 100)
                                progress_data['percent'] = percent  # Store for main thread to read
                        
                        urllib.request.urlretrieve(repo_raw_url, file_local_path, reporthook=download_progress)
                    except Exception as e:
                        download_error[0] = str(e)
                
                # Run download in a separate thread
                download_thread = threading.Thread(target=download_with_progress, daemon=False)
                download_thread.start()
                
                # Keep UI responsive while download is happening
                while download_thread.is_alive():
                    # Update UI from main thread only
                    if not silent:
                        messageBox.setValue(progress_data['percent'])
                        messageBox.setLabelText(f"Downloading: {progress_data['percent']}%")
                    QApplication.processEvents()
                    download_thread.join(timeout=0.1)
                
                # Check if there was an error
                if download_error[0]:
                    raise Exception(download_error[0])
                
                #urllib.request.urlretrieve(repo_raw_url, local_path, reporthook=download_progress) #download the file and calla  callback when chunks are downloaded
                
                if not silent:
                    messageBox.close()
                    QApplication.processEvents()  # Process the close event
                
                return True
            else:
                QMessageBox.critical(None, "File Error", "File name cannot be blank")
                return False
        except Exception as e:
            if not silent:
                messageBox.close()  #close the message box on error
            QMessageBox.critical(None, "Download Error", f"Failed to download {file_name} file: {e}")
            return False
    
    def git_download_repo(self, silent=False):
        """
        @brief Download the latest version of the DM Program from GitHub.
        @param silent If True, suppresses confirmation dialogs.
        @return True if there was an error, False otherwise.
        """
        #check to see if we have already downloaded the repo this session. If so, exit early
        if self.downloaded_repo == True:
            return True
        
        #create the message box early so we can close it on an error
        messageBox = QProgressDialog("Downloading files...", None, 0, 100)
        messageBox.setWindowTitle("Downloading")
        messageBox.setAutoClose(False)
        messageBox.setRange(0, 100)
        messageBox.setValue(0)
        messageBox.setLabelText("Downloading files...")
        
        try:            
            # Create temp folder
            #temp_dir = os.path.join(os.path.dirname(__file__), "temp")
            temp_dir = os.path.join(tempfile.gettempdir(), "DM-Program") #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
            self.downloaded_repo_path = temp_dir    #store the path where the repo was downloaded
            
            # Check if temp folder already exists
            # are we in silent mode?            
            if not silent:
                if os.path.exists(temp_dir):
                    reply = QMessageBox.question(None, "GitHub Files Exists", 
                        "A recent copy of the GitHub files already exists. Do you want to overwrite them?", 
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        shutil.rmtree(temp_dir)
                        os.makedirs(temp_dir, exist_ok=True)
                    else:
                        return False
                else:
                    os.makedirs(temp_dir, exist_ok=True)
            else:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                else:
                    os.makedirs(temp_dir, exist_ok=True)
            
            if (not silent): 
                messageBox.show()
                messageBox.setLabelText("Downloading repository...")
                QApplication.processEvents()

            # Download repo zip with progress updates
            # raw.githubusercontent.com is for raw file blobs; use the GitHub archive URL for repository zips
            zip_url = "https://github.com/GS-A1/DM-Program/archive/refs/heads/main.zip"
            self.zip_path = os.path.join(temp_dir, "repo.zip")
            
            download_error = [False]  # Use list to capture error in thread
            progress_data = {'percent': 0}  # Thread-safe progress tracking
            
            def download_with_progress():
                """Download function to run in thread"""
                try:
                    def download_progress(blocknum, blocksize, totalsize):
                        """Collect progress data (called from worker thread)"""
                        if totalsize > 0:
                            downloaded = blocknum * blocksize
                            percent = min(int((downloaded / totalsize) * 100), 100)
                            progress_data['percent'] = percent  # Store for main thread to read
                    
                    urllib.request.urlretrieve(zip_url, self.zip_path, reporthook=download_progress)
                except Exception as e:
                    download_error[0] = str(e)
            
            # Run download in a separate thread
            download_thread = threading.Thread(target=download_with_progress, daemon=False)
            download_thread.start()
            
            # Keep UI responsive while download is happening
            while download_thread.is_alive():
                # Update UI from main thread only
                if not silent:
                    messageBox.setValue(progress_data['percent'])
                    messageBox.setLabelText(f"Downloading: {progress_data['percent']}%")
                QApplication.processEvents()
                download_thread.join(timeout=0.1)
            
            # Check if there was an error
            if download_error[0]:
                raise Exception(download_error[0])
            
            #if we are not in silent mode, show a confirmation message
            if not silent:
                messageBox.close() #close the downloading message box
                QMessageBox.information(None, "Download Complete", "Files downloaded successfully.")

            self.downloaded_repo = True  #set the flag to indicate we have downloaded the repo this session
            return True

        except Exception as e:
            if (not silent):
                messageBox.close()
                QMessageBox.critical(None,"Download Error", f"Failed to download files from github: {e}")
            return False

    def git_extract_folder(self, zip_folder_path = "", desired_folder_path="", silent=False):
        """
        @brief Extract a specific folder from a downloaded .zip file
        @param zip_folder_path The path to the folder in the zip file (from zip root)
        @param desired_folder_path The path to the folder in the GitHub repo (from repo root)
        @param silent If True, suppresses confirmation dialogs.
        @return True if successful, False otherwise.
        """
        # succ = self.git_download_repo(silent)  #download the repo if it has not already been downloaded
        # #if we failed to download the repo, exit early
        # if not succ:
        #     return False
        
        #if the folder paths are blank, exit early
        if zip_folder_path == "" or desired_folder_path == "":
            if not silent:
                QMessageBox.critical(None, "Extraction Error", "Folder paths cannot be blank")
            return False
        
        try:
            if zip_folder_path.__contains__("\\"):
                zip_folder_path = zip_folder_path.replace("\\", "/")  #convert to unix style paths for zipfile compatibility
            
            file_path, separator, file_name = zip_folder_path.rpartition('/')   #find just the file name from the string
            
            # Create output directories
            #dir = os.path.join(os.path.dirname(__file__), "temp", f"{folder_path}")
            dir = os.path.join(file_path, f"{desired_folder_path}")
            os.makedirs(dir, exist_ok=True)
            
            messageBox = QProgressDialog("Downloading files...", None, 0, 100)
            messageBox.setWindowTitle("Downloading")
            messageBox.setAutoClose(False)
            messageBox.setRange(0, 100)
            messageBox.setValue(0)
            messageBox.setLabelText("Downloading files...")
            
            messageBox.setLabelText("Extracting files...")
            QApplication.processEvents()
            
            # Extract the contents of the desired folder, preserving directories
            with zipfile.ZipFile(zip_folder_path, 'r') as zip_ref:
                prefix = desired_folder_path.rstrip('/') + '/'
                for file_info in zip_ref.infolist():
                    # Only process entries under the desired folder path
                    if not file_info.filename.startswith(prefix):
                        continue

                    # Relative path inside the desired folder
                    rel_path = file_info.filename[len(prefix):]

                    # If the entry is the folder itself, ensure directory exists and continue
                    if rel_path == '':
                        os.makedirs(dir, exist_ok=True)
                        continue

                    target_path = os.path.join(dir, rel_path)

                    # If entry is a directory, create it
                    is_dir = False
                    if hasattr(file_info, 'is_dir'):
                        try:
                            is_dir = file_info.is_dir()
                        except Exception:
                            is_dir = file_info.filename.endswith('/')
                    else:
                        is_dir = file_info.filename.endswith('/')

                    if is_dir:
                        os.makedirs(target_path, exist_ok=True)
                        continue

                    # Ensure parent directories exist, then extract file
                    parent_dir = os.path.dirname(target_path)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)

                    with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                
            messageBox.close()
            QApplication.processEvents()  # Process the close event
            return True
        except Exception as e:
            if not silent:
                messageBox.close()
                QMessageBox.critical(None, "Extraction Error", f"Failed to extract folder: {e}")
            return False