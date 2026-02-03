from PyQt6.QtWidgets import QProgressDialog, QMessageBox, QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import QEventLoop, QTimer, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

import os
import urllib.request
import shutil  # Import shutil for file operations
import zipfile
import threading
import tempfile
import time
          
class GitHubDownloader:
    """
    @breif Class deals with downloading files from Github
    """
    
    repo_url = "https://raw.githubusercontent.com/GS-A1/DM-Program/main"
    downloaded_repo_path = ""
    zip_path = ""
    downloaded_repo = False  # Flag to indicate if the repo has been downloaded this session
    
    def git_download_file_qt(self, file: str = "", outputPath: str = "", silent: bool = False, timeoutTime: int = 10000) -> bool:
        """
        @brief Download a specific file from the GitHub repository
        @param file The specific file to dowload. Must include the whole path from the repo root
        @param outputPath The local path to the folder to save the downloaded file. If blank, uses the same path as in the repo.
        @param silent If True, suppresses UI dialogs.
        @param timeoutTime The time in milliseconds to wait before timing out the download if no progress is made.
        @return False if there was an error, True otherwise.
        """
        file_path, _, file_name = file.rpartition('/')

        if not file:
            if not silent:
                QMessageBox.critical(None, "File Error", "File name cannot be blank")
            return False

        repo_raw_url = f"{self.repo_url}/{file}"

        # Output directory
        if outputPath == "":
            local_dir = file_path if file_path else "."
        else:
            local_dir = outputPath

        os.makedirs(local_dir, exist_ok=True)

        final_path = os.path.join(local_dir, file_name)
        tmp_path = final_path + ".part"

        # Progress dialog
        progress = QProgressDialog("Downloading...", "Cancel", 0, 100)
        progress.setWindowTitle("Downloading")
        progress.setAutoClose(False)
        progress.setRange(0, 100)
        progress.setValue(0)

        # Keep a single manager alive (important)
        manager = getattr(self, "net_manager", None)
        if manager is None:
            manager = QNetworkAccessManager()   # no parent because self isn't QObject
            self.net_manager = manager

        request = QNetworkRequest(QUrl(repo_raw_url))
        reply = manager.get(request)

        # Track last time we received bytes (for "no progress" timeout)
        last_activity_ms = time.time() * 1000.0

        # Ensure we don't overwrite a good existing file unless download fully succeeds
        try:
            f = open(tmp_path, "wb")
        except OSError as e:
            reply.abort()
            reply.deleteLater()
            if not silent:
                QMessageBox.critical(None, "File Error", f"Cannot write to: {tmp_path}\n{e}")
            return False

        def cleanup_tmp():
            try:
                f.close()
            except Exception:
                pass
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

        def on_ready_read():
            nonlocal last_activity_ms
            data = reply.readAll()
            if not data.isEmpty():
                f.write(bytes(data))
                last_activity_ms = time.time() * 1000.0

        def on_progress(bytes_received: int, bytes_total: int):
            nonlocal last_activity_ms
            # Progress signal implies bytes are moving
            last_activity_ms = time.time() * 1000.0

            if bytes_total > 0 and not silent:
                percent = int((bytes_received / bytes_total) * 100)
                percent = max(0, min(percent, 100))
                progress.setValue(percent)
                progress.setLabelText(f"Downloading: {percent}%")

        # "No progress" timeout checker (NOT an overall timeout)
        timer = QTimer()
        timer.setInterval(200)  # check 5x/s

        def on_timeout_check():
            now_ms = time.time() * 1000.0
            if now_ms - last_activity_ms > timeoutTime:
                reply.abort()  # triggers finished; handled below

        timer.timeout.connect(on_timeout_check)

        # Cancel button just aborts the reply
        if not silent:
            progress.canceled.connect(reply.abort)
            progress.show()

        # Wire signals
        reply.readyRead.connect(on_ready_read)
        reply.downloadProgress.connect(on_progress)

        # Run a local event loop until finished (keeps UI responsive)
        loop = QEventLoop()

        def on_finished():
            loop.quit()

        reply.finished.connect(on_finished)

        timer.start()
        loop.exec()
        timer.stop()

        # Finalize file handle
        try:
            f.flush()
        except Exception:
            pass
        try:
            f.close()
        except Exception:
            pass
        
        
        #from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest

        # Debugging code for if the download is not working for whatver reason
        # http_status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        # redir = reply.attribute(QNetworkRequest.Attribute.RedirectionTargetAttribute)

        # err = reply.error()

        # print("---- DOWNLOAD DEBUG ----")
        # print("URL:", reply.url().toString())
        # print("NetworkError value:", err.value)
        # print("NetworkError name:", err.name)
        # print("errorString:", reply.errorString())
        # print("HTTP status:", http_status)
        # print("Redirect target:", redir.toString() if redir else None)
        # print("------------------------")
        
        # Check result
        if reply.error() != QNetworkReply.NetworkError.NoError:
            err = reply.errorString()
            reply.deleteLater()
            cleanup_tmp()
            if not silent:
                progress.close()
                QMessageBox.critical(None, "Download Error", f"Failed to download {file_name}:\n{err}")
            return False

        reply.deleteLater()

        # Atomic replace
        try:
            os.replace(tmp_path, final_path)
        except OSError as e:
            cleanup_tmp()
            if not silent:
                progress.close()
                QMessageBox.critical(None, "File Error", f"Failed to save file:\n{e}")
            return False

        if not silent:
            progress.setValue(100)
            progress.close()

        return True
    
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
    
    #OLD METHODS, NOT AS SAFE OR EFFICIENT AS THE QT NETWORKING ONE ABOVE
    def git_download_file(self, file = "", outputPath = "", silent=False, timeoutTime=10000):
        """
        @brief Update the the conditions/spell effects file from github
        @param file The specific file to dowload. Must include the whole path from the repo root
        @param outputPath The local path to the folder to save the downloaded file. If blank, uses the same path as in the repo.
        @param silent If True, suppresses UI dialogs.
        @param timeoutTime The time in milliseconds to wait before timing out the download if no progress is made.
        @return False if there was an error, True otherwise.
        """
        file_path, separator, file_name = file.rpartition('/')   #find just the file name from the string
        
        #create the message box early so we can close it on an error
        messageBox = QProgressDialog("Downloading files...", "Cancel", 0, 100)
        messageBox.setWindowTitle("Downloading")
        messageBox.setAutoClose(False)
        messageBox.setRange(0, 100)
        messageBox.setValue(0)
        messageBox.setLabelText("Downloading files...")
        
        try:
            #Try to download the default file from the GitHub repository
            if file != "":
                
                repo_raw_url = f"{self.repo_url}/{file}"
                
                #if they have not specified an output path, use the file name
                if outputPath == "":
                    local_path = file_path if file_path else "."  #use the same path as in the repo. If blank, use current directory
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
                download_error = [None]  # Use list to capture error in thread
                progress_data = {'percent': 0}  # Thread-safe progress tracking
                cancel_event = threading.Event() # Event to signal cancellation

                #temp exception to signal download cancellation
                class DownloadCancelled(Exception):
                    pass
            
                def download_with_progress():
                    """@brief: Download function to run in thread"""
                    
                    tmp_path = file_local_path + ".part"  #temporary file path during download
                    
                    try:
                        def download_progress(blocknum, blocksize, totalsize):
                            #if the cancel event is set, raise an exception to stop the download
                            if cancel_event.is_set():
                                raise DownloadCancelled("Cancelled")
                            
                            """Collect progress data (called from worker thread)"""
                            if totalsize > 0:
                                downloaded = blocknum * blocksize
                                percent = min(int((downloaded / totalsize) * 100), 100)
                                progress_data['percent'] = percent  # Store for main thread to read
                        
                        urllib.request.urlretrieve(repo_raw_url, tmp_path, reporthook=download_progress)
                        #urllib.request.urlretrieve(repo_raw_url, file_local_path, reporthook=download_progress)
                        
                        #if an cancle event came right at the end, treat likde a cancellation
                        if cancel_event.is_set():
                            raise DownloadCancelled("Cancelled")
                        
                        os.replace(tmp_path, file_local_path)  #rename temp file to final file name
                    
                    except DownloadCancelled:
                        # Remove partially downloaded file if cancelled
                        try:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                        except Exception:
                            pass  # If removal fails, just continue
                        download_error[0] = "Download cancelled by user."
                    
                    except Exception as e:
                        try:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                        except Exception:
                            pass  # If removal fails, just continue
                        download_error[0] = str(e)
                
                def cancel_download():
                    """
                    @brief: Function to signal cancellation with timeout
                    """
                    cancel_event.set()
                    startTIme = time.time() * 1000  #get the current time in milliseconds
                    while download_thread.is_alive():
                        currTime = time.time() * 1000  #get the current time in milliseconds
                        if currTime - startTIme > 5000:  #wait up to 5 seconds for the thread to exit
                            break
                        QApplication.processEvents()        #process UI events
                        download_thread.join(timeout=0.1)   #sleep this thread briefly
                
                # Run download in a separate thread
                download_thread = threading.Thread(target=download_with_progress, daemon=False)
                download_thread.start()
                
                #store the time we started downloading or last got a percent update
                startTIme = time.time() * 1000  #get the current time in milliseconds
                oldPercent = 0
                
                # Keep UI responsive while download is happening
                while download_thread.is_alive():
                    #include a timeout to allow for graceful exit if needed
                    #if there has been some progress, reset the start time
                    if progress_data['percent'] != oldPercent:
                        startTIme = time.time() * 1000  #get the current time in milliseconds
                        oldPercent = progress_data['percent']
                    currTime = time.time() * 1000  #get the current time in milliseconds
                    # If more than too much time has passed since we last got a percent update
                    if currTime - startTIme > timeoutTime:  
                        cancel_download()
                        #cancel_event.set()  #signal cancellation
                        #download_thread.join(timeout=0.1)
                        raise Exception("Download timed out")
                    # Update UI from main thread only
                    if not silent:
                        messageBox.setValue(progress_data['percent'])
                        messageBox.setLabelText(f"Downloading: {progress_data['percent']}%")
                        #if someone has canceled the download from the message box
                        if messageBox.wasCanceled():
                            #cancel_event.set()  #signal cancellation
                            cancel_download()
                            raise Exception("download cancelled by user")
                    QApplication.processEvents()
                    download_thread.join(timeout=0.1)
                
                # Check if there was an error
                if download_error[0] is not None:
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
      
    def git_download_repo(self, silent=False, timeoutTime=10000):
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
            
            download_error = [None]  # Use list to capture error in thread
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
            
            #store the time we started downloading or last got a percent update
            startTIme = time.time() * 1000  #get the current time in milliseconds
            oldPercent = 0
            
            # Keep UI responsive while download is happening
            while download_thread.is_alive():
                #include a timeout to allow for graceful exit if needed
                #if there has been some progress, reset the start time
                if progress_data['percent'] != oldPercent:
                    startTIme = time.time() * 1000  #get the current time in milliseconds
                    oldPercent = progress_data['percent']
                currTime = time.time() * 1000  #get the current time in milliseconds
                # If more than too much time has passed since we last got a percent update
                if currTime - startTIme > timeoutTime:  
                    download_thread.join(timeout=0.1)
                    raise Exception("Download timed out")
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

    