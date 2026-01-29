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
        
        #create the folder structure if it does not already exist
        os.makedirs("Settings/Condition_Spell_Effects", exist_ok=True)
        os.makedirs("Settings/Characters", exist_ok=True)
        os.makedirs("Save Files", exist_ok=True)

        #version number of the application
        self.version = self.readversionnumber() #read the version number from the version.txt file
        
        #github variables
        self.github_downloader = GitHubDownloader()  # Create an instance of the GitHubDownloader class

        self.process_damage_flag = True # Flag to control if damage applied
        self.default_condit_file_name = "DnD_2024.xml"
        self.condtions_spellEffect_file_path = f"Settings/Condition_Spell_Effects/{self.default_condit_file_name}"  # Path to the XML file for conditions and spell effects
        self.conditions_file_error = False  # Flag to track if there was an error loading the conditions file so we only try to download once per session it once
        self.file_path = ""  # Initialize file_path to an empty string. Used to store where the file is saved if the save button is used         
        self.rows: list[CharacterRow] = []      #create a list of objects to store all row data
        self.character_sheet_row_ID = 4  # store the index we are going to use for the character sheet
        self.character_sheet_window = None
        
        self.setWindowTitle("DM Assistant")  # Set the window title
        self.setGeometry(100, 100, 1000, 400)  # Set window size
        
        self.style_sheet = StyleInfo()      #object for storing and recalling the style sheet information
        self.settings = Settings()          #object for storing and recalling the general settings
        
        # Create a menu bar
        menu_bar = self.menuBar()

        # Add "File" menu
        file_menu = menu_bar.addMenu("File")

        # Add actions to the "File" menu
        file_menu.addAction("New", self.new_action)  # New action resets the table to default values
        file_menu.addAction("Open", self.open_action)  # Open action calls the open_table_data method
        file_menu.addAction("Save", self.save_action)  # Save action calls the save_table_data method
        file_menu.addAction("Save As", self.save_as_action)  # Save action calls the save_table_data method
        file_menu.addAction("Exit", self.exit_action)  # Exit action closes the application
        file_menu.addAction("Download Repo", self.download_repo_action)  # Exit action closes the application
        
        # Add "View" menu
        view_menu = menu_bar.addMenu("View")

        # Add actions to the "View" menu
        view_menu.addAction("Hide/Show Columns", self.hide_columns_action)
        view_menu.addAction("Toggle Fullscreen", self.toggle_fullscreen)
        view_menu.addAction("Reset Layout", self.reset_layout)
        
        preference_menu = menu_bar.addMenu("Preferences")
        preference_menu.addAction("Options", self.options_action)  # Add action to set highlight colors
        # Create the submenu
        conditions_menu = preference_menu.addMenu("Conditions and Spell Effects")

        # Add actions to the submenu
        conditions_menu.addAction("Select File", self.select_conditions_file)
        conditions_menu.addAction("Modify Conditions/Spell Effects", self.modify_conditions_spell_effects)
        
        self.columns = {name: idx for idx, name in enumerate(ColumnNames)}
        
        #Add the buttons to end of the table
        self.rows.append(CharacterRow(is_button="Add Default Row"))  # Add a default row for the "Add Row" button
        self.rows.append(CharacterRow(is_button="Add Characters"))  # Add a default row for the "Add Characters" button
        
        #add the help menue
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.about_menue_action)  # Add action to show the about dialog
        
        self.previous_values = {}  # Store previous values for validation
        
        self.validate_error = False  # Flag to track if there was a validation error. Needed as the function can run twice when the values are set back so we dont do things like change HP
        
        # Dynamically set the total number of columns based on the headers
        self.total_columns = len(self.columns)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Use QSplitter for vertical alignment of the table and buttons
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a QTableWidget for the table
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(200)
        self.table.setMinimumWidth(750)
        
        # Wrap the table in a scroll area to enable scrolling when needed
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidget(self.table)
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        splitter.addWidget(table_scroll_area)

        # Create a QWidget for the buttons
        button_widget = QWidget()
        button_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button_widget.setMinimumHeight(100)
        button_layout = QGridLayout(button_widget)

        # Add the "Next Turn" button to the button layout
        self.next_turn_button = QPushButton("Next Turn")
        button_layout.addWidget(self.next_turn_button, 0, 0)
        self.next_turn_button.clicked.connect(self.next_turn)

        # Add the "Roll Initiative" button above the "Sort Initiative" button
        self.roll_initiative_button = QPushButton("Roll Initiative")
        button_layout.addWidget(self.roll_initiative_button, 0, 1)  # Insert at position 1 (above Sort Initiative)
        self.roll_initiative_button.clicked.connect(self.roll_initiative)

        # Add the "Sort Initiative" button to the button layout
        self.sort_initiative_button = QPushButton("Sort Initiative")
        button_layout.addWidget(self.sort_initiative_button, 1, 1)
        self.sort_initiative_button.clicked.connect(self.sort_initiative)

        # Add the "Finish Combat" button to the button layout
        self.finish_combat_button = QPushButton("Finish Combat")
        button_layout.addWidget(self.finish_combat_button, 0, 2)
        self.finish_combat_button.clicked.connect(self.finish_combat)

        # Add the "Reset HP" button to the button layout
        self.reset_hp_button = QPushButton("Reset HP")
        button_layout.addWidget(self.reset_hp_button, 1, 2)
        self.reset_hp_button.clicked.connect(self.reset_all_hp)

        # Add the "Dice Roller" button to the button layout
        self.dice_roller_button = QPushButton("Dice Roller")
        button_layout.addWidget(self.dice_roller_button, 0, 3)
        self.dice_roller_button.clicked.connect(self.open_dice_roller)
        
        # Add the "character sheet" button to the button layout
        self.character_sheet_button = QPushButton("Character Sheet")
        button_layout.addWidget(self.character_sheet_button, 1, 3)
        self.character_sheet_button.clicked.connect(self.open_character_sheet)

        # Add a spacer to push the buttons to the top
        #button_layout.addStretch()

        # Add the button widget to the splitter
        splitter.addWidget(button_widget)

        # Set the stretch factors: 4 for the table (80%) and 1 for the buttons (20%)
        splitter.setStretchFactor(0, 4)  # Index 0 corresponds to the table
        splitter.setStretchFactor(1, 1)  # Index 1 corresponds to the buttons

        # Set the initial sizes: 80% for the table and 20% for the buttons
        splitter.setSizes([800, 200])  # Adjust these values as needed for your window size

        # Prevent the buttons from expanding when the table shrinks
        splitter.setChildrenCollapsible(False)

        # Set the splitter as the layout for the central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(splitter)

        # Set the number of columns and their headers
        self.table.setColumnCount(len(ColumnNames))
        self.table.setHorizontalHeaderLabels(ColumnNames)  # Use the first row as headers

        # Make the header text bold and center-aligned
        for col in range(self.total_columns):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item:
                # Make the text bold
                font = QFont()
                font.setBold(True)
                header_item.setFont(font)

                # Center the text
                header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Make columns stretch to fill available horizontal space
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Make rows stretch to fill available vertical space
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Create 7 rows as default (5 + 2 for the "Add Row" and "Add Character" button)
        self.table.setRowCount(7)
        
        self.table.verticalHeader().setMinimumSectionSize(30)  # Set minimum row height
        self.table.horizontalHeader().setMinimumSectionSize(80)  # Set minimum row width

        # Populate the first 5 rows with default data
        for row in range(5):
            character_temp = CharacterRow()  # Create a new CharacterRow instance
            character_temp._set_generic()  # Set generic values for the character
            self.generate_row(row, character_temp)  # Generate the row with default data

        # Add the "Add Row" button to the last row
        self.add_row_button = QPushButton("Add Default Row")
        self.table.setCellWidget(5, 0, self.add_row_button)  # Place the button in the first column of the last row
        self.table.setSpan(5, 0, 1, self.total_columns)  # Span the button across all data columns
        
        # Connect the "Add Row" button to the add_row method
        self.add_row_button.clicked.connect(self.add_row_blank)
        
        # Add the "Add Row" button to the last row
        self.add_character_button = QPushButton("Add Character(s)")
        self.table.setCellWidget(6, 0, self.add_character_button)  # Place the button in the first column of the last row
        self.table.setSpan(6, 0, 1, self.total_columns)  # Span the button across all data columns

        # Connect the "Add Character" button to the add_character method
        self.add_character_button.clicked.connect(self.add_character)

        # Highlight the first non-header row
        self.highlight_row(0)

        # Connect the cellChanged signal to validate cell content
        self.table.cellChanged.connect(self.cell_content_signal)
        self.table.itemSelectionChanged.connect(self.item_slec_chang_sig)  # Connect to item selection changed instead of cell changed
        
        #Set the layout to the default state
        self.reset_layout()

