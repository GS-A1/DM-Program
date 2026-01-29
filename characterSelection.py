from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QComboBox, QMessageBox, QMenuBar, QMenu, QLineEdit, QFormLayout, QWidget, QScrollArea, QGridLayout, QTextEdit, QCompleter
from PyQt6.QtGui import QTextOption, QIntValidator
from PyQt6.QtCore import Qt
import os
import xml.etree.ElementTree as ET  # Import the XML parsing module
from xml.etree.ElementTree import ElementTree, indent
from rowdata import CharacterRow  # Assuming CharacterRow is defined in rowdata.py
import rowDataFileIO as CFIO
from githubDownload import GitHubDownloader
import shutil

class CharacterFormWidget(QWidget):
    """
    Widget containing all character input fields, layouts, and helper methods.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_layout = QFormLayout(self)
        self.validator = QIntValidator()

        # Create all input fields as attributes
        self.url_input = QLineEdit()
        self.name_input = QLineEdit()
        self.armor_class_input = QLineEdit()
        self.armor_class_input.setValidator(self.validator)
        self.max_hp_input = QLineEdit()
        self.max_hp_input.setValidator(self.validator)
        self.speed_input_walk = QLineEdit()
        self.speed_input_walk.setValidator(self.validator)
        self.speed_input_fly = QLineEdit()
        self.speed_input_fly.setValidator(self.validator)
        self.speed_input_swim = QLineEdit()
        self.speed_input_swim.setValidator(self.validator)
        self.speed_input_climb = QLineEdit()
        self.speed_input_climb.setValidator(self.validator)
        self.speed_input_burrow = QLineEdit()
        self.speed_input_burrow.setValidator(self.validator)
        self.strength_input = QLineEdit()
        self.strength_input.setValidator(self.validator)
        self.dexterity_input = QLineEdit()
        self.dexterity_input.setValidator(self.validator)
        self.constitution_input = QLineEdit()
        self.constitution_input.setValidator(self.validator)
        self.intelligence_input = QLineEdit()
        self.intelligence_input.setValidator(self.validator)
        self.wisdom_input = QLineEdit()
        self.wisdom_input.setValidator(self.validator)
        self.charisma_input = QLineEdit()
        self.charisma_input.setValidator(self.validator)
        self.background_input = QLineEdit()
        self.class_input = QLineEdit()
        self.species_input = QLineEdit()
        self.subclass_input = QLineEdit()
        self.level_input = QLineEdit()
        self.level_input.setValidator(self.validator)
        self.hit_dice_input = QLineEdit()
        self.proficiency_bonus_input = QLineEdit()
        self.proficiency_bonus_input.setValidator(self.validator)
        self.initiative_bonus_input = QLineEdit()
        self.initiative_bonus_input.setValidator(self.validator)
        self.size_input = QLineEdit()
        self.passive_perception_input = QLineEdit()
        self.passive_perception_input.setValidator(self.validator)
        self.temporary_hit_points_input = QLineEdit()
        self.temporary_hit_points_input.setValidator(self.validator)
        self.arcana_input = QLineEdit()
        self.arcana_input.setValidator(self.validator)
        self.history_input = QLineEdit()
        self.history_input.setValidator(self.validator)
        self.investigation_input = QLineEdit()
        self.investigation_input.setValidator(self.validator)
        self.nature_input = QLineEdit()
        self.nature_input.setValidator(self.validator)
        self.religion_input = QLineEdit()
        self.religion_input.setValidator(self.validator)
        self.athletics_input = QLineEdit()
        self.athletics_input.setValidator(self.validator)
        self.acrobatics_input = QLineEdit()
        self.acrobatics_input.setValidator(self.validator)
        self.sleight_of_hand_input = QLineEdit()
        self.sleight_of_hand_input.setValidator(self.validator)
        self.stealth_input = QLineEdit()
        self.stealth_input.setValidator(self.validator)
        self.animal_handling_input = QLineEdit()
        self.animal_handling_input.setValidator(self.validator)
        self.insight_input = QLineEdit()
        self.insight_input.setValidator(self.validator)
        self.medicine_input = QLineEdit()
        self.medicine_input.setValidator(self.validator)
        self.perception_input = QLineEdit()
        self.perception_input.setValidator(self.validator)
        self.survival_input = QLineEdit()
        self.survival_input.setValidator(self.validator)
        self.deception_input = QLineEdit()
        self.deception_input.setValidator(self.validator)
        self.intimidation_input = QLineEdit()
        self.intimidation_input.setValidator(self.validator)
        self.performance_input = QLineEdit()
        self.performance_input.setValidator(self.validator)
        self.persuasion_input = QLineEdit()
        self.persuasion_input.setValidator(self.validator)
        self.saving_throws_input = QLineEdit()
        self.damage_resistance_input = QLineEdit()
        self.damage_immunities_input = QLineEdit()
        self.condition_immunities_input = QLineEdit()
        self.languages_input = QLineEdit()
        self.senses_input = QLineEdit()
        self.challenge_rating_input = QLineEdit()
        self.equipment_input = QLineEdit()
        self.special_abilities_input = QLineEdit()

        # Spell slots
        self.spell_slots_input = [QLineEdit() for _ in range(9)]
        for slot in self.spell_slots_input:
            slot.setValidator(self.validator)

        #make a custom class to the label as bold text
        class BoldLabel(QLabel):
            def __init__(self, text):
                super().__init__(text)
                font = self.font()
                font.setBold(True)
                self.setFont(font)
        
        class GeneralDesInput(QWidget):
            """
            @brief Widget for dynamically adding/removing rows of (name, description) inputs for things such as actions.
            Each row has a label (e.g. "Legendary Action 1") in italics, then name label/input and description label/input lined up.
            The description input is a QTextEdit that shows 3 lines and wraps text.
            """
            def __init__(self, label="Legendary Action", parent=None):
                super().__init__(parent)
                self.label = label
                self.layout = QVBoxLayout(self)
                self.input_rows = []  # List of (name_input, description_input, row_widgets) tuples

                #self.add_row()  # Add initial row

                # Add/Remove buttons in a horizontal layout
                button_row = QHBoxLayout()
                self.add_button = QPushButton(f"Add {label}")
                self.remove_button = QPushButton("Remove")
                self.add_button.clicked.connect(self.add_row)
                self.remove_button.clicked.connect(self.remove_row)
                button_row.addWidget(self.add_button)
                button_row.addWidget(self.remove_button)
                self.layout.addLayout(button_row)

            def add_row(self):
                row_index = len(self.input_rows) + 1

                # Italic label row
                italic_label = QLabel(f"{self.label} {row_index}")
                font = italic_label.font()
                font.setItalic(True)
                italic_label.setFont(font)
                italic_label_row = QWidget()
                italic_label_layout = QHBoxLayout(italic_label_row)
                italic_label_layout.addWidget(italic_label)
                italic_label_layout.addStretch()

                # Name and Description row (lined up)
                row_widget = QWidget()
                row_layout = QGridLayout(row_widget)
                name_label = QLabel("Name:")
                name_input = QLineEdit()
                desc_label = QLabel("Description:")
                description_input = QTextEdit()
                description_input.setFixedHeight(60)  # Show about 3 lines
                description_input.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                description_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)

                row_layout.addWidget(name_label, 0, 0)
                row_layout.addWidget(name_input, 0, 1)
                row_layout.addWidget(desc_label, 1, 0)
                row_layout.addWidget(description_input, 1, 1)

                # Insert both rows above the button row
                insert_pos = self.layout.count() - 1
                self.layout.insertWidget(insert_pos, italic_label_row)
                self.layout.insertWidget(insert_pos + 1, row_widget)

                self.input_rows.append((name_input, description_input, (italic_label_row, row_widget)))

            def remove_row(self):
                if self.input_rows:
                    name_input, description_input, widgets = self.input_rows.pop()
                    for widget in widgets:
                        widget.setParent(None)
                    # Optionally, you could update the labels to reflect new numbering

            def get_inputs(self):
                """
                @return a list of CharacterRow.GeneralDes objects from all input rows.
                """
                tempList = []               #create a blank list to hold all the inputs
                #cycle through all of the objects in the input_Rows list
                for temp in self.input_rows:
                    tempGR = CharacterRow.GeneralDes()  #create a blank GeneralDes object
                    tempGR.name = temp[0].text()   #get the text from the name input
                    tempGR.description = temp[1].toPlainText() #get the text from the description input
                    #if there was something input, add it to the list
                    if tempGR.name or tempGR.description:
                        tempList.append(tempGR)
                return tempList
        
        class SpellDesInput(QWidget):
            """
            @brief Widget for dynamically adding/removing rows of (name, description) inputs.
            Each row has a label (e.g. "Legendary Action 1") in italics, then name label/input and description label/input lined up.
            The description input is a QTextEdit that shows 3 lines and wraps text.
            """
            def __init__(self, label="Spell", parent=None):
                super().__init__(parent)
                self.label = label
                self.layout = QVBoxLayout(self)
                self.input_rows = []  # List of (name_input, description_input, row_widgets) tuples

                #self.add_row()  # Add initial row

                # Add/Remove buttons in a horizontal layout
                button_row = QHBoxLayout()
                self.add_button = QPushButton(f"Add {label}")
                self.remove_button = QPushButton("Remove")
                self.add_button.clicked.connect(self.add_row)
                self.remove_button.clicked.connect(self.remove_row)
                button_row.addWidget(self.add_button)
                button_row.addWidget(self.remove_button)
                self.layout.addLayout(button_row)

            def add_row(self):
                row_index = len(self.input_rows) + 1

                # Italic label row
                italic_label = QLabel(f"{self.label} {row_index}")
                font = italic_label.font()
                font.setItalic(True)
                italic_label.setFont(font)
                italic_label_row = QWidget()
                italic_label_layout = QHBoxLayout(italic_label_row)
                italic_label_layout.addWidget(italic_label)
                italic_label_layout.addStretch()

                # Name and Description row (lined up)
                row_widget = QWidget()
                row_layout = QGridLayout(row_widget)
                level_label = QLabel("Level:")
                level_input = QLineEdit()
                level_input.setValidator(QIntValidator())
                name_label = QLabel("Name:")
                name_input = QLineEdit()
                desc_label = QLabel("Description:")
                description_input = QTextEdit()
                description_input.setFixedHeight(60)  # Show about 3 lines
                description_input.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                description_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)
                times_per_day_label = QLabel("Times per day:")
                times_per_day_input = QLineEdit()
                times_per_day_input.setValidator(QIntValidator())

                row_layout.addWidget(level_label, 0, 0)
                row_layout.addWidget(level_input, 0, 1)
                row_layout.addWidget(name_label, 1, 0)
                row_layout.addWidget(name_input, 1, 1)
                row_layout.addWidget(desc_label, 2, 0)
                row_layout.addWidget(description_input, 2, 1)
                row_layout.addWidget(times_per_day_label, 3, 0)
                row_layout.addWidget(times_per_day_input, 3, 1)
                

                # Insert both rows above the button row
                insert_pos = self.layout.count() - 1
                self.layout.insertWidget(insert_pos, italic_label_row)
                self.layout.insertWidget(insert_pos + 1, row_widget)

                self.input_rows.append((level_input, name_input, description_input, times_per_day_input, (italic_label_row, row_widget)))

            def remove_row(self):
                if self.input_rows:
                    level_input, name_input, description_input, times_per_day_input, widgets = self.input_rows.pop()
                    for widget in widgets:
                        widget.setParent(None)
                    # Optionally, you could update the labels to reflect new numbering

            def get_inputs(self):
                """
                @return a list of CharacterRow.SpellDes objects from all input rows.
                """
                tempList = []           #create a blank list to hold all the inputs
                #cycle through all of the objects in the input_Rows list
                for temp in self.input_rows:
                    tempCR = CharacterRow.SpellsDes() #create a blank SpellDes object
                    #attempt to convert the level input to an integer
                    try:
                        tempCR.spell_level = int(temp[0].text())  #get the text from the level input
                    except ValueError:
                        tempCR.spell_level = 0  #set to 0 if it failed
                    tempCR.spell_name = temp[1].text()      #get the spell name from the name input
                    tempCR.spell_description = temp[2].toPlainText() #get the text from the description input
                    #attempt to convert the times per day input to an integer
                    try:
                        tempCR.times_per_day = int(temp[3].text())  #get the text from the level input
                    except ValueError:
                        tempCR.times_per_day = 0 #set to 0 if it failed
                    #add tempCR to the list only if something was input
                    if tempCR.spell_level or tempCR.spell_name or tempCR.spell_description or tempCR.times_per_day: #only add if something was input
                        tempList.append(tempCR)
                return tempList
                
        self.form_layout.addRow(BoldLabel("URL"), self.url_input)
        self.form_layout.addRow(BoldLabel("Name:"), self.name_input)
        self.form_layout.addRow(BoldLabel("Armor Class:"), self.armor_class_input)
        self.form_layout.addRow(BoldLabel("Max HP:"), self.max_hp_input)
        
        self.form_layout.addRow(BoldLabel("Speed:"), None)
        # set up the speed inputs
        speed_widget = QWidget()
        speed_layout = QGridLayout(speed_widget)
        speed_layout.addWidget(QLabel("\tWalk"), 0, 0)
        speed_layout.addWidget(self.speed_input_walk, 0, 1)
        speed_layout.addWidget(QLabel("\tFly"), 1, 0)
        speed_layout.addWidget(self.speed_input_fly, 1, 1)
        speed_layout.addWidget(QLabel("\tSwim"), 2, 0)
        speed_layout.addWidget(self.speed_input_swim, 2, 1)
        speed_layout.addWidget(QLabel("\tClimb"), 3, 0)
        speed_layout.addWidget(self.speed_input_climb, 3, 1)
        speed_layout.addWidget(QLabel("\tBurrow"), 4, 0)
        speed_layout.addWidget(self.speed_input_burrow, 4, 1)
        self.form_layout.addRow(speed_widget)
        
        self.form_layout.addRow(BoldLabel("Strength:"), self.strength_input)
        self.form_layout.addRow(BoldLabel("Dexterity:"), self.dexterity_input)
        self.form_layout.addRow(BoldLabel("Constitution:"), self.constitution_input)
        self.form_layout.addRow(BoldLabel("Intelligence:"), self.intelligence_input)
        self.form_layout.addRow(BoldLabel("Wisdom:"), self.wisdom_input)
        self.form_layout.addRow(BoldLabel("Charisma:"), self.charisma_input)
        #######
        self.form_layout.addRow(BoldLabel("Background:"), self.background_input)
        self.form_layout.addRow(BoldLabel("Class:"), self.class_input)
        self.form_layout.addRow(BoldLabel("Species:"), self.species_input)
        self.form_layout.addRow(BoldLabel("Subclass:"), self.subclass_input)
        self.form_layout.addRow(BoldLabel("Level:"), self.level_input)
        self.form_layout.addRow(BoldLabel("Hit Dice:"), self.hit_dice_input)
        self.form_layout.addRow(BoldLabel("Proficiency Bonus:"), self.proficiency_bonus_input)
        self.form_layout.addRow(BoldLabel("Initiative Bonus:"), self.initiative_bonus_input)
        self.form_layout.addRow(BoldLabel("Size:"), self.size_input)
        self.form_layout.addRow(BoldLabel("Passive Perception:"), self.passive_perception_input)
        self.form_layout.addRow(BoldLabel("Temporary Hit Points:"), self.temporary_hit_points_input)
        self.form_layout.addRow(BoldLabel("Arcana:"), self.arcana_input)
        self.form_layout.addRow(BoldLabel("History:"), self.history_input)
        self.form_layout.addRow(BoldLabel("Investigation:"), self.investigation_input)
        self.form_layout.addRow(BoldLabel("Nature:"), self.nature_input)
        self.form_layout.addRow(BoldLabel("Religion:"), self.religion_input)
        self.form_layout.addRow(BoldLabel("Athletics:"), self.athletics_input)
        self.form_layout.addRow(BoldLabel("Acrobatics:"), self.acrobatics_input)
        self.form_layout.addRow(BoldLabel("Sleight of Hand:"), self.sleight_of_hand_input)
        self.form_layout.addRow(BoldLabel("Stealth:"), self.stealth_input)
        self.form_layout.addRow(BoldLabel("Animal Handling:"), self.animal_handling_input)
        self.form_layout.addRow(BoldLabel("Insight:"), self.insight_input)
        self.form_layout.addRow(BoldLabel("Medicine:"), self.medicine_input)
        self.form_layout.addRow(BoldLabel("Perception:"), self.perception_input)
        self.form_layout.addRow(BoldLabel("Survival:"), self.survival_input)
        self.form_layout.addRow(BoldLabel("Deception:"), self.deception_input)
        self.form_layout.addRow(BoldLabel("Intimidation:"), self.intimidation_input)
        self.form_layout.addRow(BoldLabel("Performance:"), self.performance_input)
        self.form_layout.addRow(BoldLabel("Persuasion:"), self.persuasion_input)
        self.form_layout.addRow(BoldLabel("Saving Throws:"), self.saving_throws_input)
        self.form_layout.addRow(BoldLabel("Damage Resistance:"), self.damage_resistance_input)
        self.form_layout.addRow(BoldLabel("Damage Immunities:"), self.damage_immunities_input)
        self.form_layout.addRow(BoldLabel("Condition Immunities:"), self.condition_immunities_input)
        self.form_layout.addRow(BoldLabel("Languages:"), self.languages_input)
        self.form_layout.addRow(BoldLabel("Senses:"), self.senses_input)
        self.form_layout.addRow(BoldLabel("Challenge Rating:"), self.challenge_rating_input)
        self.form_layout.addRow(BoldLabel("Equipment:"), self.equipment_input)
        self.form_layout.addRow(BoldLabel("Special Abilities:"), self.special_abilities_input)
        #form_layout.addRow(BoldLabel("Spells:"), spells_input)
        #add in things that have severl rows of inputs
        self.form_layout.addRow(BoldLabel("Feats:"), None)
        self.feats_inputs = GeneralDesInput(label="Feat")
        self.form_layout.addRow(self.feats_inputs)
        self.form_layout.addRow(BoldLabel("Actions:"), None)
        self.actions_inputs = GeneralDesInput(label="Action")
        self.form_layout.addRow(self.actions_inputs)
        self.form_layout.addRow(BoldLabel("Bonus Actions:"), None)
        self.bonus_actions_inputs = GeneralDesInput(label="Bonus Action")
        self.form_layout.addRow(self.bonus_actions_inputs)
        self.form_layout.addRow(BoldLabel("Reactions:"), None)
        self.reactions_inputs = GeneralDesInput(label="Reaction")
        self.form_layout.addRow(self.reactions_inputs)
        self.form_layout.addRow(BoldLabel("Legendary Actions:"), None)
        self.legendary_actions_inputs = GeneralDesInput(label="Legendary Action")
        self.form_layout.addRow(self.legendary_actions_inputs)
        #spell Slots
        self.form_layout.addRow(BoldLabel("Spell Slots:"), None)
        # set up the speed inputs
        spell_widget = QWidget()
        spell_layout = QGridLayout(spell_widget)
        spell_layout.addWidget(QLabel("\tLevel 1: "), 0, 0)
        spell_layout.addWidget(self.spell_slots_input[0], 0, 1)
        spell_layout.addWidget(QLabel("\tLevel 2: "), 1, 0)
        spell_layout.addWidget(self.spell_slots_input[1], 1, 1)
        spell_layout.addWidget(QLabel("\tLevel 3: "), 2, 0)
        spell_layout.addWidget(self.spell_slots_input[2], 2, 1)
        spell_layout.addWidget(QLabel("\tLevel 4: "), 3, 0)
        spell_layout.addWidget(self.spell_slots_input[3], 3, 1)
        spell_layout.addWidget(QLabel("\tLevel 5: "), 4, 0)
        spell_layout.addWidget(self.spell_slots_input[4], 4, 1)
        spell_layout.addWidget(QLabel("\tLevel 6: "), 5, 0)
        spell_layout.addWidget(self.spell_slots_input[5], 5, 1)
        spell_layout.addWidget(QLabel("\tLevel 7: "), 6, 0)
        spell_layout.addWidget(self.spell_slots_input[6], 6, 1)
        spell_layout.addWidget(QLabel("\tLevel 8: "), 7, 0)
        spell_layout.addWidget(self.spell_slots_input[7], 7, 1)
        spell_layout.addWidget(QLabel("\tLevel 9: "), 8, 0)
        spell_layout.addWidget(self.spell_slots_input[8], 8, 1)
        self.form_layout.addRow(spell_widget)
        
        self.form_layout.addRow(BoldLabel("Spells:"), None)
        self.spells_inputs = SpellDesInput(label="Spell")
        self.form_layout.addRow(self.spells_inputs)

    def get_character_data(self):
        """
        Return a CharacterRow object with all input values.
        """
        def readInt(string):
            """
            @brief Read an integer from a QLineEdit, returning 0 if invalid.
            @param inputFeild The QLineEdit to read from.
            @return The integer value or 0 if invalid.
            """
            try:
                return int(string)
            except ValueError:
                return 0
        
        #build a character object from the inputs
        tempChar = CharacterRow()   #make a blank object to return
        tempChar.character_url = self.url_input.text()
        tempChar.Character_Name = self.name_input.text()
        tempChar.Armor_Class = readInt(self.armor_class_input.text())
        tempChar.Max_HP = readInt(self.max_hp_input.text())
        tempChar.Current_HP = readInt(self.max_hp_input.text())
        tempChar.Walk_Speed = readInt(self.speed_input_walk.text())
        tempChar.Fly_Speed = readInt(self.speed_input_fly.text())    
        tempChar.Swim_Speed = readInt(self.speed_input_swim.text())
        tempChar.Climb_Speed = readInt(self.speed_input_climb.text())
        tempChar.Burrow_Speed = readInt(self.speed_input_burrow.text())
        tempChar.Strength = readInt(self.strength_input.text())
        tempChar.Dexterity = readInt(self.dexterity_input.text())
        tempChar.Constitution = readInt(self.constitution_input.text())
        tempChar.Intelligence = readInt(self.intelligence_input.text())
        tempChar.Wisdom = readInt(self.wisdom_input.text())
        tempChar.Charisma = readInt(self.charisma_input.text())
        tempChar.Background = self.background_input.text()
        tempChar.Class = self.class_input.text()
        tempChar.Species = self.species_input.text()
        tempChar.Subclass = self.subclass_input.text()
        tempChar.Level = readInt(self.level_input.text())
        tempChar.Hit_Dice = self.hit_dice_input.text()
        tempChar.Proficiency_Bonus = readInt(self.proficiency_bonus_input.text())
        tempChar.Initiative_Bonus = readInt(self.initiative_bonus_input.text())  
        tempChar.Size = self.size_input.text()
        tempChar.Passive_Perception = readInt(self.passive_perception_input.text())
        tempChar.Temporary_Hit_Points = readInt(self.temporary_hit_points_input.text())
        tempChar.Arcana = readInt(self.arcana_input.text())
        tempChar.History = readInt(self.history_input.text())
        tempChar.Investigation = readInt(self.investigation_input.text())
        tempChar.Nature = readInt(self.nature_input.text())
        tempChar.Religion = readInt(self.religion_input.text())
        tempChar.Athletics = readInt(self.athletics_input.text())
        tempChar.Acrobatics = readInt(self.acrobatics_input.text())
        tempChar.Sleight_of_Hand = readInt(self.sleight_of_hand_input.text())
        tempChar.Stealth = readInt(self.stealth_input.text())
        tempChar.Animal_Handling = readInt(self.animal_handling_input.text())
        tempChar.Insight = readInt(self.insight_input.text())
        tempChar.Medicine = readInt(self.medicine_input.text())
        tempChar.Perception = readInt(self.perception_input.text())
        tempChar.Survival = readInt(self.survival_input.text())
        tempChar.Deception = readInt(self.deception_input.text())
        tempChar.Intimidation = readInt(self.intimidation_input.text())
        tempChar.Performance = readInt(self.performance_input.text())
        tempChar.Persuasion = readInt(self.persuasion_input.text())
        tempChar.Saving_Throws = self.saving_throws_input.text()
        tempChar.Damage_Resistance = self.damage_resistance_input.text()
        tempChar.Damage_Immunities = self.damage_immunities_input.text()
        tempChar.Condition_Immunities = self.condition_immunities_input.text()
        tempChar.Languages = self.languages_input.text()
        tempChar.Senses = self.senses_input.text()
        tempChar.Challenge_Rating = self.challenge_rating_input.text()
        tempChar.Equipment = self.equipment_input.text()
        tempChar.Special_Abilities = self.special_abilities_input.text()
        tempChar.Spells = self.spells_inputs.get_inputs()  # List of (level, name, description, times_per_day)
        tempChar.Spell_Slots = [int(slot.text()) if slot.text().isdigit() else 0 for slot in self.spell_slots_input]  # List of integers
        tempChar.Feats = self.feats_inputs.get_inputs()  # List of (name, description
        tempChar.Actions = self.actions_inputs.get_inputs()  # List of (name, description)
        tempChar.Bonus_Actions = self.bonus_actions_inputs.get_inputs()  # List of (
        tempChar.Reactions = self.reactions_inputs.get_inputs()  # List of (name, description)
        tempChar.Legendary_Actions = self.legendary_actions_inputs.get_inputs()  # List of (name, description)
        
        #return the built character object
        return tempChar

    def set_character_data(self, character_row = CharacterRow()):
        """
        Set all input fields from a CharacterRow object.
        """
        self.url_input.setText(character_row.character_url)
        self.name_input.setText(character_row.Character_Name)
        self.armor_class_input.setText(str(character_row.Armor_Class))
        self.max_hp_input.setText(str(character_row.Max_HP))
        self.speed_input_walk.setText(str(character_row.Walk_Speed))
        self.speed_input_fly.setText(str(character_row.Fly_Speed))
        self.speed_input_swim.setText(str(character_row.Swim_Speed))
        self.speed_input_climb.setText(str(character_row.Climb_Speed))
        self.speed_input_burrow.setText(str(character_row.Burrow_Speed))
        self.strength_input.setText(str(character_row.Strength))
        self.dexterity_input.setText(str(character_row.Dexterity))
        self.constitution_input.setText(str(character_row.Constitution))
        self.intelligence_input.setText(str(character_row.Intelligence))
        self.wisdom_input.setText(str(character_row.Wisdom))
        self.charisma_input.setText(str(character_row.Charisma))
        self.background_input.setText(character_row.Background)
        self.class_input.setText(character_row.Class)
        self.species_input.setText(character_row.Species)
        self.subclass_input.setText(character_row.Subclass)
        self.level_input.setText(str(character_row.Level))
        self.hit_dice_input.setText(character_row.Hit_Dice)
        self.proficiency_bonus_input.setText(str(character_row.Proficiency_Bonus))
        self.initiative_bonus_input.setText(str(character_row.Initiative_Bonus))
        self.size_input.setText(character_row.Size)
        self.passive_perception_input.setText(str(character_row.Passive_Perception))
        self.temporary_hit_points_input.setText(str(character_row.Temporary_Hit_Points))
        self.arcana_input.setText(str(character_row.Arcana))
        self.history_input.setText(str(character_row.History))
        self.investigation_input.setText(str(character_row.Investigation))
        self.nature_input.setText(str(character_row.Nature))
        self.religion_input.setText(str(character_row.Religion))
        self.athletics_input.setText(str(character_row.Athletics))
        self.acrobatics_input.setText(str(character_row.Acrobatics))
        self.sleight_of_hand_input.setText(str(character_row.Sleight_of_Hand))
        self.stealth_input.setText(str(character_row.Stealth))
        self.animal_handling_input.setText(str(character_row.Animal_Handling))
        self.insight_input.setText(str(character_row.Insight))
        self.medicine_input.setText(str(character_row.Medicine))
        self.perception_input.setText(str(character_row.Perception))
        self.survival_input.setText(str(character_row.Survival))
        self.deception_input.setText(str(character_row.Deception))
        self.intimidation_input.setText(str(character_row.Intimidation))
        self.performance_input.setText(str(character_row.Performance))
        self.persuasion_input.setText(str(character_row.Persuasion))
        self.saving_throws_input.setText(character_row.Saving_Throws)
        self.damage_resistance_input.setText(character_row.Damage_Resistance)
        self.languages_input.setText(character_row.Languages)
        self.challenge_rating_input.setText(character_row.Challenge_Rating)
        self.equipment_input.setText(character_row.Equipment)
        self.special_abilities_input.setText(character_row.Special_Abilities)
       
        self.spells_inputs.input_rows.clear()
        for i in reversed(range(self.spells_inputs.layout.count() - 1)):
            widget = self.spells_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for spell in character_row.Spells:
            self.spells_inputs.add_row()
            if self.spells_inputs.input_rows:
                last_row = self.spells_inputs.input_rows[-1]
                last_row[0].setText(str(spell.spell_level))
                last_row[1].setText(spell.spell_name)
                last_row[2].setPlainText(spell.spell_description)
                last_row[3].setText(str(spell.times_per_day))
        # Set feats, actions, bonus actions, reactions, legendary actions
        self.feats_inputs.input_rows.clear()
        for i in reversed(range(self.feats_inputs.layout.count() - 1)):
            widget = self.feats_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for feat in character_row.Feats:
            self.feats_inputs.add_row()
            if self.feats_inputs.input_rows:
                last_row = self.feats_inputs.input_rows[-1]
                last_row[0].setText(feat.name)
                last_row[1].setPlainText(feat.description)
        self.actions_inputs.input_rows.clear()
        for i in reversed(range(self.actions_inputs.layout.count() - 1)):
            widget = self.actions_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for action in character_row.Actions:
            self.actions_inputs.add_row()
            if self.actions_inputs.input_rows:
                last_row = self.actions_inputs.input_rows[-1]
                last_row[0].setText(action.name)
                last_row[1].setPlainText(action.description)
        self.bonus_actions_inputs.input_rows.clear()
        for i in reversed(range(self.bonus_actions_inputs.layout.count() - 1)):
            widget = self.bonus_actions_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for bonus_action in character_row.Bonus_Actions:
            self.bonus_actions_inputs.add_row()
            if self.bonus_actions_inputs.input_rows:
                last_row = self.bonus_actions_inputs.input_rows[-1]
                last_row[0].setText(bonus_action.name)
                last_row[1].setPlainText(bonus_action.description)
        self.reactions_inputs.input_rows.clear()
        for i in reversed(range(self.reactions_inputs.layout.count() - 1)):
            widget = self.reactions_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for reaction in character_row.Reactions:
            self.reactions_inputs.add_row()
            if self.reactions_inputs.input_rows:
                last_row = self.reactions_inputs.input_rows[-1]
                last_row[0].setText(reaction.name)
                last_row[1].setPlainText(reaction.description)
        self.legendary_actions_inputs.input_rows.clear()
        for i in reversed(range(self.legendary_actions_inputs.layout.count() - 1)):
            widget = self.legendary_actions_inputs.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for legendary_action in character_row.Legendary_Actions:
            self.legendary_actions_inputs.add_row()
            if self.legendary_actions_inputs.input_rows:
                last_row = self.legendary_actions_inputs.input_rows[-1]
                last_row[0].setText(legendary_action.name)
                last_row[1].setPlainText(legendary_action.description)
                
        # ... set all other fields ...
        # For dynamic widgets, you may want to clear and re-add rows based on the data
        # Example:
        # self.feats_inputs.set_inputs(character_row.Feats)
        # self.actions_inputs.set_inputs(character_row.Actions)
        # ... etc ...
        for i, slot in enumerate(self.spell_slots_input):
            slot.setText(str(character_row.Spell_Slots[i]) if i < len(character_row.Spell_Slots) else "0")
        # ... set all other fields ...

class CharacterSelectionWindow(QDialog):
    """
    @class CharacterSelectionWindow
    @brief Dialog window for selecting, adding, and modifying characters from XML files.
    """
    master_character_list = []  # list to hold all characters from the xml file
    character_folder = "./Settings/Characters/"  # folder where character XML files are stored
    
    def __init__(self, parent=None):
        """
        @brief Constructor for CharacterSelectionWindow.
        @param parent The parent widget.
        Initializes the UI, menu bar, character lists, and loads XML files.
        """
        super().__init__(parent)
        self.setWindowTitle("Select Characters")
        self.setGeometry(200, 200, 600, 400)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Menu bar
        self.menu_bar = QMenuBar(self)
        
        # New file option
        new_menu = QMenu("New", self)
        self.new_file_action = new_menu.addAction("Character File")
        self.new_file_action.triggered.connect(self.new_character_file)
        self.menu_bar.addMenu(new_menu)
        
        # Add and modify character option
        add_menu = QMenu("Add/Remove", self)
        self.add_character_action = add_menu.addAction("Add New Character")
        self.add_character_action.triggered.connect(self.open_add_character_window)
        self.menu_bar.addMenu(add_menu)
        self.add_character_action.setEnabled(False)  # Initially disabled
        
        self.modify_character_action = add_menu.addAction("Modify Character")
        self.modify_character_action.setEnabled(False)  # Initially disabled
        self.modify_character_action.triggered.connect(self.open_modify_character_window)
        
        self.remove_character_action = add_menu.addAction("Remove Character")
        self.remove_character_action.setEnabled(False)  # Initially disabled
        self.remove_character_action.triggered.connect(self.open_remove_character_window)
        
        update_menue = QMenu("Update Files", self)
        self.update_menue_action = update_menue.addAction("Update Character File")
        self.update_menue_action.triggered.connect(self.update_character_files)
        self.menu_bar.addMenu(update_menue)
        
        main_layout.setMenuBar(self.menu_bar)  # Add the menu bar to the dialog

        # Layouts for the rest of the UI
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Combo box to select XML files
        self.file_combo = QComboBox()
        self.file_combo.addItem("Select a file")
        self.file_combo.currentTextChanged.connect(self.load_character_names_into_comboBox)
        self.file_combo.currentTextChanged.connect(self.update_menu_state)
        left_layout.addWidget(QLabel("Select Character File:"))
        left_layout.addWidget(self.file_combo)
        
        #search box for the different characters
        left_layout.addWidget(QLabel("Search Characters:"))
        self.search_input = QLineEdit()
        self.search_input.setEnabled(False)  # Initially disabled
        left_layout.addWidget(self.search_input)

        # List of characters in the selected file
        self.character_list = QListWidget()
        self.character_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.character_list.itemDoubleClicked.connect(self.add_character_from_double_click)
        left_layout.addWidget(QLabel("Available Characters:"))
        left_layout.addWidget(self.character_list)

        # Add to game button
        self.add_button = QPushButton("Add")
        self.add_button.setEnabled(False)  # Initially disabled
        self.add_button.clicked.connect(self.add_butt)
        left_layout.addWidget(self.add_button)

        # List of characters to be added to the game
        self.selected_characters_list = QListWidget()
        self.selected_characters_list.itemDoubleClicked.connect(self.remove_character_from_double_click)  # Connect double-click signal
        right_layout.addWidget(QLabel("Characters to Add:"))
        right_layout.addWidget(self.selected_characters_list)

        # Add and Cancel buttons
        self.add_to_game_button = QPushButton("Add to Game")
        self.add_to_game_button.clicked.connect(self.accept)
        self.add_to_game_button.setEnabled(False)  # Initially disabled
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        right_layout.addWidget(self.add_to_game_button)
        right_layout.addWidget(self.cancel_button)

        # Add layouts to the content layout
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        # Add the content layout to the main layout
        main_layout.addLayout(content_layout)

        # Load XML files from the directory
        self.load_xml_files()

        # Store selected characters
        self.selected_characters = []
        
        """
        @brief filter the character list based on search input.
        @param text with the information to search for
        """
        def filter_list(text):
            self.character_list.clear()     #clear the combo box
            #for each name in the list of characters
            for name in self.master_character_list:
                #set all of the text to loweer case and look for any matches
                if text.lower() in name.lower() or not text:
                    self.character_list.addItem(name)   #add the item to the list shown so it can be selected

        self.search_input.textChanged.connect(filter_list)
        
        


    """
    @brief Load XML files from the ./Settings/Characters directory into the combo box.
    Creates the directory if it does not exist.
    @param self this object
    """
    def load_xml_files(self):
        directory = "./Settings/Characters"
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it doesn't exist
        for file in os.listdir(directory):
            if file.endswith(".xml"):
                self.file_combo.addItem(file)

    """
    @brief Enable or disable menu options based on file selection.
    @param self this object
    @param file_name The currently selected file name in the combo box.
    """
    def update_menu_state(self, file_name):
        if file_name == "Select a file":
            self.add_character_action.setEnabled(False)
            self.modify_character_action.setEnabled(False)
            self.remove_character_action.setEnabled(False)
            self.add_button.setEnabled(False)
            self.add_to_game_button.setEnabled(False)
            self.search_input.setEnabled(False)
        else:
            self.add_character_action.setEnabled(True)
            self.modify_character_action.setEnabled(True)
            self.remove_character_action.setEnabled(True)
            self.add_button.setEnabled(True)
            self.add_to_game_button.setEnabled(True)
            self.search_input.setEnabled(True)
    
    """
    @brief OPen a dialog to create a new character XML file.
    @param self this object
    """
    def new_character_file(self):
        new_file_dialog = QDialog(self)
        new_file_dialog.setWindowTitle("Create New Character File")
        new_file_dialog.setGeometry(300, 300, 300, 100)

        layout = QVBoxLayout(new_file_dialog)

        file_name_input = QLineEdit()
        file_name_input.setPlaceholderText("Enter new file name (without .xml)")
        layout.addWidget(file_name_input)

        button_layout = QHBoxLayout()
        create_button = QPushButton("Create")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def create_file():
            file_name = file_name_input.text().strip()
            if not file_name:
                QMessageBox.warning(new_file_dialog, "Invalid Input", "File name cannot be empty.")
                return
            if not file_name.endswith(".xml"):
                file_name += ".xml"
            file_path = os.path.join("./Settings/Characters", file_name)
            if os.path.exists(file_path):
                QMessageBox.warning(new_file_dialog, "File Exists", "A file with that name already exists.")
                return
            try:
                # Create a new XML file with a root element
                root = ET.Element("characters")
                tree = ElementTree(root)
                tree.write(file_path, encoding="unicode", xml_declaration=True)
                self.file_combo.addItem(file_name)
                self.file_combo.setCurrentText(file_name)  # Select the newly created file
                QMessageBox.information(new_file_dialog, "Success", f"File '{file_name}' created successfully!")
                new_file_dialog.accept()
            except Exception as e:
                QMessageBox.critical(new_file_dialog, "Error", f"Failed to create file: {e}")

        create_button.clicked.connect(create_file)
        cancel_button.clicked.connect(new_file_dialog.reject)

        new_file_dialog.exec()

    """
    @brief Update the character XML files by fetching new data from github.
    @param self this object
    """
    def update_character_files(self):
        reply = QMessageBox.question(None, "Update Characters", "Do you want to update all character files from GitHub? This will overide anyfiles that have the same name as those on github", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            git_hub_downloader = GitHubDownloader()
            #error = git_hub_downloader.git_extract_folder(silent=True, folder_path=os.path.join(os.path.dirname(__file__), "Settings", "Characters"))
            succ = git_hub_downloader.git_extract_folder(silent=False, folder_path="Settings/Characters")
            if succ == False:
                #show an error message
                QMessageBox.critical(None, "Error", "Failed to download character files from GitHub.")
                return
            else:
                #copy the character files from the downloaded repo to the character folder
                source_folder = os.path.join(git_hub_downloader.downloaded_repo_path, "Settings/Characters")
                dest_folder = self.character_folder
                try:
                    for file_name in os.listdir(source_folder):
                        if file_name.endswith(".xml"):
                            full_file_name = os.path.join(source_folder, file_name)
                            if os.path.isfile(full_file_name):
                                shutil.copy(full_file_name, dest_folder)
                    QMessageBox.information(None, "Success", "Character files updated successfully from GitHub.")
                    #reload the xml files
                    # Prevent currentTextChanged signals firing while we reset the combo box
                    self.file_combo.blockSignals(True)
                    self.file_combo.clear()
                    self.file_combo.addItem("Select a file")
                    self.file_combo.setCurrentText("Select a file")
                    self.file_combo.blockSignals(False)
                    # Now safely reload files
                    self.load_xml_files()
                except Exception as e:
                    QMessageBox.critical(None, "Error", f"Failed to update character files: {e}")
    
    """
    @brief Open a dialog window to add a new character to the selected XML file.
    """
    def open_add_character_window(self):
        
        if self.file_combo.currentText() == "Select a file":
            QMessageBox.warning(self, "No File Selected", "Please select an XML file first.")
            return

        add_character_dialog = QDialog(self)
        add_character_dialog.setWindowTitle("Add New Character")
        add_character_dialog.setGeometry(300, 300, 400, 400)

        # Main layout for the dialog
        main_layout = QVBoxLayout(add_character_dialog)

        # Create a QWidget to hold the form layout
        form_widget = CharacterFormWidget()
        
        # Create a QScrollArea and set the form_widget as its widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)
        
        
        #**************************Functions**********************************************
        def save_character():
            """
            @brief Save the new character to the currently selected XML file.
            """
            
            #get a character object from the form inputs
            tempChar = form_widget.get_character_data()
            
            file_name = self.file_combo.currentText()
            file_path = os.path.join("./Settings/Characters", file_name)

            # Create a new character element
            character_name = tempChar.Character_Name
            if not character_name.strip():
                QMessageBox.warning(self, "Invalid Input", "Character name cannot be empty.")
                return

            # Check if a character with the same name already exists
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                for character in root.findall("character"):
                    existing_name = character.find("character_name").text
                    if existing_name == character_name:
                        QMessageBox.warning(self, "Duplicate Character", f"A character with the name '{character_name}' already exists.")
                        return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the XML file: {e}")
                return

            #Add the chracter to an xlml file    
            CFIO.write_character_information_to_xml(file_path, tempChar)
            #reload the list
            self.load_character_names_into_comboBox(file_name)
            #close the form
            add_character_dialog.done(0)
        
        # Save and Cancel buttons (outside scroll area)
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        # Connect buttons
        save_button.clicked.connect(save_character)
        cancel_button.clicked.connect(add_character_dialog.reject)

        add_character_dialog.exec()
    
    """
    @brief Open a dialog window to modify an existing character in the selected XML file.
    @param self this object
    """
    def open_modify_character_window(self):
        if self.file_combo.currentText() == "Select a file":
            QMessageBox.warning(self, "No File Selected", "Please select an XML file first.")
            return

        modify_character_dialog = QDialog(self)
        modify_character_dialog.setWindowTitle("Modify Character")
        modify_character_dialog.setGeometry(300, 300, 400, 400)

        # Main layout for the dialog
        main_layout = QVBoxLayout(modify_character_dialog)

        # Combo box to select an existing character (outside scroll area)
        file_name = self.file_combo.currentText()

        #get the character names from the selected file
        names = CFIO.load_character_names_xml(self.character_folder+file_name)
        
        main_layout.addWidget(QLabel("Select Character:"))
        search_input = QLineEdit()
        main_layout.addWidget(search_input)
        
        character_list_widget = QListWidget()
        character_list_widget.addItems(names)
        #fix the height of the list to show 3 items
        character_list_widget.setMinimumHeight(character_list_widget.sizeHintForRow(0) * 3 + 2 * character_list_widget.frameWidth())
        character_list_widget.setMaximumHeight(character_list_widget.sizeHintForRow(0) * 3 + 2 * character_list_widget.frameWidth())
        main_layout.addWidget(character_list_widget)
        
        # Create a QWidget to hold the form layout
        form_widget = CharacterFormWidget()
        
        # Create a QScrollArea and set the form_widget as its widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Save and Cancel buttons (outside scroll area)
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        #**************************Functions**********************************************
        # Live filtering
        def filter_list(text):
            character_list_widget.clear()
            for name in names:
                if text.lower() in name.lower() or not text:
                    character_list_widget.addItem(name)

        search_input.textChanged.connect(filter_list)
        
        def populate_fields():
            selected_items = character_list_widget.selectedItems()
            if selected_items:
                selected_name = selected_items[0].text()
                character_row = CFIO.load_character_information_xml(self.character_folder+file_name, selected_name)
                if character_row.Character_Name != "":
                    form_widget.set_character_data(character_row)
        
        character_list_widget.itemClicked.connect(lambda item: populate_fields())
        character_list_widget.itemDoubleClicked.connect(lambda item: populate_fields())
        search_input.returnPressed.connect(populate_fields)
        
        
        # Function to save the modified character
        def save_character():    
            """
            @brief Save the new character to the currently selected XML file.
            """
            #get a character object from the form inputs
            tempChar = form_widget.get_character_data()
            
            file_name = self.file_combo.currentText()
            file_path = os.path.join("./Settings/Characters", file_name)

            # Create a new character element
            character_name = tempChar.Character_Name
            if not character_name.strip():
                QMessageBox.warning(self, "Invalid Input", "Character name cannot be empty.")
                return

            # Check if a character with the same name already exists
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                nameFound = False
                for character in root.findall("character"):
                    existing_name = character.find("character_name").text
                    if existing_name == character_name:
                        QMessageBox.information(self, "Overriding Character", f"Overriding character '{character_name}'.")
                        nameFound = True
                        break
                #if the name was not found, show the generating new character message
                if (nameFound == False):
                    QMessageBox.information(self, "Creating new character", f"Creating new character: '{character_name}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the XML file: {e}")
                return

            #Add the chracter to an xlml file    
            CFIO.write_character_information_to_xml(file_path, tempChar)
            #reload the list
            self.load_character_names_into_comboBox(file_name)
            #close the form
            modify_character_dialog.done(0)
        
        

        # Connect buttons
        save_button.clicked.connect(save_character)
        cancel_button.clicked.connect(modify_character_dialog.reject)

        modify_character_dialog.exec()

    """
    @brief Show a confirmation dialog and remove selected characters from the XML file if confirmed.
    The dialog displays the number of selected characters.
    @param self this object
    """
    def open_remove_character_window(self):
        selected_items = self.character_list.selectedItems()
        count = len(selected_items)
        if count == 0:
            QMessageBox.warning(self, "No Selection", "Please select one or more characters to remove.")
            return

        reply = QMessageBox.question(
            self,
            "Remove Characters",
            f"Are you sure you want to remove {count} selected character{'s' if count > 1 else ''}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            file_name = self.file_combo.currentText()
            if file_name == "Select a file":
                QMessageBox.warning(self, "No File Selected", "Please select an XML file first.")
                return
            file_path = os.path.join("./Settings/Characters", file_name)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                names_to_remove = [item.text() for item in selected_items]
                for character in root.findall("character"):
                    name = character.find("character_name").text
                    if name in names_to_remove:
                        root.remove(character)
                indent(root)
                tree.write(file_path, encoding="unicode", xml_declaration=True)
                QMessageBox.information(self, "Success", "Selected characters removed successfully.")
                self.load_character_names_into_comboBox(file_name)  # Refresh the character list
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove characters: {e}")
        # If No is selected, do nothing
    
    """
    @brief Return the selected characters as a list of XML strings.
    @param self this object
    @return List of XML strings for the selected characters, or an empty list if cancelled.
    """
    def get_selected_characters(self):
        # Only return characters if the dialog was accepted
        if self.result() == QDialog.DialogCode.Accepted:
            characters = []
            file_name = self.file_combo.currentText()
            if file_name == "Select a file":
                return characters  # No file selected, return an empty list

            file_path = os.path.join("./Settings/Characters", file_name)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                for i in range(self.selected_characters_list.count()):
                    selected_name = self.selected_characters_list.item(i).text()
                    for character in root.findall("character"):
                        name = character.find("character_name").text
                        if name == selected_name:
                            # Convert the character element back to an XML string
                            character_xml = ET.tostring(character, encoding="unicode")
                            characters.append(character_xml)
                            break
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to retrieve character data: {e}")
            return characters
        else:
            # If the dialog was rejected or closed, return an empty list
            return []
    
    """
    @brief Return the selected characters as a list of CharacterRow objects.
    @details This function retrieves the selected characters from the 'Characters to Add' list,
            parses the XML file, and returns them as a list of CharacterRow objects with fields populated
            from the XML data matching the CharacterRow class attributes, including lists for spells, feats, actions, etc.
    @param self this object
    @return List of CharacterRow objects for the selected characters, or an empty list if cancelled.
    """
    def get_selected_characters_class(self):
        from rowdata import CharacterRow

        # Only return characters if the dialog was accepted
        if self.result() == QDialog.DialogCode.Accepted:
            character_rows = []
            file_name = self.file_combo.currentText()
            if file_name == "Select a file":
                return character_rows  # No file selected, return an empty list

            selected_names = [self.selected_characters_list.item(i).text() for i in range(self.selected_characters_list.count())]
            
            #loop through each selected character
            for name in selected_names:
                temp_character = CFIO.load_character_information_xml(self.character_folder+file_name, name)   #get the character data as a CharacterRow object
                #if there was no error loading in the charcter information then add it to the list
                if temp_character.Current_HP != -9999999999:
                    character_rows.append(temp_character)
                else:
                    #clear the list and exit the loop
                    character_rows.clear()
                    break
            
            return character_rows
        else:
            # If the dialog was rejected or closed, return an empty list
            return []
    
    #**************************Signal Handlers***********************************
    """
    @brief update the character names list with characters from the an file
    @param self this object
    @param name of the file to load the characters from. Assuming this file is in the ./Settings/Characters directory
    @retval list of character names
    """
    def load_character_names_into_comboBox(self, file_name):
        self.search_input.clear()                   #clear the search box
        self.character_list.clear()                 #clear the current names in the list
        self.master_character_list = CFIO.load_character_names_xml(self.character_folder+file_name)
        #if we found some names, add them to the list
        if self.master_character_list is not None:
            for name in self.master_character_list:
                self.character_list.addItem(name)
            self.character_list.sortItems()  # Sort alphabetically
    
    """
    @breif Move selected characters to the 'Characters to Add' list and clear the selection.
    """
    def add_butt(self):
        selected_items = self.character_list.selectedItems()
        self.selected_characters = []  # Clear the selected characters list
        for item in selected_items:
            self.selected_characters_list.addItem(item.text())
            self.selected_characters.append(item.text())  # Add the selected character to the list

        # Clear the selection in the Available Characters list
        self.character_list.clearSelection()
    
    """
    @brief Add a character to the 'Characters to Add' list by double-clicking.
    @param item The QListWidgetItem that was double-clicked.
    """
    def add_character_from_double_click(self, item):
        self.selected_characters_list.addItem(item.text())
        #self.character_list.takeItem(self.character_list.row(item))

    """
    @brief Remove a character from the 'Characters to Add' list by double-clicking.
    @param item The QListWidgetItem that was double-clicked.
    """
    def remove_character_from_double_click(self, item):
        #self.character_list.addItem(item.text())
        self.selected_characters_list.takeItem(self.selected_characters_list.row(item))
    
    #**************************Events**********************************************
    """
    @brief Ensure no characters are returned when the dialog is closed.
    @param event The close event.
    """
    def closeEvent(self, event):
        self.selected_characters = []  # Clear the selected characters list
        event.accept()  # Allow the window to close