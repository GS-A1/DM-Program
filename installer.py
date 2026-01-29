"""
Installer script for the DM Assistant application.
This script is used to generate a simple installer.
The installer downloads the output folder from GitHub and places it in the specified installation directory.
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QMessageBox, QCheckBox, QTextEdit  # Import QMessageBox for dialog boxes
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog  # Import QFileDialog for file selection
from PyQt6.QtWidgets import QVBoxLayout, QPushButton

import sys
import os  # Import os for file path handling
import shutil  # Import shutil for file operations
import tempfile

from settingsAndStyle import StyleInfo # Import the function to set the custom style sheet information
from githubDownload import GitHubDownloader  # Import the GitHub downloader class


class MainWindow(QMainWindow):
    """
    @class MainWindow
    @brief The main window class for the DM Assistant application.
    """

    def __init__(self):
        """
        @brief Constructor for MainWindow. Initializes the UI and sets up the table and buttons.
        """
        super().__init__()
        
        self.gitHubDownload = GitHubDownloader()
        
        # In your __init__ method
        self.setWindowTitle("DM Assistant Installer")  # Set the window title
        self.setGeometry(100, 100, 600, 500)  # Set window size
                
        self.style_sheet = StyleInfo()      #object for storing and recalling the style sheet information
        self.style_sheet.resetLayout()  #reset the style sheet to default values
        self.set_Custom_Style_Sheet()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create checkboxes for downloads
        self.checkbox_characters = QCheckBox("Download Characters Files")
        self.checkbox_characters.setChecked(True)
        #self.checkbox_characters.stateChanged.connect(self.on_characters_checkbox_changed)
        
        self.checkbox_conditions = QCheckBox("Download Condition Spell Effects Files")
        self.checkbox_conditions.setChecked(True)
        
        # Add checkboxes to layout
        main_layout.addWidget(self.checkbox_characters)
        main_layout.addWidget(self.checkbox_conditions)
        
        # Create install button
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.on_install_clicked)
        main_layout.addWidget(self.install_button)
        
        # Create scrollable text box for terminal output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        #self.output_text.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #00ff00; font-family: 'Courier New'; font-size: 10px; }")
        main_layout.addWidget(self.output_text)
        
    def on_install_clicked(self):
        """
        @brief Handle the install button click event.
        """
        
        self.log_output("Starting Installation...")
        self.log_output("Selecting installation directory...")
        
        # Set the starting directory to Documents
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        installPath = QFileDialog.getExistingDirectory(self, "Select Installation Directory", documents_dir)
        
        if not installPath:
            self.log_output("Installation cancelled.")
            return
        
        
        ##############################################Download and install the program###################################################
        self.log_output("Downloading program...")
        download_path = os.path.join(tempfile.gettempdir(), "DM-Program") 
        succ = self.gitHubDownload.git_download_file(file="last_build/DM_Assistant.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
        if not succ:
            self.log_output("Failed to download program. Installation aborted.")
            return
        self.log_output("Files downloaded successfully.")
            
        self.log_output(f"Moving zip to installation directory {installPath}")
        #move the last_build folder to the selected installation directory
        source_folder = download_path
        try:
            if os.path.exists(os.path.join(installPath, "DM Assistant", "DM Assistant.exe")) or os.path.exists(os.path.join(installPath, "DM Assistant", "_internal")):
                reply = QMessageBox.question(None, "Confirm Installation", "An installation already exists in this folder. Do you wish to overide it? Other data such as save files will be preserved", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    # Remove only the executable and internal folder to preserve user data
                    self.remove_from_directory(os.path.join(installPath, "DM Assistant"), ["DM Assistant.exe", "_internal"])
                else:
                    self.log_output("Installation cancelled.")
                    return
            shutil.move(os.path.join(source_folder, "DM_Assistant.zip"), installPath)
        except Exception as e:
            self.log_output(f"Failed to install files: {e}")
            return
        
        output_zip_path = os.path.join(installPath, "DM_Assistant.zip")
        if output_zip_path.__contains__("\\"):
                output_zip_path = output_zip_path.replace("\\", "/")
        print(f"Extracting files: {output_zip_path}")
        #extract the .zip file in the installation directory
        shutil.unpack_archive(output_zip_path, installPath)
        os.remove(output_zip_path)  #remove the .zip file after extraction
        print("Program installed successfully.")
        
        #####################################################Download and install Characters###################################################
        #if needed, extract the settings folders
        #characters
        if self.checkbox_characters.isChecked():
            self.log_output("Extracting Characters...")
            suc = downloadAndExtractSettingsFolder(installPath=installPath, folderName="Characters")
            if suc:
                self.log_output("Character files installed successfully.")
            else:
                self.log_output("Failed to install Character files.")
            # succ = True #set to true incase we dont need to download it
            # #if the files dont already exist in the temp folder, download the settings zip
            # if not os.path.exists(os.path.join(download_path, "Settings.zip")):
            #     succ = self.gitHubDownload.git_download_file(file="last_build/Settings.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
            # if not succ:
            #     self.log_output("Failed to download Settings.zip.")
            #     return
            
            # succ = self.gitHubDownload.git_extract_folder(silent=True, zip_folder_path = os.path.join(download_path, "Settings.zip"), desired_folder_path="Characters")
            
            # #moving the characters to the correct folder
            # self.log_output(f"Moving Character Files to {installPath}/DM Assistant/Settings/Characters ...")
            # source_char_folder = os.path.join(download_path, "Characters")
            # dest_char_folder = os.path.join(installPath, "DM Assistant", "Settings", "Characters")
            # try:
            #     if os.path.exists(dest_char_folder):
            #         reply = QMessageBox.question(None, "Confirm Installation", "A Characters folder already exists. Do you wish to overide it? All data in the folder will be deleated", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            #         if reply == QMessageBox.StandardButton.Yes:
            #             # Remove only the executable and internal folder to preserve user data
            #             shutil.rmtree(dest_char_folder)  # Remove existing characters folder
            #             shutil.move(source_char_folder, dest_char_folder)
            #         else:
            #             self.log_output("Failed to install Character files: Installation cancelled.")
            #     else:
            #         shutil.move(source_char_folder, dest_char_folder)
            #     self.log_output("Character files installed successfully.")
            # except Exception as e:
            #     self.log_output(f"Failed to move character files: {e}")
            #     return
        #####################################################Download and install Conditions and Spell Effects###################################################    
        if self.checkbox_conditions.isChecked():
            self.log_output("Extracting Conditions and Spell Effects...")
            suc = downloadAndExtractSettingsFolder(installPath=installPath, folderName="Condition_Spell_Effects")
            if suc:
                self.log_output("Conditions and Spell Effects installed successfully.")
            else:
                self.log_output("Failed to install Conditions and Spell Effects.")
            # succ = True #set to true incase we dont need to download it
            # #if the files dont already exist in the temp folder, download the settings zip
            # if not os.path.exists(os.path.join(download_path, "Settings.zip")):
            #     succ = self.gitHubDownload.git_download_file(file="last_build/Settings.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
            # if not succ:
            #     self.log_output("Failed to download Settings.zip.")
            #     return
            
            # succ = self.gitHubDownload.git_extract_folder(silent=True, zip_folder_path = os.path.join(download_path, "Settings.zip"), desired_folder_path="Condition_Spell_effects")
            
            # #moving the conditions and spell effects to the correct folder
            # self.log_output(f"Moving Condition and Spell Effect Files to {installPath}/DM Assistant/Settings/Condition_Spell_Effects ...")
            # source_char_folder = os.path.join(download_path, "Condition_Spell_Effects")
            # dest_char_folder = os.path.join(installPath, "DM Assistant", "Settings", "Condition_Spell_Effects")
            # try:
            #     if os.path.exists(dest_char_folder):
            #         reply = QMessageBox.question(None, "Confirm Installation", "A Condition_Spell_Effects folder already exists. Do you wish to overide it? All data in the folder will be deleated", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            #         if reply == QMessageBox.StandardButton.Yes:
            #             # Remove only the executable and internal folder to preserve user data
            #             shutil.rmtree(dest_char_folder)  # Remove existing characters folder
            #             shutil.move(source_char_folder, dest_char_folder)
            #         else:
            #             self.log_output("Failed to install Condition_Spell_Effects files: Installation cancelled.")
            #     else:
            #         shutil.move(source_char_folder, dest_char_folder)
            # except Exception as e:
            #     self.log_output(f"Failed to move Condition_Spell_Effects files: {e}")
            #     return
        
        #create the save files folder
        save_files_folder = os.path.join(installPath, "DM Assistant", "Save Files")
        os.makedirs(save_files_folder, exist_ok=True)    
        self.log_output("Installation complete!")
    
    def log_output(self, message):
        """
        @brief Log a message to the output text box.
        @param message The message to log.
        """
        self.output_text.append(message)
        

#**************************Functions********************************************
    def remove_from_directory(self, directory, items_to_remove):
        """
        @brief Remove only specific files and folders from a directory.
        @param directory The directory to clean.
        @param exclude_items List of folder/file names to remove (e.g., ["DM Assistant.exe", "_internal"]).
        """
        if not os.path.exists(directory):
            return
        
        for item in items_to_remove:
            item_path = os.path.join(directory, item)
            if os.path.exists(item_path):
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        self.log_output(f"Removed folder: {item}")
                    else:
                        os.remove(item_path)
                        self.log_output(f"Removed file: {item}")
                except Exception as e:
                    self.log_output(f"Warning: Could not remove {item}: {e}")
    
    def set_Custom_Style_Sheet(self):
            style = f"""
                /*General Styles applied to most things in the app*/
                QWidget {{
                    background: {self.style_sheet.colour_general};
                    font-family: "{self.style_sheet.font_general_style}";
                    font-size: {self.style_sheet.font_general_size}pt;
                    color: {self.style_sheet.colour_general_text}
                }}
                
                QMainWindow {{
                    background: rgba(250, 242, 220, 255);
                }}
                
                QGroupBox {{
                    border: 2px solid #a47b5a;
                    border-radius: 6px;
                    margin-top: 6px;
                    background: rgba(255, 245, 230, 180);
                    font-weight: bold;
                    color: #2a1a0b;
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 4px;
                    background: {self.style_sheet.colour_button};
                    color: {self.style_sheet.colour_button_text};
                    border-radius: 3px;
                }}
                QTabBar::tab {{
                    background: {self.style_sheet.colour_button};
                    color: {self.style_sheet.colour_button_text};
                    padding: 8px 20px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    font-weight: bold;
                }}
                QTabBar::tab:selected {{
                    background: {self.style_sheet.findHover(self.style_sheet.colour_button, 25)};
                    color: {self.style_sheet.colour_button_text};
                }}
                
                QTableWidget{{
                    background: {self.style_sheet.colour_minor};
                    font-family: "{self.style_sheet.font_table_style}";
                    font-size: {self.style_sheet.font_table_size}pt;
                    color: {self.style_sheet.colour_table_text};
                    line-height: 1.4em;
                }}
                QTableWidget::item:selected {{
                    color: black;  /* Set text color to black */
                    background-color: {self.style_sheet.colour_minor};
                }}
                QHeaderView::section {{
                    background: {self.style_sheet.colour_minor};
                    font-family: "{self.style_sheet.font_table_style}";
                    font-size: {self.style_sheet.font_table_size}pt;
                    color: {self.style_sheet.colour_table_text};
                }}
                
                QPushButton {{
                    background-color: {self.style_sheet.colour_button};
                    color: {self.style_sheet.colour_button_text};
                    font-family: "{self.style_sheet.font_button_style}";
                    font-size: {self.style_sheet.font_button_size}pt;
                    padding: 8px 20px;
                    border: 1px solid #7f1f1f;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.style_sheet.findHover(self.style_sheet.colour_button)};
                    color: #fffdd5;
                }}
                QPushButton:pressed {{
                    background-color: {self.style_sheet.findHover(self.style_sheet.colour_button, 70)}; /*tweaked so a press is a bit different to a hover */
                    color: #fffdd5;
                }}
                
                QComboBox{{
                    background: {self.style_sheet.colour_minor};
                    background-color: {self.style_sheet.colour_minor};
                }}
                
                QListWidget{{
                    background: {self.style_sheet.colour_minor};
                    background-color: {self.style_sheet.colour_minor};
                }}  
                
                QLineEdit{{
                    background: {self.style_sheet.colour_minor};
                    background-color: {self.style_sheet.colour_minor};
                }}    
                
                QTextEdit{{
                    background: {self.style_sheet.colour_minor};
                    background-color: {self.style_sheet.colour_minor};
                }}    
                
                /* menu frame (one border around the whole menu) */
                QMenu {{
                    border: 1px solid rgba(0, 0, 0, 0.5);      /* outer border around all items */
                    border-radius: 3px;
                    padding: 2px;                   /* space inside the menu */
                }}
                
                /* individual items: no outer border, only change background on hover */
                QMenu::item {{
                    background: transparent;
                    padding: 6px 20px;
                }}
                QMenu::item:selected {{
                    background-color: rgba(241, 233, 212, 255);
                    color: #2a1a0b;
                    border: 1px solid #7f1f1f;      /* outer border around all items */
                    border-radius: 3px;
                }}            
                
            """
            QApplication.instance().setStyleSheet(style)
        
#**************************Events**********************************************
    def closeEvent(self, event):
        """
        @brief Ask if the user wants to save before closing.
        @param event The close event.
        """
        #delete the temp folder and all its contents if it exists
        temp_dir = os.path.join(tempfile.gettempdir(), "DM-Program")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        event.accept()  # Allow the window to close
        
#**************************End of Class***************************************


#**************************Public Functions***************************************
def downloadAndExtractSettingsFolder(installPath = "", folderName = ""):
    """
    @breif Download the settigns folder to temp and extract a folder from it to the install path
    @param installPath The path to install the extracted folder to
    """
    gitHubDownload = GitHubDownloader()
    download_path = os.path.join(tempfile.gettempdir(), "DM-Program") 
    succ = True #set to true incase we dont need to download it
    #if the files dont already exist in the temp folder, download the settings zip
    if not os.path.exists(os.path.join(download_path, "Settings.zip")):
        succ = gitHubDownload.git_download_file(file="last_build/Settings.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
    if not succ:
        #self.log_output("Failed to download Settings.zip.")
        return False
    
    succ = gitHubDownload.git_extract_folder(silent=True, zip_folder_path = os.path.join(download_path, "Settings.zip"), desired_folder_path=folderName)
    
    #moving folderName to the correct folder
    #self.log_output(f"Moving Character Files to {installPath}/DM Assistant/Settings/Characters ...")
    source_char_folder = os.path.join(download_path, folderName)
    dest_char_folder = os.path.join(installPath, "DM Assistant", "Settings", folderName)
    try:
        if os.path.exists(dest_char_folder):
            reply = QMessageBox.question(None, "Confirm Installation", f"A {folderName} folder already exists. Do you wish to overide it? All data in the folder will be deleated", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # Remove only the executable and internal folder to preserve user data
                shutil.rmtree(dest_char_folder)  # Remove existing characters folder
                shutil.move(source_char_folder, dest_char_folder)
            else:
                #self.log_output("Failed to install Character files: Installation cancelled.")
                return False
        else:
            shutil.move(source_char_folder, dest_char_folder)
        #self.log_output("Character files installed successfully.")
        return True
    except Exception as e:
        #self.log_output(f"Failed to move character files: {e}")
        return False

#**************************Main Function***********************************
if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "Settings", "dnd_dm_icons.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    
    window.show()

    app.exec()