#**************************Functions***********************************
    def readversionnumber(self):
            """Read the version number from the version.txt file."""
            version_file_path = readVersionNumber() #read the version number from the version.txt file
            if version_file_path == "Unknown Version":
                QMessageBox.warning(
                self,
                "Invalid Input",
                f"Could not find version file at {version_file_path}"
                )
            else:
                return version_file_path

    def validate_cell_content(self, row, col):
        """
        @brief Validate the content of a cell and process it if valid.
        @param row The row index of the cell.
        @param col The column index of the cell.
        @return True if there is a validation error, False otherwise.
        """
        
        skip_validation_columns = {
            "Player Name",
            "Character Name",
            "Conditions/Spell Effects",
            "Select",
            "Background",
            "Class",
            "Species",
            "Subclass",
            "Hit Dice",
            "Size",
            "Saving Throws",
            "Damage Resistance",
            "Languages",
            "Challenge Rating",
            "Special Equipment",
            "Speical Abilities",
            "Spells",
            "Speed",
            "Actions",
            "Reactions",
            "Legendary Actions",
            "Equipment",
            "Special Abilities",
            "Spell Slots",
            "Feats",
            "Bonus Actions",
            "X"
        }
        skip_indices = {self.columns[name] for name in skip_validation_columns if name in self.columns}
        
        # Get the item at the specified row and column
        item = self.table.item(row, col)
        
        #skip if we are in a row that does not have a data, such as the "Add Row" button row
        if row == self.table.rowCount() - 1 or row == self.table.rowCount() - 2:
            return
        
        # Skip validation for any non-numeric columns (e.g., "Player Name", "Character Name", "Conditions/Spell Effects")
        #if col == self.columns["Player Name"] or col == self.columns["Character Name"] or col == self.columns["Conditions/Spell Effects"] or col == self.columns["Select"] or col == self.columns["X"]:
            #return  # validation not needed for these columns
        if col in skip_indices:
                return  # validation not needed for these columns
        
        # Check if the value is a valid integer
        if not self.is_integer(item.text()):
            # Show a dialog box for invalid input
            
            QMessageBox.warning(
                self,
                "Invalid Input",
                f"Invalid value entered in row: {row + 1}, column: {ColumnNames[col]}. "
                "Please only enter valid integers."
            )

            # Revert to the previous value if the text is not a valid integer
            previous_value = self.previous_values.get((row, col), "")
            item.setText(str(previous_value))
            return True
        else:
            # Update the previous value if the text is valid
            self.previous_values[(row, col)] = item.text()
            return False

    def add_row(self, character_data: CharacterRow, add_to_rows = True):
        """
        @brief Add a new row to the table above the 'Add Row' button.
        @param character_data The CharacterRow data to populate the new row.
        @param add_to_rows Flag to indicate if the character should be added to the rows list.
        """
        #exit if no character data is provided
        if character_data is None:
            return
        
        #Remove the signals to check valid data as we are entering it
        self.table.cellChanged.disconnect(self.cell_content_signal)
        
        #the last two rows are button rows. So add the row just above the button row
        last_data_row = self.table.rowCount() - 2 
        
        self.table.insertRow(last_data_row)  # Insert a new row before the "Add Row" button
        self.generate_row(last_data_row, character_data, add_to_rows)  # Generate the new row
        self.update_condition_tooltip(last_data_row)      # Update the tooltip for the conditions/spell effects column
        
        self.table.cellChanged.connect(self.cell_content_signal)

    def delete_row(self, row_index, delete_character = True):
        """
        @brief Delete a specific row form the table
        @param index of the row to be deleated
        @param delete_character Flag to indicate if the character should be deleted from the rows list.
        """
        # Explicitly set focus back to the table widget. This removes the view randomly shifting as a row is deleated
        self.table.setFocus(Qt.FocusReason.OtherFocusReason)
        
        #if row_index == self.table.rowCount() - 2:  # Prevent deleting the "Add Row" and "Add Character" button row
        #    return
        
        row_char_id = int(self.table.item(row_index, self.columns["Character ID"]).text()) #get the character ID for this row
        #cycle through all the row objects
        for row in self.rows:
            if row.Character_ID == row_char_id:
                #if the row is not a button
                if row.is_button == "":
                    #do we want to remove the character from the list of row objects as well?
                    if delete_character:
                        self.rows.remove(row)  # Remove the corresponding CharacterRow instance
                    self.table.removeRow(row_index) #remove the row from the table
                break
    
    def delete_row_character(self, character = CharacterRow(), delete_character = True):
        """
        @brief Delete a specific row form the table by character ID
        @param character_id The ID of the character to be deleted.
        @param delete_character Flag to indicate if the character should be deleted from the rows list.
        """
        #return if a button is sent
        if character.is_button != "":
            return
        
        #cycle through all the rows in the table
        for row_index in range(self.table.rowCount()):
            char_id_item = self.table.item(row_index, self.columns["Character ID"]) #get the character ID for this row
            #if we could get a character ID
            if char_id_item is not None:
                #if this row matches the given character ID
                if character.Character_ID == int(char_id_item.text()):
                    self.delete_row(row_index, delete_character) #delete this row
                    break
    
    def update_entire_table_column(self, column_name = ""):
        """
        @breif Update a specific column in the table for all characters
        @param column_name The name of the column to update.
        """
        if column_name not in self.columns:
            return  # Invalid column name
        else:
            #for every row object
            for row_obj in self.rows:
                # if the row is not a button row
                if row_obj.is_button == "":
                    self.update_single_table_column(column_name, row_obj) #update the specific column for this row object
                    
    def update_single_table_column(self, column_name = "", char = CharacterRow()):
        """
        @breif Update a specific column in the table for one characters 
        @param column_name The name of the column to update.
        @param char The character qho is being updated
        """
        for row_index in range(self.table.rowCount() - 2):
                char_id_item = self.table.item(row_index, self.columns["Character ID"]) #get the character ID for this row
                #if this row matches the object's character ID
                if char.Character_ID == int(char_id_item.text()):
                    #for the initiative column, update it from the object
                    if column_name == "Initiative":
                        item = self.table.item(row_index, self.columns["Initiative"])
                        if item:
                            item.setText(str(char.Initiative))
                    #for the initiative column, update it from the object
                    if column_name == "Damage":
                        item = self.table.item(row_index, self.columns["Damage"])
                        if item:
                            item.setText(str(char.Damage))
                    #for the initiative column, update it from the object
                    if column_name == "Current HP":
                        item = self.table.item(row_index, self.columns["Current HP"])
                        if item:
                            item.setText(str(char.Current_HP))
                    #for the initiative column, update it from the object
                    if column_name == "Temp. HP":
                        item = self.table.item(row_index, self.columns["Temp. HP"])
                        if item:
                            item.setText(str(char.Temporary_Hit_Points))
                    #for the initiative column, update it from the object
                    if column_name == "Max HP":
                        item = self.table.item(row_index, self.columns["Max HP"])
                        if item:
                            item.setText(str(char.Max_HP))
                    #for the initiative column, update it from the object
                    if column_name == "Armor Class":
                        item = self.table.item(row_index, self.columns["Armor Class"])
                        if item:
                            item.setText(str(char.Armor_Class))
                    #for the initiative column, update it from the object
                    if column_name == "Character Name":
                        item = self.table.item(row_index, self.columns["Character Name"])
                        if item:
                            item.setText(str(char.Character_Name))
                    #for the initiative column, update it from the object
                    if column_name == "Player Name":
                        item = self.table.item(row_index, self.columns["Player Name"])
                        if item:
                            item.setText(str(char.Player_Name))
                    if column_name == "Conditions/Spell Effects":
                        item = self.table.item(row_index, self.columns["Conditions/Spell Effects"])
                        if item:
                            item.setText(str(char.Conditions_Spell_Effects))
                    break
        
    def highlight_row(self, row_index):
        """
        @brief Highlight a specific row with the current turn highlight color.
        @param row_index The index of the row to highlight.
        """
        for col in range(self.total_columns):
            item = self.table.item(row_index, col)
            if not item:
                # Ensure the cell has a QTableWidgetItem
                item = QTableWidgetItem("")
                self.table.setItem(row_index, col, item)
            #only set the background if the item does not have a background already
            if item.background().color() != QColor(self.style_sheet.colour_full_hp) and item.background().color() != QColor(self.style_sheet.colour_critical_hp) and item.background().color() != QColor(self.style_sheet.colour_no_hp):
                #set the background to the current turn highlight colour
                item.setBackground(QBrush(QColor(self.style_sheet.colour_current_turn)))  # Use QBrush to set the background color

    def clear_highlight(self, row_index):
        """
        @brief Clear the highlight from a specific row.
        @param row_index The index of the row to clear.
        """
        for col in range(self.total_columns):
            item = self.table.item(row_index, col)
            if not item:
                # Ensure the cell has a QTableWidgetItem
                item = QTableWidgetItem("")
                self.table.setItem(row_index, col, item)
            item.setBackground(QBrush(QColor("transparent")))  # Use QBrush to reset the background color

    def clear_highlighted_row(self, colour):
        """
        @brief Find the highlighted row and clear it.
        @param colour The color used to identify the highlighted row.
        @return The index of the cleared row, or -1 if not found.
        """
        current_row = -1
        current_row = self.find_highlighted_row(colour)
        #if no row could be found, return
        if current_row == -1:
            return -1

        # Clear the highlight from the current row
        if current_row != -1:
            self.clear_highlight(current_row)
    
        return current_row
    
    def find_highlighted_row(self, colour):
        """
        @brief Find the currently highlighted row.
        @param colour The color used to identify the highlighted row.
        @return The index of the highlighted row, or -1 if not found.
        """
        current_row = -1
        # Find the currently highlighted row
        for row in range(self.table.rowCount() - 1):  # Exclude the "Add Row" button row
            item = self.table.item(row, 0)
            if item and item.background().color() == QColor(colour):
                current_row = row
                break
        return current_row

    def add_delete_button(self, row):
        """
        @brief Add a delete button to the specified row.
        @param row The index of the row to add the button to.
        """
        delete_button = QPushButton("X")
        delete_button.setStyleSheet(
            "color: red; font-weight: bold; border: none; padding: 0;"
        )  # Make the "X" red, remove borders, and remove padding
        delete_button.clicked.connect(lambda: self.delete_row_button(delete_button))

        # Set the button to fill the entire cell
        delete_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Set the button as the cell widget
        self.table.setCellWidget(row, self.columns["X"], delete_button)

        # Ensure the background of the last column is transparent
        transparent_item = QTableWidgetItem()
        transparent_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-editable
        transparent_item.setBackground(Qt.GlobalColor.transparent)  # Set transparent background
        self.table.setItem(row, self.columns["X"], transparent_item)

    def delete_row_button(self, button):
        """
        @brief Delete the row containing the specified button.
        @param button The QPushButton instance that was clicked.
        """
        # Explicitly set focus back to the table widget. This removes the view randomly shifting as a row is deleated
        self.table.setFocus(Qt.FocusReason.OtherFocusReason)
        
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, self.columns["X"]) == button:
                self.delete_row(row)
                break
            
    def add_dropdown(self, row_index):
        """
        @brief Add a dropdown box to the unnamed column in the specified row.
        @param row_index The index of the row to add the dropdown to.
        """
        dropdown = QComboBox()
        dropdown.addItem("")  # add a blank iteam

        if not self.conditions_file_error:
            #check to see if the file exists before we continue
            if not os.path.isfile(self.condtions_spellEffect_file_path):
                message = f"Failed to load default conditions and spell effects file {self.default_condit_file_name}. Do you want to download the file from GitHub?"
                reply = QMessageBox.question(None, "File Not Found", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    error = self.github_downloader.githiub_download_file(self.condtions_spellEffect_file_path) #try to download the file from github
                    #if there was an error downloading the file
                    if error == True:
                        self.conditions_file_error = True
                else:
                    self.conditions_file_error = True
            
            # Load items and descriptions from the XML file if there was no error
            if self.conditions_file_error != True:
                try:
                    tree = ET.parse(self.condtions_spellEffect_file_path)  # Parse the XML file
                    root = tree.getroot()

                    for condition in root.findall("condition"):
                        name = condition.find("name").text  # Get the <name> tag
                        description = condition.find("description").text  # Get the <description> tag
                        dropdown.addItem(name)  # Add the name to the dropdown
                        dropdown.setItemData(dropdown.count() - 1, description, Qt.ItemDataRole.ToolTipRole)  # Set the tooltip
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load dropdown items: {e}")

        # Connect the dropdown selection to update the "Condition/Spell Effects" column
        dropdown.currentTextChanged.connect(lambda text, row=row_index: self.update_condition_spell_effects(row, text))

        # Set the dropdown as the cell widget
        self.table.setCellWidget(row_index, self.columns["Select"], dropdown)
        
    def update_condition_spell_effects(self, row_index, selected_text):
        """
        @brief Update the 'Condition/Spell Effects' column with the selected dropdown value.
        Also sets tooltips for each condition in the cell.
        @param row_index The index of the row to update.
        @param selected_text The text selected from the dropdown.
        """
        condition_item = self.table.item(row_index, self.columns["Conditions/Spell Effects"])
        if not condition_item:
            condition_item = QTableWidgetItem("")
            self.table.setItem(row_index, self.columns["Conditions/Spell Effects"], condition_item)

        # Append the selected text to the existing text
        current_text = condition_item.text()
        if selected_text and selected_text not in current_text:
            if current_text:
                condition_item.setText(f"{current_text}, {selected_text}")
            else:
                condition_item.setText(selected_text)

        # --- Update tooltip using the shared function ---
        self.update_condition_tooltip(row_index)

        # Reset the combo box to the first item
        combo_box = self.table.cellWidget(row_index, self.columns["Select"])
        if isinstance(combo_box, QComboBox):
            combo_box.setCurrentIndex(0)
    
    def update_condition_tooltip(self, row_index):
        """
        @brief Update the tooltip for the 'Conditions/Spell Effects' cell at the given row.
        @param row_index The index of the row to update.
        """
        condition_item = self.table.item(row_index, self.columns["Conditions/Spell Effects"])
        if not condition_item:
            return

        # Load all condition descriptions from XML
        try:
            tree = ET.parse(self.condtions_spellEffect_file_path)
            root = tree.getroot()
            desc_map = {}
            for condition in root.findall("condition"):
                name = condition.find("name").text
                description = condition.find("description").text
                desc_map[name] = description
        except Exception as e:
            desc_map = {}

        # Build tooltip text for all conditions in the cell
        tooltip = ""
        for cond in [c.strip() for c in condition_item.text().split(",") if c.strip()]:
            desc = desc_map.get(cond, "")
            tooltip += f"<b>{cond}</b>: {desc}<br>" if desc else f"<b>{cond}</b><br>"
            tooltip += "<br/>"  # Add extra space between conditions
        condition_item.setToolTip(tooltip.strip())

    def generate_row(self, row_index, character_data: CharacterRow, add_to_Rows = True):
        """
        @brief Generate a new row with default data and an 'X' button.
        @param row_index The index at which to generate the new row.
        @param character_data A CharacterRow instance containing the data for the row.
        """
        
        #if an empty character_data is passed, we will not generate a row as there is no data
        if character_data is None:
            return
        
        lastRow = 0
        #cycle through the rows to find the last row that is not a button
        for curr_row in self.rows:
            if curr_row.is_button == "":
                lastRow = lastRow + 1
            else:
                break
        
        if add_to_Rows:
            self.rows.insert(lastRow, character_data)  #add this row to the row index
        #self.rows.insert(lastRow, character_data)
        
        for col, col_name in enumerate(ColumnNames):
            item = self.table.item(row_index, col)
            #the speed is treated differently as it is made up of multiple fields
            if col_name == "Speed":
                    speedString = ""
                    #set the speed bassed on what is available from the user
                    if character_data.Walk_Speed != 0:
                        speedString += f"Walk: {character_data.Walk_Speed}ft, "
                    if character_data.Fly_Speed != 0:
                        speedString += f"Fly: {character_data.Fly_Speed}ft, "
                    if character_data.Swim_Speed != 0:
                        speedString += f"Swim: {character_data.Swim_Speed}ft, "
                    if character_data.Climb_Speed != 0:
                        speedString += f"Climb: {character_data.Climb_Speed}ft, "
                    if character_data.Burrow_Speed != 0:
                        speedString += f"Burrow: {character_data.Burrow_Speed}ft, "
                    speedString = speedString.rstrip(", ")  # Remove the trailing comma and space
                    if not item:
                        item = QTableWidgetItem(speedString)
                        self.table.setItem(row_index, col, item)
            elif col_name == "Temp. HP":
                value = character_data.Temporary_Hit_Points
                if not item:
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_index, col, item)
                else:
                    item.setText(str(value))
            else:
                # Replace spaces and special characters with underscores to match dataclass field names
                attr_name = col_name.replace(" ", "_").replace("/", "_").replace("-", "_")
                value = getattr(character_data, attr_name, "")
                if not item:
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_index, col, item)
                else:
                    item.setText(value)
            # Store the initial value in the previous_values dictionary
            self.previous_values[(row_index, col)] = value
        
        #ADD IN SOME SPECIFIC VALUES> FOR EXAMPLE, THE SPEED COLUMS DOES NOT MATCH
        
        self.add_dropdown(row_index)        # Add a dropdown box to the unnamed column
        self.add_delete_button(row_index)  # Add the "X" button to the last column
        self.HP_Highlighting(row_index)  # Highlight the HP cell based on the initial values
    
    def process_damage(self, row, character_id):
        """
        @brief Process the damage value entered in the Damage column for a specific character.
        @param row The row index in the table.
        @param character_id The unique Character_ID of the row object.
        """
        
        # Find the CharacterRow object with this Character_ID if it exists
        target_row_obj = None
        if character_id is not None:
            for obj in self.rows:
                if hasattr(obj, "Character_ID") and obj.Character_ID == character_id and getattr(obj, "is_button", "") == "":
                    target_row_obj = obj
                    break
        
        #If we could not find the row object, return
        if target_row_obj is None:
            return
        
        """If damage should be processed"""
        if self.process_damage_flag:
            """Process the damage value entered in the Damage column."""
            # Get the current Temporary HP and Current HP values
            damage_item = self.table.item(row, self.columns["Damage"])
            temp_hp_item = self.table.item(row, self.columns["Temp. HP"])
            current_hp_item = self.table.item(row, self.columns["Current HP"])
            #damage = int(damage_item.text()) if damage_item and self.is_integer(damage_item.text()) else 0
            #temp_hp = int(temp_hp_item.text()) if temp_hp_item and self.is_integer(temp_hp_item.text()) else 0
            #current_hp = int(current_hp_item.text()) if current_hp_item and self.is_integer(current_hp_item.text()) else 0
            damage = target_row_obj.Damage
            temp_hp = target_row_obj.Temporary_Hit_Points
            current_hp = target_row_obj.Current_HP
            
            #if they are doing damage (ie the damage is positive)
            if damage > 0:
                # Apply damage to Temporary HP first
                temp_hp -= damage
                if temp_hp < 0:
                    # If Temporary HP is depleted, apply the remaining damage to Current HP
                    current_hp += temp_hp  # temp_hp is negative, so this subtracts the remaining damage
                    temp_hp = 0
            else:
                # If damage is negative (healing), add the healing effect (minus as the damge is negative)
                current_hp -= damage
                #make sure we do not go above max HP
                max_hp = target_row_obj.Max_HP
                if current_hp > max_hp:
                    current_hp = max_hp

            # Update the Temporary HP and Current HP cells
            if temp_hp_item:
                temp_hp_item.setText(str(temp_hp))  #Update the cell text
                target_row_obj.Temporary_Hit_Points = temp_hp  # Update the Temporary HP in the CharacterRow object
            if current_hp_item:
                current_hp_item.setText(str(current_hp))    #update the cell
                target_row_obj.Current_HP = current_hp      # Update the Current HP in the CharacterRow object
            
            self.HP_Highlighting(row)  # Highlight the HP cell based on the updated values
        
    def HP_Highlighting(self, row):
        """
        @brief Highlight the HP cell based on its value.
        @param row The row index to highlight.
        """
        curr_hp = int(self.table.item(row, self.columns["Current HP"]).text())
        #Get the valid HP values
        max_hp = int(self.table.item(row, self.columns["Max HP"]).text())
        
        val = 0.5 * float(max_hp)
        
        if (curr_hp > 0.5 * float(max_hp)):
            # Highlight the cell with green if HP is above 50%
            self.table.item(row, self.columns["Current HP"]).setBackground(QBrush(QColor(self.style_sheet.colour_full_hp)))
        elif (curr_hp > 0):
            # Highlight the cell with orange if HP is above 0 but below 50%
            self.table.item(row, self.columns["Current HP"]).setBackground(QBrush(QColor(self.style_sheet.colour_critical_hp)))
        else:
            # Highlight the cell with red if HP is 0 or below
            self.table.item(row, self.columns["Current HP"]).setBackground(QBrush(QColor(self.style_sheet.colour_no_hp)))

    def is_integer(self, string):
        """
        @brief Check if a string is a valid integer (positive or negative).
        @param string The string to check.
        @return True if the string is a valid integer, False otherwise.
        """
        if string.startswith('-'):  # Check if the string starts with a negative sign
            return string[1:].isdigit()  # Check if the rest of the string is digits
        return string.isdigit()  # Check if the string is all digits for positive numbers
 
    def save_data_to_xml(self):
        """
        @brief Save all CharacterRow objects in self.rows to an XML file matching the Custom.xml layout.
        Also saves row order, selected colours, and visible columns.
        """
        import xml.etree.ElementTree as ET

        #delete the existing file so we start fresh
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        
        #create a new file with the correct root elements 
        root = ET.Element("Saved_file")
        settings_elem = ET.SubElement(root, "settings")     #to store the settings - placholder
        tree = ET.ElementTree(root)
        tree.write(self.file_path, encoding="utf-8", xml_declaration=True)
        
        #write each character too the file
        for char_obj in self.rows:
            #if the row is not a button row, write it to the file
            if char_obj.is_button == "":
                CFIO.write_character_information_to_xml(self.file_path, char_obj, "characters", True)

        #reopen the file to add the settings
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        settings_elem = root.find("settings")   #add to the exisiting settings element
        #if the settings element could not be found (no reason why, but hey) add it
        if settings_elem is None:
            settings_elem = ET.SubElement(root, "settings")
        
        
        #save text size and other information
        general_elm = ET.SubElement(settings_elem, "general_settings")
        #general settings
        ET.SubElement(general_elm, "roll_pc_init").text = str(self.settings.roll_pc_initiative)
        
        
        #save text size and other information
        text_elm = ET.SubElement(settings_elem, "text_settings")
        #text and UI settings
        ET.SubElement(text_elm, "general_text_size").text = str(self.style_sheet.font_general_size)
        ET.SubElement(text_elm, "general_text_style").text = str(self.style_sheet.font_general_style)
        ET.SubElement(text_elm, "button_text_size").text = str(self.style_sheet.font_button_size)
        ET.SubElement(text_elm, "button_text_style").text = str(self.style_sheet.font_button_style)
        ET.SubElement(text_elm, "table_text_size").text = str(self.style_sheet.font_table_size)
        ET.SubElement(text_elm, "table_text_style").text = str(self.style_sheet.font_table_style)
        
        ET.SubElement(text_elm, "general_text_colour").text = str(self.style_sheet.colour_general_text)
        ET.SubElement(text_elm, "button_text_colour").text = str(self.style_sheet.colour_button_text)
        ET.SubElement(text_elm, "table_text_colour").text = str(self.style_sheet.colour_table_text)
        
        ET.SubElement(text_elm, "button_color").text = str(self.style_sheet.colour_button)
        ET.SubElement(text_elm, "general_color").text = str(self.style_sheet.colour_general)
        ET.SubElement(text_elm, "minor_color").text = str(self.style_sheet.colour_minor)
        
        # Save selected colours
        colours_elem = ET.SubElement(settings_elem, "selected_colours")
        ET.SubElement(colours_elem, "currentTurn_highlightColour").text = self.style_sheet.colour_current_turn
        ET.SubElement(colours_elem, "fullHP_highlightColour").text = self.style_sheet.colour_full_hp
        ET.SubElement(colours_elem, "criticalHP_highlightColour").text = self.style_sheet.colour_critical_hp
        ET.SubElement(colours_elem, "noHP_highlightColour").text = self.style_sheet.colour_no_hp

        # Save visible columns
        visible_columns_elem = ET.SubElement(settings_elem, "visible_columns")
        for col in range(self.total_columns):
            if not self.table.isColumnHidden(col):
                ET.SubElement(visible_columns_elem, "column").text = ColumnNames[col]

        #currently highlighted row
        highlighted_row = self.find_highlighted_row(self.style_sheet.colour_current_turn)
        ET.SubElement(settings_elem, "highlighted_row").text = str(highlighted_row)
        
        #save the row order by Character_ID as shown in the table
        row_order_elem = ET.SubElement(settings_elem, "row_order")
        for row in range(self.table.rowCount() - 2):  # Exclude the "Add Row" and "Add Character" button rows
            char_id = None
            #find the character ID for this row
            item = self.table.item(row, self.columns["Character ID"])
            if item and self.is_integer(item.text()):
                char_id = int(item.text())
            if char_id is not None:
                ET.SubElement(row_order_elem, "character_id").text = str(char_id)
        
        # Write the XML to file
        ET.indent(tree, space="  ", level=0)
        tree.write(self.file_path, encoding="utf-8", xml_declaration=True)
    
    def open_from_xml(self):
        """
        @brief Open an XML file and load the character data, row order, colours, and visible columns.
        """
        self.process_damage_flag = False #Reset flag so damage is not calculated
        
        #close the character sheet if it is open and reset it
        if self.character_sheet_window is not None:
            self.character_sheet_window.close()
            self.character_sheet_window = None
        
        # Prompt user for file
        default_path = os.path.dirname(self.file_path) if self.file_path else "./Save Files"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open XML File", default_path, "XML Files (*.xml)")
        if not file_path:
            return

        self.file_path = file_path

        try:
            #try to load the character names from the file
            names = CFIO.load_character_names_xml(file_path, "characters")
            #show an error if no names could be found
            if names is None or len(names) == 0:
                raise Exception("No character names found in the XML file.")
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            settings_elem = root.find("settings")

            # Clear current table and rows
            self.table.setRowCount(0)
            self.rows.clear()
            self.previous_values.clear()
            
            #reset the settings and style sheet to default values
            self.settings.resetSettings()
            self.style_sheet.resetLayout()
            
            #load general settings
            general_elem = settings_elem.find("general_settings")
            if (general_elem is not None):
                #find the settings
                roll_pc_init = general_elem.findtext("roll_pc_init", str(self.settings.roll_pc_initiative))

                #set the settings
                self.settings.roll_pc_initiative = (roll_pc_init.lower() == 'true')
            
            #load text
            text_elem = settings_elem.find("text_settings")
            if (text_elem is not None):
                general_size = text_elem.findtext("general_text_size", str(self.style_sheet.font_general_size))
                general_style = text_elem.findtext("general_text_style", self.style_sheet.font_general_style)
                button_size = text_elem.findtext("button_text_size", str(self.style_sheet.font_button_size))
                button_style = text_elem.findtext("button_text_style", self.style_sheet.font_button_style)
                table_size = text_elem.findtext("table_text_size", str(self.style_sheet.font_table_size))
                table_style = text_elem.findtext("table_text_style", self.style_sheet.font_table_style)
                
                general_text_color = text_elem.findtext("general_text_colour", self.style_sheet.colour_general_text)
                button_text_color = text_elem.findtext("button_text_colour", self.style_sheet.colour_button_text)
                table_text_color = text_elem.findtext("table_text_colour", self.style_sheet.colour_table_text)
                
                general_color = text_elem.findtext("general_color", self.style_sheet.colour_general)
                button_color = text_elem.findtext("button_color", self.style_sheet.colour_button)
                minor_color = text_elem.findtext("minor_color", self.style_sheet.colour_minor)
                
                #set the style sheet values
                self.style_sheet.font_general_size = int(general_size)
                self.style_sheet.font_general_style = general_style
                self.style_sheet.font_button_size = int(button_size)
                self.style_sheet.font_button_style = button_style
                self.style_sheet.font_table_size = int(table_size)
                self.style_sheet.font_table_style = table_style
                self.style_sheet.colour_general = general_color
                self.style_sheet.colour_button = button_color
                self.style_sheet.colour_minor = minor_color
                self.style_sheet.colour_general_text = general_text_color
                self.style_sheet.colour_button_text = button_text_color
                self.style_sheet.colour_table_text = table_text_color
                
                #apply the style sheet
                self.set_Custom_Style_Sheet()
            
            # Load colours
            colours_elem = settings_elem.find("selected_colours")
            if colours_elem is not None:
                self.style_sheet.colour_current_turn = colours_elem.findtext("currentTurn_highlightColour", self.style_sheet.colour_current_turn)
                self.style_sheet.colour_full_hp = colours_elem.findtext("fullHP_highlightColour", self.style_sheet.colour_full_hp)
                self.style_sheet.colour_critical_hp = colours_elem.findtext("criticalHP_highlightColour", self.style_sheet.colour_critical_hp)
                self.style_sheet.colour_no_hp = colours_elem.findtext("noHP_highlightColour", self.style_sheet.colour_no_hp)

            # Load visible columns
            visible_columns_elem = settings_elem.find("visible_columns")
            if visible_columns_elem is not None:
                visible_names = [col.text for col in visible_columns_elem.findall("column")]
                for col, name in enumerate(ColumnNames):
                    self.table.setColumnHidden(col, name not in visible_names)

            # Load row order
            row_order_elem = settings_elem.find("row_order")
            ordered_ids = []
            if row_order_elem is not None:
                for char_id_elem in row_order_elem.findall("character_id"):
                    if char_id_elem.text and char_id_elem.text.isdigit():
                        ordered_ids.append(int(char_id_elem.text))
            
            # Load characters into a temporay list
            temp_rows = []
            for name in names:
                temp_rows.append(CFIO.load_character_information_xml(file_path, name, "characters", True))
            
            # sort the list bassed on the order saved in the xml file
            temp_rows.sort(key=lambda x: ordered_ids.index(x.Character_ID) if x and x.Character_ID in ordered_ids else len(ordered_ids))
            
            # Update the ID counter to prevent collisions with loaded characters when new ones are added
            max_loaded_id = max((row.Character_ID for row in temp_rows if row is not None), default=-1)
            if max_loaded_id >= 0:
                CharacterRow._id_counter = max_loaded_id + 1
            
            # Add button rows at the end
            self.rows.append(CharacterRow(is_button="Add Default Row"))
            self.rows.append(CharacterRow(is_button="Add Characters"))
            self.table.insertRow(self.table.rowCount())
            self.add_row_button = QPushButton("Add Default Row")
            self.table.setCellWidget(self.table.rowCount()-1, 0, self.add_row_button)
            self.table.setSpan(self.table.rowCount()-1, 0, 1, self.total_columns)
            self.add_row_button.clicked.connect(self.add_row_blank)

            self.table.insertRow(self.table.rowCount())
            self.add_character_button = QPushButton("Add Character(s)")
            self.table.setCellWidget(self.table.rowCount()-1, 0, self.add_character_button)
            self.table.setSpan(self.table.rowCount()-1, 0, 1, self.total_columns)
            self.add_character_button.clicked.connect(self.add_character)
            
            #write the rows to the table in the desired order
            for row in temp_rows:
                if row is not None:
                    self.add_row(row)

            self.resize_columns_to_content()
            # Re-highlight rows
            for row in range(self.table.rowCount() - 2):
                self.HP_Highlighting(row)

            # Highlight the previously highlighted row
            highlighted_row_elem = settings_elem.find("highlighted_row")
            highlighted_row = int(highlighted_row_elem.text) if highlighted_row_elem is not None and highlighted_row_elem.text.isdigit() else -1
            if 0 <= highlighted_row < self.table.rowCount() - 2:
                self.highlight_row(highlighted_row)
            else:
                self.highlight_row(0)
                highlighted_row = 0
            
            found_char_sheet_row = False   #did we find a matching row?
            #retrive the character ID for the highlighted row
            if 0 <= highlighted_row < self.table.rowCount() - 2:           
                item = self.table.item(highlighted_row, self.columns["Character ID"])
                temp_char_ID = int(item.text())
                #check to see if the character ID is valid for this row
                if temp_char_ID is not None:
                    #find the matching row object and make sure it is not a button row
                    for obj in self.rows:
                        if obj.Character_ID == temp_char_ID and getattr(obj, "is_button", "") == "":
                            self.character_sheet_row_ID = temp_char_ID
                            found_char_sheet_row = True    #we found a matching row
                            break
                
            #if we didnt find a matching row, reset the character sheet row ID to the first valid element is rows
            if not found_char_sheet_row:
                    for obj in self.rows:
                        if getattr(obj, "is_button", "") == "":
                            self.character_sheet_row_ID = obj.Character_ID
                            break
                            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open XML file: {e}")
            
        self.process_damage_flag = True #Set flag so damage is calculated
    
    def resize_columns_to_content(self):
        """
        @brief Resize each column in the table to fit the longest cell.
        """
        self.table.resizeColumnsToContents()
        # Force columns to stretch to fill available space
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def save_on_exit(self):
        """
        @brief Ask the user if they want to save the file before exiting.
        @return True if the user wants to exit, False otherwise.
        """
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Do you want to save your changes before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            # If the user chooses to save, call the save action
            ret = self.save_action()
            #if they sucessfully perform a save, ret will be non so true should be returned
            if ret == None:
                ret = True
        elif reply == QMessageBox.StandardButton.No:
            ret = True  # Proceed with exit without saving
        else:
            ret = False  # Cancel the exit action
        return ret
    
    def reset_all_damage(self):
        """
        @brief Set all values in the Damage column to 0, if the Damage column is present.
        """
        if self.columns["Damage"] == -1:
            return  # Damage column not present
        for row in range(self.table.rowCount() - 2):  # Exclude the "Add Row" and "Add Character" button rows
            item = self.table.item(row, self.columns["Damage"])
            if item:
                item.setText("0")
            else:
                self.table.setItem(row, self.columns["Damage"], QTableWidgetItem("0"))
    
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
        self.resize_columns_to_content()    #resize columns to fit new style
        
