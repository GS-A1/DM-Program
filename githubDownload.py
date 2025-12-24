from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QApplication
import os
import urllib.request
import shutil  # Import shutil for file operations
import zipfile

            
class GitHubDownloader:
    """
    @breif Class deals with downloading files from Github
    """
    
    repo_url = "https://raw.githubusercontent.com/GS-A1/DM-Program/main"
    downloaded_repo = False  # Flag to track if the github repo has been downloaded this session
    downloaded_repo_path = ""
    
    def githiub_download_file(self, file = ""):
        """
        @brief Update the the conditions/spell effects file from github
        @param file The specific file to dowload. Must include the whole path from the repo root
        @return True if there was an error, False otherwise.
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
                local_path = file

                # Download and save the file
                #urllib.request.urlretrieve(repo_raw_url, local_path)

                #create a message box to show download progress
                messageBox.show()
                #need to call process events to show the dialog. If this fails, add a small delay between calls
                QApplication.processEvents()
                QApplication.processEvents()
                
                #call back for download progress
                def download_progress(blocknum, blocksize, totalsize):
                    """Update progress dialog during download"""
                    if totalsize > 0:
                        downloaded = blocknum * blocksize
                        percent = min(int((downloaded / totalsize) * 100), 100)
                        messageBox.setValue(percent)
                    QApplication.processEvents()  # Keep UI responsive
                
                urllib.request.urlretrieve(repo_raw_url, local_path, reporthook=download_progress) #download the file and calla  callback when chunks are downloaded
                
                self.conditions_file_error = False  # Reset the error flag
                messageBox.close()
                QApplication.processEvents()  # Process the close event
                
                return False
            else:
                QMessageBox.critical(None, "File Error", "File name cannot be blank")
                return True
        except Exception as e:
            messageBox.close()  #close the message box on error
            QMessageBox.critical(None, "Download Error", f"Failed to download {file_name} file: {e}")
            return True
    
    def git_download_repo(self, silent=False):
        """
        @brief Download the latest version of the DM Program from GitHub.
        @param silent If True, suppresses confirmation dialogs.
        @return True if there was an error, False otherwise.
        """
        
        #create the message box early so we can close it on an error
        messageBox = QProgressDialog("Downloading files...", None, 0, 100)
        messageBox.setWindowTitle("Downloading")
        messageBox.setAutoClose(False)
        messageBox.setRange(0, 100)
        messageBox.setValue(0)
        messageBox.setLabelText("Downloading files...")
        
        if self.downloaded_repo == True:
            #already downloaded the repo this session, we dont need to do it again
            #prevents slowdown on multiple calls
            return True
        
        try:            
            # Create temp folder
            temp_dir = os.path.join(os.path.dirname(__file__), "temp")
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
                #silent mode, just overwrite the folder if it exists
                os.makedirs(temp_dir, exist_ok=True)
                shutil.rmtree(temp_dir)
                
            
            # Create output directories
            conditions_dir = os.path.join(os.path.dirname(__file__), "temp", "Condition_Spell_Effects")
            characters_dir = os.path.join(os.path.dirname(__file__), "temp", "Characters")
            os.makedirs(conditions_dir, exist_ok=True)
            os.makedirs(characters_dir, exist_ok=True)

            messageBox.show()
            #need to call process events to show the dialog. If this fails, add a small delay between calls
            QApplication.processEvents()
            QApplication.processEvents()

            # Download repo zip with progress updates
            # raw.githubusercontent.com is for raw file blobs; use the GitHub archive URL for repository zips
            zip_url = "https://github.com/GS-A1/DM-Program/archive/refs/heads/main.zip"
            zip_path = os.path.join(temp_dir, "repo.zip")
            
            def download_progress(blocknum, blocksize, totalsize):
                """Update progress dialog during download"""
                if totalsize > 0:
                    downloaded = blocknum * blocksize
                    percent = min(int((downloaded / totalsize) * 100), 100)
                    messageBox.setValue(percent)
                QApplication.processEvents()  # Keep UI responsive
            
            urllib.request.urlretrieve(zip_url, zip_path, reporthook=download_progress)
            
            messageBox.setLabelText("Extracting files...")
            QApplication.processEvents()
            
            # Extract Condition_Spell_Effects and Characters folders
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    # Extract Condition_Spell_Effects folder
                    if "Settings/Condition_Spell_Effects/" in file_info.filename:
                        file_name = file_info.filename.split("Settings/Condition_Spell_Effects/")[-1]
                        if file_name:  # Skip folder entry itself
                            local_path = os.path.join(conditions_dir, file_name)
                            with zip_ref.open(file_info) as source, open(local_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                    
                    # Extract Characters folder
                    if "Settings/Characters/" in file_info.filename:
                        file_name = file_info.filename.split("Settings/Characters/")[-1]
                        if file_name:  # Skip folder entry itself
                            local_path = os.path.join(characters_dir, file_name)
                            with zip_ref.open(file_info) as source, open(local_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
            #os.remove(zip_path) #delete the .zip file after extraction
            
            messageBox.close()
            QApplication.processEvents()  # Process the close event
            
            #if we are not in silent mode, show a confirmation message
            if not silent:
                QMessageBox.information(None, "Download Complete", "Files downloaded successfully.")
            
            self.downloaded_repo = True #set the flag so we know the repo has been downloaded
            
            return False

        except Exception as e:
            messageBox.close()
            QMessageBox.critical(None,"Download Error", f"Failed to download files from github: {e}")
            return True
