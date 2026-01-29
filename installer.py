"""
Installer script for the DM Assistant application.
This script is used to generate a simple installer.
The installer downloads the output folder from GitHub and places it in the specified installation directory.
"""
from PyQt6.QtWidgets import QProgressDialog, QScrollArea, QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QSizePolicy, QMessageBox, QComboBox, QCheckBox, QSplitter, QGridLayout, QListWidget, QTextEdit, QHeaderView  # Import QMessageBox for dialog boxes
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QColor, QBrush, QKeySequence, QShortcut, QPalette, QLinearGradient, QFontDatabase  # Import QFont for text formatting, QColor for setting cell background color, and QBrush for setting cell background color
import sys
import os  # Import os for file path handling
import xml.etree.ElementTree as ET  # Import the XML parsing module
import html
from bs4 import BeautifulSoup
import shutil  # Import shutil for file operations
import urllib.request  # Import urllib for downloading files from GitHub

from PyQt6.QtWidgets import QFileDialog  # Import QFileDialog for file selection
import csv  # Import CSV module for reading and writing CSV files
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QColorDialog, QLineEdit

from characterSelection import CharacterSelectionWindow  # Import the character selection window
from diceRoller import DiceRollerWindow  # Import the dice roller window
from characterSheet import CharacterSheetWindow  # Import the character sheet window

from rowdata import CharacterRow, ColumnNames  # Import the CharacterRow class for handling character data

import rowDataFileIO as CFIO  # Import the file I/O functions for character data

from settingsAndStyle import StyleInfo, Settings # Import the function to set the custom style sheet information
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
        self.checkbox_characters = QCheckBox("Download Characters")
        self.checkbox_characters.setChecked(True)
        #self.checkbox_characters.stateChanged.connect(self.on_characters_checkbox_changed)
        
        self.checkbox_conditions = QCheckBox("Download Condition Spell Effects")
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
        gitHubDownload = GitHubDownloader()
        
        self.log_output("Starting Installation...")
        self.log_output("Downloading files from GitHub...")
        succ = gitHubDownload.git_download_repo() #download the repo from github 
        if not succ:
            self.log_output("Failed to download files from GitHub. Installation aborted.")
            return
        else:
            self.log_output("Files downloaded successfully.")
        
        # if self.checkbox_characters.isChecked():
        #     self.log_output("Downloading characters...")
        #     # TODO: Add download characters logic here
        
        # if self.checkbox_conditions.isChecked():
        #     self.log_output("Downloading condition/spell effects...")
        #     # TODO: Add download condition/spell effects logic here
        
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
        
#**************************Events**********************************************
    def closeEvent(self, event):
        """
        @brief Ask if the user wants to save before closing.
        @param event The close event.
        """
        #delete the temp folder and all its contents if it exists
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
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