#**************************Signal Handlers***********************************
    def item_slec_chang_sig(self):
        """
        @brief Signal handler for item selection changes.
        """
        self.table.itemSelectionChanged.disconnect(self.item_slec_chang_sig)  # Connect to item selection changed instead of cell changed
        
        # Get the selected item
        selected_items = self.table.selectedItems()
        
        # If there are selected items, get the first one
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            col = selected_item.column()
            
            #if the selected row is the damage one, set it back to 0. This is a hack so we can get the right signal to fire if the value is unchanged
            if (col == self.columns["Damage"]):
                self.table.cellChanged.disconnect(self.cell_content_signal)
                self.table.item(row, col).setText("0")
                self.table.cellChanged.connect(self.cell_content_signal)
        
        self.table.itemSelectionChanged.connect(self.item_slec_chang_sig)  # Connect to item selection changed instead of cell changed      
        
    def cell_content_signal(self, row, col):
        """
        @brief Signal handler for cell content validation and updating the data model.
        @param row The row index of the changed cell.
        @param col The column index of the changed cell.
        """
        self.table.cellChanged.disconnect(self.cell_content_signal)
        
        error = self.validate_cell_content(row, col)
        
        if not error:
            # Get the Character_ID from the table for this row
            char_id_item = self.table.item(row, self.columns["Character ID"])
            if char_id_item:
                try:
                    char_id = int(char_id_item.text())
                except ValueError:
                    char_id = None
            else:
                char_id = None

            # Find the CharacterRow object with this Character_ID
            target_row_obj = None
            if char_id is not None:
                for obj in self.rows:
                    if hasattr(obj, "Character_ID") and obj.Character_ID == char_id and getattr(obj, "is_button", "") == "":
                        target_row_obj = obj
                        break

            # Update the attribute if found
            if target_row_obj:
                col_name = ColumnNames[col]
                attr_name = col_name.replace(" ", "_").replace("/", "_").replace("-", "_")
                item = self.table.item(row, col)
                if item:
                    # Get the current type of the attribute
                    current_value = getattr(target_row_obj, attr_name, "")
                    new_value = item.text()
                    skipSave = False
                    # Try to cast to the original type
                    try:
                        if isinstance(current_value, int):
                            cast_value = int(new_value) if new_value.strip() != "" else 0
                        elif isinstance(current_value, float):
                            cast_value = float(new_value) if new_value.strip() != "" else 0.0
                        elif isinstance(current_value, list):
                            #do nothing, as this is not currently used (feats, actions, etc)
                            skipSave = True
                        else:
                            cast_value = new_value
                    except ValueError:
                        cast_value = current_value  # fallback to old value if conversion fails
                    if not skipSave:
                        setattr(target_row_obj, attr_name, cast_value)

        if not error:
            if col == self.columns["Temp. HP"]:
                target_row_obj.Temporary_Hit_Points = int(self.table.item(row, col).text())
            if col == self.columns["Damage"] and target_row_obj is not None:
                self.process_damage(row, target_row_obj.Character_ID)
            if col == self.columns["Current HP"]:
                self.HP_Highlighting(row)
            if col == self.columns["Conditions/Spell Effects"]:
                self.update_condition_tooltip(row)
        
            if self.process_damage_flag == True:
                if self.character_sheet_window is not None:
                    #are we looking at the character displayed by the character sheet?
                    #self.update_character_sheet(target_row_obj) #update the sheet we with the new information
                    self.character_sheet_window.update_sheet_object(target_row_obj)
                    
        self.table.cellChanged.connect(self.cell_content_signal)
    
    def next_turn(self):
        """
        @brief Highlight the next valid row for the next turn.
        """
        
        self.process_damage_flag = False #Reset flag so damage is not calculated

        """Find the next valid row and highlight it."""
        current_row = self.clear_highlighted_row(self.style_sheet.colour_current_turn)

        # Find the next valid row
        next_row = -1
        for row in range(current_row + 1, self.table.rowCount() - 2):  # Exclude the "Add Row" button row
            initiative_item = self.table.item(row, self.columns["Initiative"])  # Use variable
            hp_item = self.table.item(row, self.columns["Current HP"])  # Use variable
            if initiative_item and hp_item:
                initiative = int(initiative_item.text())
                current_hp = int(hp_item.text())
                if initiative > 0 and current_hp > 0:
                    next_row = row
                    break

        # If no valid row is found below, start from the top
        if next_row == -1:
            for row in range(0, current_row):
                initiative_item = self.table.item(row, self.columns["Initiative"])  # Use variable
                hp_item = self.table.item(row, self.columns["Current HP"])  # Use variable
                if initiative_item and hp_item:
                    initiative = int(initiative_item.text())
                    current_hp = int(hp_item.text())
                    if initiative > 0 and current_hp > 0:
                        next_row = row
                        break

        # Highlight the next valid row
        if next_row != -1:
            self.highlight_row(next_row)
        
        #update the character sheet to this character only if it exists
        if hasattr(self, 'character_sheet_window'):
            #find the char ID for the highlighted row
            char_id_item = self.table.item(next_row, self.columns["Character ID"])
            if char_id_item:
                try:
                    char_id = int(char_id_item.text())
                except ValueError:
                    char_id = 0
            else:
                char_id = 0
            
            self.character_sheet_row_ID = char_id   #store the ID of the character to show in the sheet
            #find the object for this row
            target_row_obj = None
            for row_obj in self.rows:
                if hasattr(row_obj, "Character_ID") and row_obj.Character_ID == char_id and getattr(row_obj, "is_button", "") == "":
                    target_row_obj = row_obj
                    break
            self.update_character_sheet(target_row_obj)
            
        self.process_damage_flag = True #Set flag so damage is not calculated
             
    def sort_initiative(self):
        """
        @brief Sort the rows of the table based on the Initiative column.
        """
        self.process_damage_flag = False #Reset flag so damage is not calculated
        
        # If no rows are present except the header, return
        if self.table.rowCount() == 1:
            return
        
        self.clear_highlighted_row(self.style_sheet.colour_current_turn)
        
            
        # Create a sorted list of rows based on Initiative in descending order
        sorted_rows = sorted(
            [row for row in self.rows if getattr(row, "is_button", "") == ""],
            key=lambda x: x.Initiative,
            reverse=True
        )
        
        #delete all rows except (button rows are handled in delete_row)
        for row_obj in sorted_rows:
            self.delete_row_character(row_obj, False)   #False so we dont remove from self.rows
        
        #re-add all rows from the ordered list
        for row_obj in sorted_rows:
            self.add_row(row_obj, False)  #False so we dont add to self.rows again
        
        # Highlight the next valid row after sorting
        self.next_turn()
        
        self.process_damage_flag = True #Reset flag so damage is not calculated
        
    def reset_all_hp(self):
        """
        @brief Reset all HP in the Current HP column to the value in the Max HP column.
        """
        for row in range(self.table.rowCount() - 2):  # Exclude the "Add Row" and "Add Character" button row
            max_hp_item = self.table.item(row, self.columns["Max HP"])
            current_hp_item = self.table.item(row, self.columns["Current HP"])
            temp_hp_item = self.table.item(row, self.columns["Temp. HP"])
            damage_item = self.table.item(row, self.columns["Damage"])

            
            if max_hp_item and current_hp_item:
                max_hp = int(max_hp_item.text()) if self.is_integer(max_hp_item.text()) else 0
                current_hp_item.setText(str(max_hp))  # Set Current HP to Max HP
            
            if temp_hp_item:
                temp_hp_item.setText("0")  # Reset Temporary HP to 0
            
            if damage_item:
                damage_item.setText("0")  # Reset Damage to 0

            # Update the HP highlighting for the row
            self.HP_Highlighting(row)
    
    def add_row_blank(self):
        '''
        @brief Add a blank row to the table.
        '''
        char_temp = CharacterRow()
        char_temp._set_generic()
        self.add_row(char_temp)
    
    def finish_combat(self):
        """
        @brief Reset the damage column and sort rows so non-NPC rows are on top, sorted alphabetically.
        """
        """reset the damage column to 0 so it does not affect the sorting."""
        self.reset_all_damage()
        
        #Set all initiatives to 0
        for char in self.rows:
            if getattr(char, "is_button", "") == "":
                char.Initiative = 0
        
        #re-order so the player characters are at the top, sorted alphabetically
        non_npc_rows = [row for row in self.rows if getattr(row, "is_button", "") == "" and row.Player_Name != "NPC"]
        npc_rows = [row for row in self.rows if getattr(row, "is_button", "") == "" and row.Player_Name == "NPC"]

        #delete all rows except (button rows are handled in delete_row)
        for row_obj in non_npc_rows:
            self.delete_row_character(row_obj, False)   #False so we dont remove from self.rows
        for row_obj in npc_rows:
            self.delete_row_character(row_obj, False)   #False so we dont remove from self.rows
        
        #add the rows back, non-npc first sorted alphabetically
        npc_rows.sort(key=lambda x: x.Player_Name)
        non_npc_rows.sort(key=lambda x: x.Player_Name)
        for row_obj in non_npc_rows:
            self.add_row(row_obj, False)  #False so we dont add to self.rows again
        for row_obj in npc_rows:
            self.add_row(row_obj, False)  #False so we dont add to self.rows again

    def add_character(self):
        """
        @brief Open a new window to select characters from XML files and add them to the game.
        """
        character_window = CharacterSelectionWindow(self)
        character_window.exec()  # Open the window as a modal dialog

        # Get the selected characters from the dialog
        #selected_characters = character_window.get_selected_characters()
        selected_characters = character_window.get_selected_characters_class()
        
        for character in selected_characters:
            # Add each selected character to the table
            self.add_row(character)  # Use the add_row method to add the character to the list and table
        
        # Add the selected characters to the table
        #for character in selected_characters:
        #    self.add_character_from_xml(character)

    def open_dice_roller(self):
        """
        @brief Open the Dice Roller window.
        """
        self.dice_roller_window = DiceRollerWindow(self)
        self.dice_roller_window.show()

    def roll_initiative(self):
        """
        @brief Roll initiative for all characters with current_HP > 0 and is_button == "".
        Sets initiative to a random value between 0 and 20 for each applicable CharacterRow.
        Updates the table to reflect the new initiative values.
        """
        self.process_damage_flag = False #Reset flag so damage is not calculated
        
        #Confirm with the user before rolling initiative. Stops problems if they click it by mistake
        message = "Do you want to roll initiative for "
        if self.settings.roll_pc_initiative == True:
            message += "all characters?"
        else:
            message += "only NPCs?"
        reply = QMessageBox.question(None, "Confirm Roll", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            import random
            for row in self.rows:
                if row.is_button == "":
                    if row.Current_HP > 0:
                        if self.settings.roll_pc_initiative == True or row.Player_Name == "NPC":
                            initiative = random.randint(1, 20)
                            #if they have a custom initiative bonus, add it to the rolled value
                            if row.Initiative_Bonus != 0:
                                initiative += row.Initiative_Bonus  # Add any existing initiative value
                            else:
                                #add the dex modifier to the initiative
                                initiative += (row.Dexterity - 10) // 2  # Calculate the Dexterity modifier
                            #make sure the initiative is set to atleast 1
                            if initiative < 1:
                                initiative = 1
                            
                            row.Initiative = initiative #set the initiative value for this object
            
            self.update_entire_table_column("Initiative")  # Update the table to reflect changes
        
        self.process_damage_flag = True #Reset flag so damage is calculated

    def update_conditions_Dropboxes(self):
        # --- Update all dropdowns in the Select column ---
        for row in range(self.table.rowCount() - 2):  # Exclude the last two button rows
            dropdown = self.table.cellWidget(row, self.columns["Select"])
            if isinstance(dropdown, QComboBox):
                dropdown.blockSignals(True)
                dropdown.clear()
                dropdown.addItem("")  # add a blank item

                # Load items and descriptions from the new XML file
                try:
                    tree = ET.parse(self.condtions_spellEffect_file_path)
                    root = tree.getroot()
                    for condition in root.findall("condition"):
                        name = condition.find("name").text
                        description = condition.find("description").text
                        dropdown.addItem(name)
                        dropdown.setItemData(dropdown.count() - 1, description, Qt.ItemDataRole.ToolTipRole)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load dropdown items: {e}")
                dropdown.blockSignals(False)
                #update the tooltip for the conditions/spell effects column
                self.update_condition_tooltip(row)
    
    def select_conditions_file(self):
        """
        @brief open up a dialog so the conditions/spell effects file can be selected.
        """

        #set the default path to the conditions spell effects folder
        default_path = "./Settings/Condition_Spell_Effects"

        # Open a file dialog to select the save location
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Conditions/Spell Effects File", default_path, "XML Files (*.xml)")
        if not file_path:
            return False # If the user cancels, do nothing
        
        self.condtions_spellEffect_file_path = file_path   #store the file path if it is valid 
        
        self.update_conditions_Dropboxes() #update all the dropboxes in the select column

    def modify_conditions_spell_effects(self):
        """
        @brief Open a window to view, edit, add, and save conditions/spell effects from the selected XML file.
        """
        # Read conditions from XML
        try:
            tree = ET.parse(self.condtions_spellEffect_file_path)
            root = tree.getroot()
            conditions = []
            for cond_elem in root.findall("condition"):
                name = cond_elem.findtext("name", "")
                description = cond_elem.findtext("description", "")
                conditions.append({"name": name, "description": description})
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load conditions: {e}")
            return

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Modify Conditions and Spell Effects")
        dialog.setMinimumSize(600, 400)
        main_layout = QVBoxLayout(dialog)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left: List of conditions
        list_widget = QListWidget()
        for cond in conditions:
            list_widget.addItem(cond["name"])
        content_layout.addWidget(list_widget, 1)

        # Right: Editable fields
        edit_widget = QWidget()
        edit_layout = QVBoxLayout(edit_widget)
        name_label = QLabel("Name:")
        name_input = QLineEdit()
        desc_label = QLabel("Description:")
        
        # Formatting buttons
        format_button_layout = QHBoxLayout()
        bold_button = QPushButton("B")
        bold_button.setCheckable(True)
        bold_button.setStyleSheet("font-weight: bold;")
        italic_button = QPushButton("I")
        italic_button.setCheckable(True)
        italic_button.setStyleSheet("font-style: italic;")
        underline_button = QPushButton("U")
        underline_button.setCheckable(True)
        underline_button.setStyleSheet("text-decoration: underline;")
        format_button_layout.addWidget(bold_button)
        format_button_layout.addWidget(italic_button)
        format_button_layout.addWidget(underline_button)
        
        desc_input = QTextEdit()
        desc_input.setMinimumHeight(100)
        edit_layout.addWidget(name_label)
        edit_layout.addWidget(name_input)
        edit_layout.addWidget(desc_label)
        edit_layout.addLayout(format_button_layout)
        edit_layout.addWidget(desc_input)
        content_layout.addWidget(edit_widget, 2)

        # Bottom: Add and Save buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New Condition")
        save_button = QPushButton("Save Changes")
        remove_button = QPushButton("Remove Condition")
        button_layout.addWidget(add_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(remove_button)
        main_layout.addLayout(button_layout)

        # Track last selected index
        last_selected = [None]
        
        # Formatting functions
        def toggle_bold():
            desc_input.setFocus()
            cursor = desc_input.textCursor()
            fmt = desc_input.currentCharFormat()
            is_bold = fmt.fontWeight() == QFont.Weight.Bold
            fmt.setFontWeight(QFont.Weight.Normal if is_bold else QFont.Weight.Bold)
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                desc_input.setCurrentCharFormat(fmt)
            bold_button.setChecked(not is_bold)

        def toggle_italic():
            desc_input.setFocus()
            cursor = desc_input.textCursor()
            fmt = desc_input.currentCharFormat()
            is_italic = fmt.fontItalic()
            fmt.setFontItalic(not is_italic)
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                desc_input.setCurrentCharFormat(fmt)
            italic_button.setChecked(not is_italic)

        def toggle_underline():
            desc_input.setFocus()
            cursor = desc_input.textCursor()
            fmt = desc_input.currentCharFormat()
            is_underline = fmt.fontUnderline()
            fmt.setFontUnderline(not is_underline)
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                desc_input.setCurrentCharFormat(fmt)
            underline_button.setChecked(not is_underline)

        #attach the formatting functions to the buttons and shortcuts
        bold_button.clicked.connect(toggle_bold)
        italic_button.clicked.connect(toggle_italic)
        underline_button.clicked.connect(toggle_underline)
        # Add keyboard shortcuts for formatting
        QShortcut(QKeySequence("Ctrl+B"), desc_input, toggle_bold)
        QShortcut(QKeySequence("Ctrl+I"), desc_input, toggle_italic)
        QShortcut(QKeySequence("Ctrl+U"), desc_input, toggle_underline)

        # Optional: Update button states when cursor moves
        def update_format_buttons():
            fmt = desc_input.currentCharFormat()
            bold_button.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
            italic_button.setChecked(fmt.fontItalic())
            underline_button.setChecked(fmt.fontUnderline())

        desc_input.cursorPositionChanged.connect(update_format_buttons)

        def load_selected_condition():
            idx = list_widget.currentRow()
            if 0 <= idx < len(conditions):
                name_input.setText(conditions[idx]["name"])
                desc_input.setHtml(html.unescape(conditions[idx]["description"]))
            else:
                name_input.clear()
                desc_input.clear()
        
        def minimal_html_from_qtextedit(desc_input):
            """
            @brief Convert QTextEdit HTML to minimal HTML with only <b>, <i>, <u>, and <br> tags.
            @param desc_input The QTextEdit containing the rich text.
            @return A string with the cleaned HTML.
            """
            # Get the full HTML from QTextEdit
            full_html = desc_input.toHtml()
            soup = BeautifulSoup(full_html, "html.parser")
            body = soup.body
            if body:
                html_content = body.decode_contents()
            else:
                html_content = desc_input.toPlainText().replace('\n', '<br>')

            # Parse again to manipulate tags
            soup = BeautifulSoup(html_content, "html.parser")

            # Convert <span style=" font-weight:700;"> to <b>
            for span in soup.find_all("span"):
                style = span.get("style", "")
                if "font-weight:700" in style or "font-weight: bold" in style:
                    b_tag = soup.new_tag("b")
                    b_tag.string = span.get_text()
                    span.replace_with(b_tag)
                elif "font-style:italic" in style:
                    i_tag = soup.new_tag("i")
                    i_tag.string = span.get_text()
                    span.replace_with(i_tag)
                elif "text-decoration: underline" in style:
                    u_tag = soup.new_tag("u")
                    u_tag.string = span.get_text()
                    span.replace_with(u_tag)
                else:
                    # If not bold/italic/underline, unwrap the span
                    span.unwrap()

            # Remove all <p> tags but keep their contents and <br>
            for p in soup.find_all("p"):
                p.insert_after(soup.new_tag("br"))
                p.unwrap()

            # Remove all attributes from allowed tags
            for tag in soup.find_all(['b', 'i', 'u', 'br']):
                tag.attrs = {}

            # Remove any other tags
            for tag in soup.find_all(True):
                if tag.name not in ['b', 'i', 'u', 'br']:
                    tag.unwrap()

            # Remove trailing <br> if present
            result = soup.decode_contents().strip()
            while result.endswith('<br/>'):
                result = result[:-5].rstrip()

            return result

        def save_current_edits():
            idx = last_selected[0]
            if idx is not None and 0 <= idx < len(conditions):
                conditions[idx]["name"] = name_input.text()
                desc_clean = minimal_html_from_qtextedit(desc_input)
                conditions[idx]["description"] = desc_clean
                list_widget.item(idx).setText(name_input.text())

        def on_selection_changed(new_idx):
            # Save edits to the previously selected item (if any)
            if last_selected[0] is not None and 0 <= last_selected[0] < len(conditions):
                save_current_edits()
            # Load the newly selected item's data
            load_selected_condition()
            last_selected[0] = new_idx

        list_widget.currentRowChanged.connect(on_selection_changed)
        
        #main save condition function
        def save_to_xml(showDialogMessage=True):
            # Save edits to the currently selected item
            if last_selected[0] is not None and 0 <= last_selected[0] < len(conditions):
                save_current_edits()
            # Remove all old conditions
            for cond_elem in root.findall("condition"):
                root.remove(cond_elem)
            # Add updated conditions
            for cond in conditions:
                cond_elem = ET.SubElement(root, "condition")
                ET.SubElement(cond_elem, "name").text = cond["name"]
                ET.SubElement(cond_elem, "description").text = cond["description"]
            try:
                ET.indent(tree, space="  ", level=0)
                tree.write(self.condtions_spellEffect_file_path, encoding="utf-8", xml_declaration=True)
                #only show the message and close the box if the button was pressed, not if crtl+s was used
                if showDialogMessage:
                    QMessageBox.information(dialog, "Success", "Conditions saved successfully.")
                    dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save XML: {e}")
            
            self.update_conditions_Dropboxes() #update the dropboxes in the select column with the new changes

        def save_to_xml_silent():
            save_to_xml(showDialogMessage=False)
        
        def save_to_xml_loud():
            save_to_xml(showDialogMessage=True)
        
        save_button.clicked.connect(save_to_xml_loud)
        
        #Add new condition function
        def add_new_condition():
            # Save edits to the currently selected item
            if last_selected[0] is not None and 0 <= last_selected[0] < len(conditions):
                save_current_edits()
            # Add new blank condition
            conditions.append({"name": "New Condition", "description": ""})
            list_widget.addItem("New Condition")
            list_widget.setCurrentRow(len(conditions) - 1)  # This will trigger loading the new blank fields

        add_button.clicked.connect(add_new_condition)
        
        #Remove condition function
        def remove_condition():
            idx = list_widget.currentRow()
            if 0 <= idx < len(conditions):
                # Confirm deletion
                reply = QMessageBox.question(dialog, "Confirm Deletion", f"Are you sure you want to delete the condition '{conditions[idx]['name']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    # Remove from data and UI
                    conditions.pop(idx)
                    list_widget.takeItem(idx)
                    # Clear fields
                    name_input.clear()
                    desc_input.clear()
                    last_selected[0] = None
                    save_to_xml_silent()  # Save changes immediately
    
        remove_button.clicked.connect(remove_condition)
        
        # Add keyboard shortcuts for formatting
        QShortcut(QKeySequence("Ctrl+S"), desc_input, save_to_xml_silent)

        # Initialize selection
        if conditions:
            list_widget.setCurrentRow(0)
        else:
            add_new_condition()

        dialog.exec()

    def open_character_sheet(self):
        """
        @brief Open the Character Sheet window.
        """
        #cycle through the rows to find the character with the matching ID
        for row in self.rows:
            #if the row is not a button
            if row.is_button == "":
                #if the rows match
                if row.Character_ID == self.character_sheet_row_ID:
                    #if it the character sheet does not exist, create it
                    if self.character_sheet_window is None:
                        #self.character_sheet_window = CharacterSheetWindow(row)
                        self.character_sheet_window = CharacterSheetWindow(self.rows, row.Character_ID)
                    #if the window is not visable, show it
                    if not self.character_sheet_window.isVisible():
                        self.character_sheet_window.show()
                    break
    
    def update_character_sheet(self, character_row = CharacterRow()):
        """
        @brief Update the Character Sheet window if it exists
        @param character_row The CharacterRow object to display in the character sheet.
        """        
        #if the object exisits
        if character_row is not None and self.character_sheet_window is not None:
            # if the objct is not a button
            if character_row.is_button == "":
                #if there is a character sheet object send the ID
                if self.character_sheet_window.isVisible():
                    self.character_sheet_window.update_sheet(character_row.Character_ID)  #update to a new character

#******************************Menu Functions***********************************
    
    def toggle_fullscreen(self):
        """
        @brief Toggle the fullscreen mode.
        """
        if self.isFullScreen():
            self.showNormal()  # Exit fullscreen
        else:
            self.showFullScreen()  # Enter fullscreen

    def save_action(self):
        """
        @brief Save the table data to the current file path, or prompt for a file path if not set.
        @return True if the file was saved, False otherwise.
        """
        #if a file path has been set, save the data to that file
        if self.file_path != "":
            self.save_data_to_xml()
            return True #return true to indicate that the file was saved
        else:
            #if no file path has been set, call the save_as_action function to set the file path
            return self.save_as_action() #return if the file was saved or not

    def save_as_action(self):
        """
        @brief Save the table data to a CSV file, prompting the user for a file path.
        @return True if the file was saved, False otherwise.
        """
        #make the save directory if it does not exist
        if not os.path.exists("./Save Files"):
            os.makedirs("./Save Files")
        
        #if we have saved or loaded a file preiously, use that file path as the default location
        if self.file_path != "":
            default_path = os.path.dirname(self.file_path)
        else:
            default_path = "./Save Files"
        
        # Open a file dialog to select the save location
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path, "XML Files (*.xml)")
        if not file_path:
            return  False # If the user cancels, do nothing

        #store the file path if it is valid
        self.file_path = file_path
        
        self.save_data_to_xml()

    def open_action(self):
        self.open_from_xml()
    
    def exit_action(self):
        """
        @brief Exit the application. Any saving will be handled by the closeEvent.
        """
        QApplication.quit()  # Close the application
           
    def reset_layout(self):
        """
        @brief Reset the layout to the default state, showing only the default columns.
        """
         #find and clear the currently highlighted row
        current_row = self.clear_highlighted_row(self.style_sheet.colour_current_turn)
        
        self.style_sheet.resetLayout()  #set the style sheet to default settings
        old_currentTurn_highlightColour = self.style_sheet.colour_current_turn #store the old colour for the highlighted row

        # Reset the colors in the table
        for row in range(self.table.rowCount() - 2):
            self.HP_Highlighting(row)
            #refresh the highlighted row if it was changed
            if row == self.find_highlighted_row(old_currentTurn_highlightColour):
                self.highlight_row(row)

        # Hide all columns by default
        for col in range(len(ColumnNames)):
            self.table.setColumnHidden(col, True)

        # Show only the specified columns
        self.table.setColumnHidden(self.columns["X"], False)
        self.table.setColumnHidden(self.columns["Player Name"], False)
        self.table.setColumnHidden(self.columns["Character Name"], False)
        self.table.setColumnHidden(self.columns["Speed"], False)
        self.table.setColumnHidden(self.columns["Initiative"], False)
        self.table.setColumnHidden(self.columns["Armor Class"], False)
        self.table.setColumnHidden(self.columns["Max HP"], False)
        self.table.setColumnHidden(self.columns["Temp. HP"], False)
        self.table.setColumnHidden(self.columns["Current HP"], False)
        self.table.setColumnHidden(self.columns["Damage"], False)
        self.table.setColumnHidden(self.columns["Conditions/Spell Effects"], False)
        self.table.setColumnHidden(self.columns["Select"], False)

        #self.resize_columns_to_content()  # Resize columns to fit content
                
        self.highlight_row(current_row) #highlight the correct row
        
        #set the text, colour, etc as per the theme
        self.set_Custom_Style_Sheet()   #apply the settings ot the style sheet
        
    def hide_columns_action(self):
        """
        @brief Open a window to select which columns to hide or unhide, with checkboxes in a grid (max 10 rows per column).
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Hide/Unhide Columns")
        dialog.setGeometry(300, 300, 400, 400)

        layout = QVBoxLayout(dialog)

        # Use a grid for checkboxes
        grid = QGridLayout()
        layout.addLayout(grid)

        checkboxes = []
        max_rows = 10
        for col in range(len(ColumnNames)):
            header_item = self.table.horizontalHeaderItem(col)
            if header_item and header_item.text():
                checkbox = QCheckBox(header_item.text())
                checkbox.setChecked(not self.table.isColumnHidden(col))
                row = len(checkboxes) % max_rows
                grid_col = len(checkboxes) // max_rows
                grid.addWidget(checkbox, row, grid_col)
                checkboxes.append((col, checkbox))

        # Hide All/Show All button
        toggle_button = QPushButton("Hide All")
        layout.addWidget(toggle_button)

        # Default button
        default_button = QPushButton("Default")
        layout.addWidget(default_button)

        # Save and Cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def update_toggle_button():
            if all(checkbox.isChecked() for _, checkbox in checkboxes):
                toggle_button.setText("Hide All")
            else:
                toggle_button.setText("Show All")

        for _, checkbox in checkboxes:
            checkbox.stateChanged.connect(update_toggle_button)

        def toggle_all():
            if toggle_button.text() == "Hide All":
                for _, checkbox in checkboxes:
                    checkbox.setChecked(False)
            else:
                for _, checkbox in checkboxes:
                    checkbox.setChecked(True)
            update_toggle_button()

        toggle_button.clicked.connect(toggle_all)

        def apply_default_visibility():
            # Set all checkboxes to False (hidden)
            for _, checkbox in checkboxes:
                checkbox.setChecked(False)
            # Enable only the specified columns
            for col, checkbox in checkboxes:
                if col in [
                    self.columns["X"],
                    self.columns["Player Name"],
                    self.columns["Character Name"],
                    self.columns["Speed"],
                    self.columns["Initiative"],
                    self.columns["Armor Class"],
                    self.columns["Max HP"],
                    self.columns["Temp. HP"],
                    self.columns["Current HP"],
                    self.columns["Damage"],
                    self.columns["Conditions/Spell Effects"],
                    self.columns["Select"],
                ]:
                    checkbox.setChecked(True)

        default_button.clicked.connect(apply_default_visibility)

        def save_column_visibility():
            for col, checkbox in checkboxes:
                self.table.setColumnHidden(col, not checkbox.isChecked())
                if col == self.columns["Conditions/Spell Effects"]:
                    self.table.setColumnHidden(self.columns["Select"], not checkbox.isChecked())
            self.resize_columns_to_content()
            dialog.accept()

        save_button.clicked.connect(save_column_visibility)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()
    
    def new_action(self):
        """
        @brief Reset the table to its default state with three default rows.
        """
        #clear all the data in theh
        while self.table.rowCount() > 2:
            self.table.removeRow(0) # Remove all rows that are not the buttons
        
        #Add in three default rows
        for i in range(3):
            char_tmep = CharacterRow()
            char_tmep._set_generic()
            self.add_row(char_tmep)  # Add a default row
        
        #reset the layout back to default
        self.reset_layout()
        
    def options_action(self):
        """
        @brief Open a dialog to change program settings.
        """
        
        #temp storage for the colours while the dialog is open
        tmp_colours = {
            "general": self.style_sheet.colour_general,
            "minor": self.style_sheet.colour_minor,
            "button": self.style_sheet.colour_button,
            "general_text": self.style_sheet.colour_general_text,
            "button_text": self.style_sheet.colour_button_text,
            "table_text": self.style_sheet.colour_table_text,
            "current_turn": self.style_sheet.colour_current_turn,
            "full_hp": self.style_sheet.colour_full_hp,
            "critical_hp": self.style_sheet.colour_critical_hp,
            "no_hp": self.style_sheet.colour_no_hp
            
        }
        # Function to open the color picker and update the temporary color
        ##ADD TO THIS< WORK IN PROGRESS
        def pick_color():
            btn = dialog.sender()           #get the button that was clicked
            color = QColorDialog.getColor()
            if color.isValid():
                #selected_type = color_type_dropdown.currentText()
                #temp_colors[selected_type] = color.name()
                # Update the color display
                #color_display.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
                if btn == general_text_colour_button:
                    tmp_colours["general_text"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    general_text_color_display.setStyleSheet(f"background-color: {tmp_colours["general_text"]}; border: 1px solid black;") #update the widget showing the colour
                elif btn == table_text_colour_button:
                    tmp_colours["table_text"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    table_text_color_display.setStyleSheet(f"background-color: {tmp_colours["table_text"]}; border: 1px solid black;")
                elif btn == button_text_colour_button:
                    tmp_colours["button_text"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    button_text_color_display.setStyleSheet(f"background-color: {tmp_colours["button_text"]}; border: 1px solid black;")
                elif btn == button_colour_button:
                    tmp_colours["button"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    button_color_display.setStyleSheet(f"background-color: {tmp_colours["button"]}; border: 1px solid black;")
                elif btn == general_colour_button:
                    tmp_colours["general"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    general_color_display.setStyleSheet(f"background-color: {tmp_colours["general"]}; border: 1px solid black;")
                elif btn == minor_colour_button:
                    tmp_colours["minor"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    minor_color_display.setStyleSheet(f"background-color: {tmp_colours["minor"]}; border: 1px solid black;")
                elif btn == current_turn_colour_button:
                    tmp_colours["current_turn"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    current_turn_color_display.setStyleSheet(f"background-color: {tmp_colours["current_turn"]}; border: 1px solid black;")
                elif btn == fullhp_colour_button:
                    tmp_colours["full_hp"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    fullhp_color_display.setStyleSheet(f"background-color: {tmp_colours["full_hp"]}; border: 1px solid black;")
                elif btn == crithp_colour_button:
                    tmp_colours["critical_hp"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    crithp_color_display.setStyleSheet(f"background-color: {tmp_colours["critical_hp"]}; border: 1px solid black;")
                elif btn == nohp_colour_button:
                    tmp_colours["no_hp"] = color.name(QColor.NameFormat.HexArgb) #return in #aarrggbb format
                    nohp_color_display.setStyleSheet(f"background-color: {tmp_colours["no_hp"]}; border: 1px solid black;")
                
        #find all available fonts on the system
        fonts = sorted(QFontDatabase.families())
        
        # Create a dialog window
        dialog = QDialog(self)
        dialog.setWindowTitle("Options")
        dialog.setGeometry(300, 300, 600, 600)

        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        
        # Create a layout for the dialog
        layout = QVBoxLayout(content_widget)
        
        scroll_area.setWidget(content_widget)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(scroll_area)
        
        layout_general = QVBoxLayout()  #layout for general settings
        
        layout_text = QHBoxLayout()  #layout for text input
        
        layout_text_size = QVBoxLayout()  #layout for text size input
        layout_text_font = QVBoxLayout()  #layout for text size input
        
        #title for the General Settings:
        text_font_title = QLabel("General Settings:")
        text_font_title.setStyleSheet("font-weight: bold;")
        layout_general.addWidget(text_font_title)
   
        
        #initive for player characters checkbox
        pc_initiative_layout = QHBoxLayout()
        pc_initiative_label = QLabel("Roll Player Characters Initiative:")
        pc_initiative_checkbox = QCheckBox()
        pc_initiative_checkbox.setChecked(self.settings.roll_pc_initiative)
        pc_initiative_layout.addWidget(pc_initiative_label)
        pc_initiative_layout.addWidget(pc_initiative_checkbox)
        layout_general.addLayout(pc_initiative_layout)
        
        layout.addLayout(layout_general)
        
        #title for the text font:
        text_font_title = QLabel("Text Font:")
        text_font_title.setStyleSheet("font-weight: bold;")
        layout_text_font.addWidget(text_font_title)
        
        # Add a layout for seleting general font
        general_font_layout = QHBoxLayout()
        general_font_lable = QLabel("General Text Font:")
        general_font_combo = QComboBox()  #combo box to selext fonts
        general_font_combo.addItems(fonts)
        #set the current font to the one in use
        current_general_font_index = general_font_combo.findText(self.style_sheet.font_general_style)
        if current_general_font_index >= 0: # Check if the font was found
            general_font_combo.setCurrentIndex(current_general_font_index)
        general_font_layout.addWidget(general_font_lable)
        general_font_layout.addWidget(general_font_combo)
        layout_text_font.addLayout(general_font_layout)
        
        # Add a layout for seleting button font
        button_font_layout = QHBoxLayout()
        button_font_lable = QLabel("Button Text Font:")
        button_font_combo = QComboBox()  #combo box to selext fonts
        button_font_combo.addItems(fonts)
        #set the current font to the one in use
        current_button_font_index = button_font_combo.findText(self.style_sheet.font_button_style)
        if current_button_font_index >= 0: # Check if the font was found
            button_font_combo.setCurrentIndex(current_button_font_index)
        button_font_layout.addWidget(button_font_lable)
        button_font_layout.addWidget(button_font_combo)
        layout_text_font.addLayout(button_font_layout)
        
        # Add a layout for seleting table font
        table_font_layout = QHBoxLayout()
        table_font_lable = QLabel("Table Text Font:")
        table_font_combo = QComboBox()  #combo box to selext fonts
        table_font_combo.addItems(fonts)
        #set the current font to the one in use
        current_table_font_index = table_font_combo.findText(self.style_sheet.font_table_style)
        if current_general_font_index >= 0: # Check if the font was found
            table_font_combo.setCurrentIndex(current_table_font_index)
        table_font_layout.addWidget(table_font_lable)
        table_font_layout.addWidget(table_font_combo)
        layout_text_font.addLayout(table_font_layout)
        
        
        layout_text.addLayout(layout_text_font)  #add the font selection layout
        
        #Add a layout for general text size
        general_text_size_layout = QHBoxLayout()
        general_text_size_label = QLabel("General Text Size:")
        general_text_size_input = QLineEdit(str(self.style_sheet.font_general_size))  # Populate with current size
        general_text_size_layout.addWidget(general_text_size_label)
        general_text_size_layout.addWidget(general_text_size_input)
        layout_text_size.addLayout(general_text_size_layout)

        # Add a layout for button text size
        button_text_size_layout = QHBoxLayout()
        button_text_size_label = QLabel("Button Text Size:")
        button_text_size_input = QLineEdit(str(self.style_sheet.font_button_size))  # Populate with current size
        button_text_size_layout.addWidget(button_text_size_label)
        button_text_size_layout.addWidget(button_text_size_input)
        layout_text_size.addLayout(button_text_size_layout)

        # Add a layout for table text size
        table_text_size_layout = QHBoxLayout()
        table_text_size_label = QLabel("Table Text Size:")
        table_text_size_input = QLineEdit(str(self.style_sheet.font_table_size))  # Populate with current size
        table_text_size_layout.addWidget(table_text_size_label)
        table_text_size_layout.addWidget(table_text_size_input)
        layout_text_size.addLayout(table_text_size_layout)
        
        layout_text.addLayout(layout_text_size)   #add the text size to the layout
        
        #add the text size layout to the main layout
        layout.addLayout(layout_text)
        
        layout_text_colour = QVBoxLayout()  #layout for text size input
        
        #title for the text colours:
        text_colour_title = QLabel("Text Colour:");
        text_colour_title.setStyleSheet("font-weight: bold;")
        layout_text_colour.addWidget(text_colour_title)
        
        # layout for colour selecter for general text
        general_text_colour_layout = QHBoxLayout()
        general_text_colour_lable = QLabel("General Text Colour:")
        general_text_colour_button = QPushButton("Pick Color")
        general_text_colour_button.clicked.connect(pick_color)
        general_text_color_display = QLabel()
        general_text_color_display.setFixedSize(50, 20)
        general_text_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_general_text}; border: 1px solid black;")
        general_text_colour_layout.addWidget(general_text_colour_lable)
        general_text_colour_layout.addWidget(general_text_color_display)
        general_text_colour_layout.addWidget(general_text_colour_button)
        layout_text_colour.addLayout(general_text_colour_layout)
        
        #for button text
        button_text_colour_layout = QHBoxLayout()
        button_text_colour_lable = QLabel("Button Text Colour:")
        button_text_colour_button = QPushButton("Pick Color")
        button_text_colour_button.clicked.connect(pick_color)
        button_text_color_display = QLabel()
        button_text_color_display.setFixedSize(50, 20)
        button_text_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_button_text}; border: 1px solid black;")
        button_text_colour_layout.addWidget(button_text_colour_lable)
        button_text_colour_layout.addWidget(button_text_color_display)
        button_text_colour_layout.addWidget(button_text_colour_button)
        layout_text_colour.addLayout(button_text_colour_layout)
        
        # layout for colour selecter for the table text
        table_text_colour_layout = QHBoxLayout()
        table_text_colour_lable = QLabel("Table Text Colours:")
        table_text_colour_button = QPushButton("Pick Color")
        table_text_colour_button.clicked.connect(pick_color)
        table_text_color_display = QLabel()
        table_text_color_display.setFixedSize(50, 20)
        table_text_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_table_text}; border: 1px solid black;")
        table_text_colour_layout.addWidget(table_text_colour_lable)
        table_text_colour_layout.addWidget(table_text_color_display)
        table_text_colour_layout.addWidget(table_text_colour_button)
        layout_text_colour.addLayout(table_text_colour_layout)
        
        #add the text colour layout to the main layout
        layout.addLayout(layout_text_colour)
        
        layout_highlight_colour = QVBoxLayout()  #layout for text size input
        
        highlight_colour_title = QLabel("Highlight colours:");
        highlight_colour_title.setStyleSheet("font-weight: bold;")
        layout_highlight_colour.addWidget(highlight_colour_title)
        
        #layout for current turn highlighting colour
        current_turn_colour_layout = QHBoxLayout()
        current_turn_colour_lable = QLabel("Current Turn Colour:")
        current_turn_colour_button = QPushButton("Pick Color")
        current_turn_colour_button.clicked.connect(pick_color)
        current_turn_color_display = QLabel()
        current_turn_color_display.setFixedSize(50, 20)
        current_turn_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_current_turn}; border: 1px solid black;")
        current_turn_colour_layout.addWidget(current_turn_colour_lable)
        current_turn_colour_layout.addWidget(current_turn_color_display)
        current_turn_colour_layout.addWidget(current_turn_colour_button)
        layout_highlight_colour.addLayout(current_turn_colour_layout)
        
        #layout for Full Hp highlighting colour
        fullhp_colour_layout = QHBoxLayout()
        fullhp_colour_lable = QLabel("Full HP Colour:")
        fullhp_colour_button = QPushButton("Pick Color")
        fullhp_colour_button.clicked.connect(pick_color)
        fullhp_color_display = QLabel()
        fullhp_color_display.setFixedSize(50, 20)
        fullhp_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_full_hp}; border: 1px solid black;")
        fullhp_colour_layout.addWidget(fullhp_colour_lable)
        fullhp_colour_layout.addWidget(fullhp_color_display)
        fullhp_colour_layout.addWidget(fullhp_colour_button)
        layout_highlight_colour.addLayout(fullhp_colour_layout)
        
        #layout for critical hp highlighting colour
        crithp_colour_layout = QHBoxLayout()
        crithp_colour_lable = QLabel("Critical HP Colour:")
        crithp_colour_button = QPushButton("Pick Color")
        crithp_colour_button.clicked.connect(pick_color)
        crithp_color_display = QLabel()
        crithp_color_display.setFixedSize(50, 20)
        crithp_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_critical_hp}; border: 1px solid black;")
        crithp_colour_layout.addWidget(crithp_colour_lable)
        crithp_colour_layout.addWidget(crithp_color_display)
        crithp_colour_layout.addWidget(crithp_colour_button)
        layout_highlight_colour.addLayout(crithp_colour_layout)
        
        #layout for no hp highlighting colour
        nohp_colour_layout = QHBoxLayout()
        nohp_colour_lable = QLabel("Critical HP Colour:")
        nohp_colour_button = QPushButton("Pick Color")
        nohp_colour_button.clicked.connect(pick_color)
        nohp_color_display = QLabel()
        nohp_color_display.setFixedSize(50, 20)
        nohp_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_no_hp}; border: 1px solid black;")
        nohp_colour_layout.addWidget(nohp_colour_lable)
        nohp_colour_layout.addWidget(nohp_color_display)
        nohp_colour_layout.addWidget(nohp_colour_button)
        layout_highlight_colour.addLayout(nohp_colour_layout)
        
        layout.addLayout(layout_highlight_colour)
        
        layout_other_colour = QVBoxLayout()  #layout for text size input
        
        #title for the other colours:
        other_colour_title = QLabel("Other Colours:");
        other_colour_title.setStyleSheet("font-weight: bold;")
        layout_other_colour.addWidget(other_colour_title)
        
        #layout for button colour
        button_colour_layout = QHBoxLayout()
        button_colour_lable = QLabel("Button Colour:")
        button_colour_button = QPushButton("Pick Color")
        button_colour_button.clicked.connect(pick_color)
        button_color_display = QLabel()
        button_color_display.setFixedSize(50, 20)
        button_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_button}; border: 1px solid black;")
        button_colour_layout.addWidget(button_colour_lable)
        button_colour_layout.addWidget(button_color_display)
        button_colour_layout.addWidget(button_colour_button)
        layout_other_colour.addLayout(button_colour_layout)
        
        #layout for general colour
        general_colour_layout = QHBoxLayout()
        general_colour_lable = QLabel("Major Colour:")
        general_colour_button = QPushButton("Pick Color")
        general_colour_button.clicked.connect(pick_color)
        general_color_display = QLabel()
        general_color_display.setFixedSize(50, 20)
        general_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_general}; border: 1px solid black;")
        general_colour_layout.addWidget(general_colour_lable)
        general_colour_layout.addWidget(general_color_display)
        general_colour_layout.addWidget(general_colour_button)
        layout_other_colour.addLayout(general_colour_layout)
        
        #layout for general colour
        minor_colour_layout = QHBoxLayout()
        minor_colour_lable = QLabel("Minor Colour:")
        minor_colour_button = QPushButton("Pick Color")
        minor_colour_button.clicked.connect(pick_color)
        minor_color_display = QLabel()
        minor_color_display.setFixedSize(50, 20)
        minor_color_display.setStyleSheet(f"background-color: {self.style_sheet.colour_minor}; border: 1px solid black;")
        minor_colour_layout.addWidget(minor_colour_lable)
        minor_colour_layout.addWidget(minor_color_display)
        minor_colour_layout.addWidget(minor_colour_button)
        layout_other_colour.addLayout(minor_colour_layout)
        
        #add the other colour layout to the main layout
        layout.addLayout(layout_other_colour)
                
        # Add Save and Cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)
        
        # Function to save the text sizes
        def save_preferences_sizes():
            """
            @brief Save the text sizes for buttons, table, and headers from the options dialog.
            
            This function validates the user input for button, table, and header text sizes,
            applies the new font sizes to the corresponding widgets, and closes the dialog if successful.
            If invalid input is provided, a warning message is shown.
            """
            try:
                #general settings
                self.settings.roll_pc_initiative = pc_initiative_checkbox.isChecked()    #store if you should roll init for players or not
                
                #TEXT FONTS
                general_text_font = general_font_combo.currentText()
                if (general_text_font == ""):
                    raise ValueError("General text font must be valid.")
                self.style_sheet.font_general_style = general_text_font
                
                button_text_font = button_font_combo.currentText()
                if (button_text_font == ""):
                    raise ValueError("Butotn text font must be valid.")
                self.style_sheet.font_button_style = button_text_font
                
                table_text_font = table_font_combo.currentText()
                if (table_text_font == ""):
                    raise ValueError("General text font must be valid.")
                self.style_sheet.font_table_style = table_text_font
                
                # TEXT SIZE
                # Validate and apply general text size
                general_text_size = int(general_text_size_input.text())
                if general_text_size <= 0:
                    raise ValueError("General text size must be a positive integer.")
                
                self.style_sheet.font_general_size = general_text_size
                
                # Validate and apply button text size
                button_text_size = int(button_text_size_input.text())
                if button_text_size <= 0:
                    raise ValueError("Button text size must be a positive integer.")
                
                self.style_sheet.font_button_size = button_text_size

                # Validate and apply table text size
                table_text_size = int(table_text_size_input.text())
                if table_text_size <= 0:
                    raise ValueError("Table text size must be a positive integer.")
                
                self.style_sheet.font_table_size = table_text_size
                
                #find and clear the currently highlighted row
                current_row = self.clear_highlighted_row(self.style_sheet.colour_current_turn)
                
                #update the colours
                self.style_sheet.colour_general_text = tmp_colours["general_text"]
                self.style_sheet.colour_button_text = tmp_colours["button_text"]
                self.style_sheet.colour_table_text = tmp_colours["table_text"]
                self.style_sheet.colour_button = tmp_colours["button"]
                self.style_sheet.colour_general = tmp_colours["general"]
                self.style_sheet.colour_minor = tmp_colours["minor"]
                self.style_sheet.colour_current_turn = tmp_colours["current_turn"]
                self.style_sheet.colour_full_hp = tmp_colours["full_hp"]
                self.style_sheet.colour_critical_hp = tmp_colours["critical_hp"]
                self.style_sheet.colour_no_hp = tmp_colours["no_hp"]
                
                self.set_Custom_Style_Sheet()
                
                # Re-highlight rows
                for row in range(self.table.rowCount() - 2):
                    self.HP_Highlighting(row) 
                
                self.highlight_row(current_row) #highlight the correct row
                
                dialog.accept()
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))

        # Connect the Save and Cancel buttons
        save_button.clicked.connect(save_preferences_sizes)
        cancel_button.clicked.connect(dialog.reject)

        # Show the dialog
        dialog.exec()

    def about_menue_action(self):
        """
        @brief Show an "About" dialog with program information.
        """
        about_text = (
            "<h2>DM Assistant</h2>"
            f"<p>Version: {self.version}</p>"
            "<p>Developed by: GS-A1</p>"
            "<p>git repository: https://github.com/GS-A1/DM-Program</p>"
            "<p>This application is designed to assist Game Masters in managing combat encounters, "
            "tracking character stats, and rolling dice for tabletop role-playing games, such as DnD 2024.</p>"
        )
        QMessageBox.about(self, "About DM Assistant", about_text)
    
    def download_repo_action(self):
        git_hub_downloader = GitHubDownloader()
        git_hub_downloader.git_extract_folder(silent=False, folder_path="Settings/Condition_Spell_Effects")
        git_hub_downloader.git_extract_folder(silent=False, folder_path="Settings/Characters")
        
        
#**************************Events**********************************************
    def closeEvent(self, event):
        """
        @brief Ask if the user wants to save before closing.
        @param event The close event.
        """
        reply = self.save_on_exit()
        
        if reply == True:
            #delete the temp folder and all its contents if it exists
            temp_dir = os.path.join(os.path.dirname(__file__), "temp")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            event.accept()  # Allow the window to close
        else:
            event.ignore()  # Cancel the close event
        
        #close the character sheet window if it is open
        if self.character_sheet_window is not None:
            self.character_sheet_window.close()
        
#**************************End of Class***************************************

#**************************Main Function***********************************
if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "Settings", "dnd_dm_icons.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    
    window.show()

    app.exec()