"""
Installer script for the DM Assistant application.
This script is used to generate a simple installer.
The installer downloads the output folder from GitHub and places it in the specified installation directory.
"""
from PyQt6.QtWidgets import QLabel, QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QMessageBox, QCheckBox, QTextEdit  # Import QMessageBox for dialog boxes
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog  # Import QFileDialog for file selection
from PyQt6.QtWidgets import QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

import sys
import os  # Import os for file path handling
import shutil  # Import shutil for file operations
import tempfile
import ctypes  # For setting AppUserModelID on Windows

from settingsAndStyle import StyleInfo # Import the function to set the custom style sheet information
from githubDownload import GitHubDownloader  # Import the GitHub downloader class

from updateVersionNum import readVersionNumber  # Import the function to read the version number

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
        
        self.version = self.readversionnumber() #read the version number from the version.txt file
        
        # In your __init__ method
        self.setWindowTitle("DM Assistant Installer")  # Set the window title
        self.setGeometry(100, 100, 600, 500)  # Set window size
         
        self.style_sheet = StyleInfo()      #object for storing and recalling the style sheet information
        self.style_sheet.resetLayout()  #reset the style sheet to default values
        self.set_Custom_Style_Sheet()
        
        # Create a menu bar
        menu_bar = self.menuBar()
        
        # Create "Help" menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.about_menue_action)
        
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
        self.log_output("**********************************************************************************")
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
        suc = downloadAndInstallProgram(installPath=installPath) #call function to handle downloading and installing the program
        #was the download and install successful?
        if suc:
            self.log_output(f"Program installed successfully to {installPath}")
        else:
            self.log_output("Failed to install program.")
            return
        
        #####################################################Download and install Characters###################################################
        #do we need to extract the characters folder?
        if self.checkbox_characters.isChecked():
            self.log_output("Extracting Characters...")
            suc = downloadAndExtractSettingsFolder(installPath=os.path.join(installPath, "DM Assistant", "Settings"), folderName="Characters")    #call function to handle downloading and installing the characters folder
            #was the download and install successful?
            if suc:
                self.log_output(f"Character files installed successfully to {os.path.join(installPath, 'DM Assistant', 'Settings', 'Characters')}.")
            else:
                self.log_output("Failed to install Character files.")
                
        #####################################################Download and install Conditions and Spell Effects###################################################    
        #do we need to extract the Condition_Spell_Effects folder?
        if self.checkbox_conditions.isChecked():
            self.log_output("Extracting Conditions and Spell Effects...")
            suc = downloadAndExtractSettingsFolder(installPath=os.path.join(installPath, "DM Assistant", "Settings"), folderName="Condition_Spell_Effects")   #call function to handle downloading and installing the conditions and spell effects folder
            #was the download and install successful?
            if suc:
                self.log_output(f"Conditions and Spell Effects installed successfully to {os.path.join(installPath, 'DM Assistant', 'Settings', 'Condition_Spell_Effects')}.")
            else:
                self.log_output("Failed to install Conditions and Spell Effects.")
                
        ##############################################Finalizing Installation###################################################
        
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
    
    def readversionnumber(self):
        """
        @brief: Read the version number from the version.txt file.
        """
        version_file_path = readVersionNumber() #read the version number from the version.txt file
        if version_file_path == "Unknown Version":
            QMessageBox.warning(
            self,
            "Invalid Input",
            f"Could not find version file at {version_file_path}"
            )
        else:
            return version_file_path

    def about_menue_action(self):
        """
        @brief Show an "About" dialog with program information.
        """
        about_text = (
            "<h2>DM Assistant Installer</h2>"
            f"<p>Version: {self.version}</p>"
            "<p>Developed by: GS-A1</p>"
            "<p>git repository: https://github.com/GS-A1/DM-Program</p>"
            "<p>This application is designed to install DM Assistant "
        )
        QMessageBox.about(self, "About DM Assistant Installer", about_text)
        
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
    @breif Download the Settings folder to temp and extract a folder from it to the install path
    @param installPath The path to install the extracted folder to
    """
    gitHubDownload = GitHubDownloader()
    download_path = os.path.join(tempfile.gettempdir(), "DM-Program") 
    succ = True #set to true incase we dont need to download it
    #if the files dont already exist in the temp folder, download the settings zip
    if not os.path.exists(os.path.join(download_path, "Settings.zip")):
        succ = gitHubDownload.git_download_file_qt(file="last_build/Settings.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
    if not succ:
        #self.log_output("Failed to download Settings.zip.")
        return False
    
    succ = gitHubDownload.git_extract_folder(silent=True, zip_folder_path = os.path.join(download_path, "Settings.zip"), desired_folder_path=folderName)
    
    #moving folderName to the correct folder
    #self.log_output(f"Moving Character Files to {installPath}/DM Assistant/Settings/Characters ...")
    source_char_folder = os.path.join(download_path, folderName)
    dest_char_folder = os.path.join(installPath, folderName)
    try:
        if os.path.exists(dest_char_folder):
            reply = QMessageBox.question(None, "Confirm Installation", f"A {folderName} folder already exists. Do you wish to overide it? All files with matching names in the folder will be replaced", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return False    #they cancelled the overwrite, so return false

            #remove the exisiting files with the same names
            # Walk through every directory under source_char_folder (recursively)
            # root  = the current folder path being visited
            # dirs  = a list of subfolder names inside root (you can modify this list to control traversal)
            # files = a list of file names inside root
            for root, dirs, files in os.walk(source_char_folder):

                # Compute the path of the current folder (root) *relative* to the source base folder.
                rel_root = os.path.relpath(root, source_char_folder)

                # Decide the destination folder that corresponds to this source folder:
                # - If rel_root == ".", we are at the top of the source folder, so target_root is dest_char_folder
                # - Otherwise, we append the relative subfolder path so the structure is preserved
                #   Example: rel_root = "SubA" -> target_root = "<dest_char_folder>/SubA"
                target_root = dest_char_folder if rel_root == "." else os.path.join(dest_char_folder, rel_root)

                # Ensure the destination folder for this level exists.
                # exist_ok=True prevents an error if the folder already exists.
                os.makedirs(target_root, exist_ok=True)

                # Loop over every file name found in the current source folder (root)
                for filename in files:

                    # Build the full path to the source file:
                    # Example: src_file = "<root>/<filename>"
                    src_file = os.path.join(root, filename)

                    # Build the full path to the destination file:
                    # Example: dst_file = "<target_root>/<filename>"
                    dst_file = os.path.join(target_root, filename)

                    # Copy the file from source to destination:
                    # - Overwrites dst_file if it already exists (this is the default behavior)
                    # - copy2() also attempts to preserve metadata (modified time, permissions, etc.)
                    shutil.copy2(src_file, dst_file)
        
        else:
            shutil.move(source_char_folder, dest_char_folder)
        #self.log_output("Character files installed successfully.")
        return True
    except Exception as e:
        #self.log_output(f"Failed to move character files: {e}")
        return False

def downloadAndInstallProgram(installPath = ""):
    """
    @brief Download the program from GitHub and install it to the specified path.
    @param installPath The path to install the program to.
    """
    gitHubDownload = GitHubDownloader()
    download_path = os.path.join(tempfile.gettempdir(), "DM-Program")
    
    succ = gitHubDownload.git_download_file_qt(file="last_build/DM_Assistant.zip", outputPath=download_path) #store in the system temp folder (C:\Users\YourUser\AppData\Local\Temp\DM-Program)
    if not succ:
        #self.log_output("Failed to download program. Installation aborted.")
        return False
    #self.log_output("Files downloaded successfully.")
        
    #self.log_output(f"Moving zip to installation directory {installPath}")
    #move the last_build folder to the selected installation directory
    source_folder = download_path
    try:
        if os.path.exists(os.path.join(installPath, "DM Assistant", "DM Assistant.exe")) or os.path.exists(os.path.join(installPath, "DM Assistant", "_internal")):
            reply = QMessageBox.question(None, "Confirm Installation", "An installation already exists in this folder. Do you wish to overide it? Other data such as save files will be preserved", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # Remove only the executable and internal folder to preserve user data
                remove_from_directory(os.path.join(installPath, "DM Assistant"), ["DM Assistant.exe", "_internal"])
            else:
                #self.log_output("Installation cancelled.")
                return False
        shutil.move(os.path.join(source_folder, "DM_Assistant.zip"), installPath)
    except Exception as e:
        #self.log_output(f"Failed to install files: {e}")
        return False
    
    output_zip_path = os.path.join(installPath, "DM_Assistant.zip")
    if output_zip_path.__contains__("\\"):
            output_zip_path = output_zip_path.replace("\\", "/")
    #print(f"Extracting files: {output_zip_path}")
    #extract the .zip file in the installation directory
    try:
        shutil.unpack_archive(output_zip_path, installPath)
    except Exception as e:
        #self.log_output(f"Failed to extract zip file: {e}")
        return False
    os.remove(output_zip_path)  #remove the .zip file after extraction
    return True

def remove_from_directory(directory, items_to_remove):
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
                    #self.log_output(f"Removed folder: {item}")
                else:
                    os.remove(item_path)
                    #self.log_output(f"Removed file: {item}")
            except Exception as e:
                #self.log_output(f"Warning: Could not remove {item}: {e}")
                pass
        
#**************************Main Function***********************************
if __name__ == "__main__":
    # On Windows, set an explicit AppUserModelID so taskbar uses your app identity.
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.mycompany.dmassistant")
        except Exception:
            pass
    
    
    app = QApplication(sys.argv)
    
    #two options for getting the icon path, one for when its compiled to an exe and one for when its run from source
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)
    icon_path = os.path.join(base, "exe_generation", "dnd_dm_installer_icon.ico")
    
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()

    app.exec()