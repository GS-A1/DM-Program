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
        
        
        self.log_output("Downloading program...")
        #succ = self.gitHubDownload.git_download_repo() #download the repo from github
        download_path = os.path.join(tempfile.gettempdir(), "DM-Program") 
        succ = self.gitHubDownload.githiub_download_file(file="last_build/DM_Assistant.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
        if not succ:
            self.log_output("Failed to download program. Installation aborted.")
            return
        self.log_output("Files downloaded successfully.")
            
        #self.log_output("Extracting program file...")
        #extract the last_build folder to get the lastest version of the program
                
        # succ = self.gitHubDownload.git_extract_folder(silent=True, folder_path="last_build")
        # if not succ:
        #     self.log_output("Failed to extract last_build folder. Installation aborted.")
        #     return
        
        # self.log_output(f"Moving executable to installation directory {installPath}")
        # #move the last_build folder to the selected installation directory
        # source_folder = os.path.join(self.gitHubDownload.downloaded_repo_path, "last_build")
        # try:
        #     if os.path.exists(os.path.join(installPath, "DM Assistant", "DM Assistant.exe")) or os.path.exists(os.path.join(installPath, "DM Assistant", "_internal")):
        #         reply = QMessageBox.question(None, "Confirm Installation", "An installation already exists in this folder. Do you wish to overide it? Other data such as save files will be preserved", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        #         if reply == QMessageBox.StandardButton.Yes:
        #             # Remove only the executable and internal folder to preserve user data
        #             self.remove_from_directory(os.path.join(installPath, "DM Assistant"), ["DM Assistant.exe", "_internal"])
        #         else:
        #             self.log_output("Installation cancelled.")
        #             return
        #     shutil.move(os.path.join(source_folder, "DM Assistant.zip"), installPath)
        # except Exception as e:
        #     self.log_output(f"Failed to install files: {e}")
        #     return
        
        # output_zip_path = os.path.join(installPath, "DM Assistant.zip")
        # print(f"Extracting executable file: {output_zip_path}")
        # #extract the .zip file in the installation directory
        # shutil.unpack_archive(output_zip_path, installPath)
        # os.remove(output_zip_path)  # Remove the zip file after extraction
        
        # #if needed, extract the settings folders
        # #characters
        # if self.checkbox_characters.isChecked():
        #     self.log_output("Extracting Characters...")
        #     succ = self.gitHubDownload.git_extract_folder(silent=True, folder_path="Settings/Characters")
        #     if not succ:
        #         self.log_output("Failed to extract the characters folder. Installation aborted.")
        #         return
        #     #moving the characters to the correct folder
        #     self.log_output(f"Moving Character Files to {installPath}/Settings/Characters ...")
        #     source_char_folder = os.path.join(self.gitHubDownload.downloaded_repo_path, "Settings", "Characters")
        #     dest_char_folder = os.path.join(installPath, "DM Assistant", "Settings", "Characters")
        #     try:
        #         if os.path.exists(dest_char_folder):
        #             reply = QMessageBox.question(None, "Confirm Installation", "A Characters folder already exists. Do you wish to overide it? All data in the folder will be deleated", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        #             if reply == QMessageBox.StandardButton.Yes:
        #                 # Remove only the executable and internal folder to preserve user data
        #                 shutil.rmtree(dest_char_folder)  # Remove existing characters folder
        #                 shutil.move(source_char_folder, dest_char_folder)
        #             else:
        #                 self.log_output("Failed to install Character files: Installation cancelled.")
        #         else:
        #             shutil.move(source_char_folder, dest_char_folder)
        #     except Exception as e:
        #         self.log_output(f"Failed to move character files: {e}")
        #         return
        # if self.checkbox_conditions.isChecked():
        #     self.log_output("Extracting Condition Spell Effects...")
        #     succ = self.gitHubDownload.git_extract_folder(silent=True, folder_path="Settings/Condition_Spell_Effects")
        #     if not succ:
        #         self.log_output("Failed to extract the condition/spell effects folder. Installation aborted.")
        #         return
        #     #moving the spell conditions to the correct folder
        #     self.log_output(f"Moving Condition Spell Effects to {installPath}/Settings/Condition_Spell_Effects ...")
        #     source_char_folder = os.path.join(self.gitHubDownload.downloaded_repo_path, "Settings", "Condition_Spell_Effects")
        #     dest_char_folder = os.path.join(installPath, "DM Assistant", "Settings", "Condition_Spell_Effects")
        #     try:
        #         if os.path.exists(dest_char_folder):
        #             reply = QMessageBox.question(None, "Confirm Installation", "A Conditions and Spell Effects folder already exists. Do you wish to overide it? All data in the folder will be deleated", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        #             if reply == QMessageBox.StandardButton.Yes:
        #                 # Remove only the executable and internal folder to preserve user data
        #                 shutil.rmtree(dest_char_folder)  # Remove existing characters folder
        #                 shutil.move(source_char_folder, dest_char_folder)
        #             else:
        #                 self.log_output("Failed to install Character files: Installation cancelled.")
        #         else:
        #             shutil.move(source_char_folder, dest_char_folder)
        #     except Exception as e:
        #         self.log_output(f"Failed to move conditions and spell effects files: {e}")
        #         return
        
        # #create the save files folder
        # save_files_folder = os.path.join(installPath, "DM Assistant", "Save Files")
        # os.makedirs(save_files_folder, exist_ok=True)    
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
        temp_dir = self.gitHubDownload.downloaded_repo_path
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        event.accept()  # Allow the window to close
        
#**************************End of Class***************************************

#**************************Main Function***********************************
if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "Settings", "dnd_dm_icons.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    
    window.show()

    app.exec()