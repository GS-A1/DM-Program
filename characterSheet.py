import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QGroupBox, QGridLayout, QFormLayout, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QLinearGradient, QBrush
from rowdata import CharacterRow
import rowDataFileIO as CFIO


class CharacterSheetWindow(QMainWindow):
    def __init__(self, character: CharacterRow):
        super().__init__()
        
        self.update_sheet(character)            #update the character data to the default character
        self.setGeometry(100, 100, 650, 850)    #draw the window in the default place with default size

    def scrollable(self, widget):
        """Wraps a tab in a scrollable container."""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent;")
        return scroll

    # ---------------------- PAGE 1: CORE STATS ---------------------- #
    def build_core_stats_tab(self):
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(2)

        header = QGridLayout()
        header.setVerticalSpacing(0)  # Reduce vertical gap between rows
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self.labeled_field("Player Name", self.character.Player_Name, True), 0, 0)
        header.addWidget(self.labeled_field("Character Name", self.character.Character_Name, True), 0, 1)
        layout.addLayout(header)

        defense_box = QGroupBox("Defense")
        defense_layout = QHBoxLayout()
        defense_layout.addWidget(self.labeled_field("AC", self.character.Armor_Class, True))
        defense_layout.addWidget(self.labeled_field("Max HP", self.character.Max_HP, True))
        defense_layout.addWidget(self.labeled_field("Temp. HP", self.character.Temporary_Hit_Points, True))
        defense_layout.addWidget(self.labeled_field("Curr HP", self.character.Current_HP, True))
        defense_layout.addWidget(self.labeled_field("Death Saves", self.character.Death_Saves, True))
        defense_layout.addWidget(self.labeled_field("Hit Dice", self.character.Hit_Dice, True))
        defense_box.setLayout(defense_layout)
        layout.addWidget(defense_box)
        
        speed_box = QGroupBox("Speed")
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.labeled_field("Walk", self.character.Walk_Speed, True, " ft."))
        speed_layout.addWidget(self.labeled_field("Burrow", self.character.Burrow_Speed, True, " ft."))
        speed_layout.addWidget(self.labeled_field("Climb", self.character.Climb_Speed, True, " ft."))
        speed_layout.addWidget(self.labeled_field("Fly", self.character.Fly_Speed, True, " ft."))
        speed_layout.addWidget(self.labeled_field("Swim", self.character.Swim_Speed, True, " ft."))
        speed_box.setLayout(speed_layout)
        layout.addWidget(speed_box)
        
        immunity_box = QGroupBox("Immunity")
        immunity_layout = QHBoxLayout()
        immunity_layout.addWidget(self.labeled_field("Damge Res.", self.character.Damage_Resistance, True))
        immunity_layout.addWidget(self.labeled_field("Damge Imun.", self.character.Damage_Immunities, True))
        immunity_layout.addWidget(self.labeled_field("Cond. Imun.", self.character.Condition_Immunities, True))
        immunity_layout.addWidget(self.labeled_field("Prof. Bonus", self.character.Proficiency_Bonus, True))
        immunity_box.setLayout(immunity_layout)
        layout.addWidget(immunity_box)
        
        other_box = QGroupBox("Other")
        other_layout = QHBoxLayout()
        other_layout.addWidget(self.labeled_field("Prof. Bonus", self.character.Proficiency_Bonus, True))
        if self.character.Spell_Save_DC == 0:
            self.character.Spell_Save_DC = "8 + Prof. Bonus + Spell Casting Ability Modifier"
        if self.character.Spell_Attack_Modifier == 0:
            self.character.Spell_Attack_Modifier = "Prof. Bonus + Spell Casting Ability Modifier"
        other_layout.addWidget(self.labeled_field("Spell Save DC", self.character.Spell_Save_DC, True))
        other_layout.addWidget(self.labeled_field("Spell Att. Mod.", self.character.Spell_Attack_Modifier, True))
        other_box.setLayout(other_layout)
        layout.addWidget(other_box)
        
        # Abilities
        abilities_box = QGroupBox("Ability Scores")
        grid = QGridLayout()
        abilities = {
            "Strength": self.character.Strength,
            "Dexterity": self.character.Dexterity,
            "Constitution": self.character.Constitution,
            "Intelligence": self.character.Intelligence,
            "Wisdom": self.character.Wisdom,
            "Charisma": self.character.Charisma,
        }
        row = 0
        for ability, value in abilities.items():
            grid.addWidget(self.ability_box(ability, value), row // 3, row % 3)
            row += 1
        abilities_box.setLayout(grid)
        layout.addWidget(abilities_box)

        #add in the url to the bottom if it exists
        if self.character.character_url:
            layout.addWidget(QLabel(f"Source: {self.character.character_url}"))
        
         # Add stretch to push content to the top
        
        layout.addStretch()
        return page

    # ---------------------- PAGE 2: FEATURES ---------------------- #    
    '''
    @breif Creates a QTextEdit formatted for CharacterRow.GeneralDes
    @param ls: list of GeneralDes to format
    @return QTextEdit formatted with bold names and descriptions
    '''
    def create_action_QTextEdit(self, ls):
        html_string = ""
        for a in ls:
            name = f"<b>{a.name}:</b>" if a.name else ""
            desc = a.description or ""
            html_string += f"{name} {desc}<br><br>"
        
        return self.create_QTextEdit(html_string)
    
    def build_features_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        #if there are Actions, show them
        if self.character.Actions:
            layout.addWidget(self.create_Heading_QLabel("ACTIONS"))
            layout.addWidget(self.create_action_QTextEdit(self.character.Actions))
        
        #if there are Bonus Actions, show them
        if self.character.Bonus_Actions:
            layout.addWidget(self.create_Heading_QLabel("BONUS ACTIONS"))
            layout.addWidget(self.create_action_QTextEdit(self.character.Bonus_Actions))
        
        #if there are Reactions, show them
        if self.character.Reactions:
            layout.addWidget(self.create_Heading_QLabel("REACTIONS"))
            layout.addWidget(self.create_action_QTextEdit(self.character.Reactions))
        
        #if there are Feats, show them
        if self.character.Feats:
            layout.addWidget(self.create_Heading_QLabel("FEATS"))
            layout.addWidget(self.create_action_QTextEdit(self.character.Feats))
        
        #if there are Legendary Actions, show them
        if self.character.Legendary_Actions:
            layout.addWidget(self.create_Heading_QLabel("LEGENDARY ACTIONS"))
            layout.addWidget(self.create_action_QTextEdit(self.character.Legendary_Actions))
        
        #if there are Special Abilities, show them
        if self.character.Special_Abilities:
            layout.addWidget(self.create_Heading_QLabel("SPECIAL ABILITIES"))
            layout.addWidget(self.create_QTextEdit(self.character.Special_Abilities))
            
        return page

    # ---------------------- PAGE 3: SPELLS ---------------------- #
    def create_sepll_QTextEdit(self, ls):
        html_string = ""
        for a in ls:
            spell_level = f"<b>Level: {a.spell_level}:</b>" if a.spell_level else ""
            spell_name = f"<b>{a.spell_name}</b>" if a.spell_name else ""
            spell_description = a.spell_description or ""
            html_string += f"{spell_level}<br>{spell_name}<br>{spell_description}<br><br>"
        
        return self.create_QTextEdit(html_string)
    
    def build_spells_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self.create_Heading_QLabel("SPELL SLOTS"))
        spellSlotSrting = ""
        for i in range(9):
            spellSlotSrting += f"Level {i+1}: {self.character.Spell_Slots[i]}"
            if (i < 8):
                spellSlotSrting += " | "
            if (i == 4):
                spellSlotSrting += "\n"
        
        layout.addWidget(QLabel(spellSlotSrting))
            
        layout.addWidget(self.create_Heading_QLabel("SPELLS"))
        layout.addWidget(self.create_sepll_QTextEdit(self.character.Spells)) #add and displays the spells and there levels
        return page

    # ---------------------- PAGE 4: EQUIPMENT ---------------------- #
    def build_equipment_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self.create_Heading_QLabel("BACKSTORY"))
        layout.addWidget(self.create_QTextEdit(self.character.Background))
        layout.addWidget(self.create_Heading_QLabel("EQUIPMENT"))
        layout.addWidget(self.create_QTextEdit(self.character.Equipment, 150))
        return page

    # ---------------------- PAGE 5: General info ---------------------- #     
    def build_other_info_tab(self):
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(4)

        h1 = QGridLayout()
        h1.addWidget(self.labeled_field("Class", self.character.Class, True),0, 0)
        h1.addWidget(self.labeled_field("Sub Class", self.character.Subclass, True),0, 1)
        h1.addWidget(self.labeled_field("Level", self.character.Level, True), 0, 2)
        h1.addWidget(self.labeled_field("Species", self.character.Species, True), 1, 0)
        h1.addWidget(self.labeled_field("Size", self.character.Size, True), 1, 1)
        h1.addWidget(self.labeled_field("Passive Perception", self.character.Passive_Perception, True), 1, 2)
        layout.addLayout(h1)
        
        h3 = QVBoxLayout()
        h3.addWidget(self.labeled_field("Languages", self.character.Languages, True))
        h3.addWidget(self.labeled_field("Spell Save DC", self.character.Spell_Save_DC, True))
        h3.addWidget(self.labeled_field("Spell Att. Mod.", self.character.Spell_Attack_Modifier, True))
        layout.addLayout(h3)
        
        # h3.addWidget(self.labeled_field("Senses", self.character.Senses, True))
        # h3.addWidget(self.labeled_field("CR", self.character.Challenge_Rating, True))
        
        # h4 = QHBoxLayout()        
        # 
        # h4.addWidget(self.labeled_field("Spell Att. Mod.", self.character.Spell_Attack_Modifier, True))
        # layout.addWidget(h4)
   
        layout.addStretch()
        return page
    
    # ---------------------- HELPER UI ELEMENTS ---------------------- #
    def labeled_field(self, label, value, centered=False, additional_string=""):
        
        #if value is not a string, convert it to one
        if not isinstance(value, str):
            value = str(value)
        
        box = QWidget()
        vbox = QVBoxLayout(box)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-weight: bold; color: #a02b2b;")
        field = QLineEdit(value+additional_string)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if centered else Qt.AlignmentFlag.AlignLeft)
        field.setAlignment(Qt.AlignmentFlag.AlignCenter if centered else Qt.AlignmentFlag.AlignLeft)
        field.setReadOnly(True)
        vbox.addWidget(lbl)
        vbox.addWidget(field)
        return box

    def ability_box(self, name, score):
        box = QGroupBox(name)
        vbox = QVBoxLayout(box)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align all widgets to the top

        score_label = QLabel(str(score))
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2a1a0b;")
        vbox.addWidget(score_label)
        
        mod = (score - 10) // 2
        mod_label = QLabel(f"Modifier: {mod:+}")
        mod_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mod_label.setStyleSheet("font-size: 9pt; font-weight: bold; color: #633;")
        vbox.addWidget(mod_label)
        
        saving_throw_lable = QLabel(f"Saving Throw: {mod:+}")
        saving_throw_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        saving_throw_lable.setStyleSheet("font-size: 9pt; font-weight: bold; color: #444;")
        vbox.addWidget(saving_throw_lable)
        
        def check_skill(skill):
            if skill == 0:
                skill = mod
            return skill

        # Add skills for the different abilities
        # Add Dexterity skills if applicable
        if name == "Strength":
            skills = [
                ("Athletics", check_skill(self.character.Athletics)),
            ]
        elif name == "Dexterity":
            skills = [
                ("Acrobatics", check_skill(self.character.Acrobatics)),
                ("Sleight of Hand", check_skill(self.character.Sleight_of_Hand)),
                ("Stealth", check_skill(self.character.Stealth)),
            ]
        elif name == "Constitution":
            skills = [
                # No skills tied to Constitution
            ]
        elif name == "Intelligence":
            skills = [
                ("Arcana", check_skill(self.character.Arcana)),
                ("History", check_skill(self.character.History)),
                ("Investigation", check_skill(self.character.Investigation)),
                ("Nature", check_skill(self.character.Nature)),
                ("Religion", check_skill(self.character.Religion)),
            ]
        elif name == "Wisdom":
            skills = [
                ("Animal Handling", check_skill(self.character.Animal_Handling)),
                ("Insight", check_skill(self.character.Insight)),
                ("Medicine", check_skill(self.character.Medicine)),
                ("Perception", check_skill(self.character.Perception)),
                ("Survival", check_skill(self.character.Survival)),
            ]
        elif name == "Charisma":
            skills = [
                ("Deception", check_skill(self.character.Deception)),
                ("Intimidation", check_skill(self.character.Intimidation)),
                ("Performance", check_skill(self.character.Performance)),
                ("Persuasion", check_skill(self.character.Persuasion)),
            ]
        else:
            skills = [] #make a blank skills list if no ability match found
        
        for skill_name, skill_val in skills:
            skill_label = QLabel(f"{skill_name}: {skill_val}")
            skill_label.setStyleSheet("font-size: 9pt; color: #444;")
            skill_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            vbox.addWidget(skill_label)
                
        return box
    
    def create_Heading_QLabel(self, text):
        actions_label = QLabel(text)
        actions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions_label.setStyleSheet("""
            QLabel {
                font-size: 13pt;
                font-weight: bold;
                color: #3b1f0b;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8e7c2, stop:1 #e0c6a1
                );
                border: 2px solid #a47b5a;
                border-radius: 4px;
                padding: 4px;
                margin-top: 10px;
            }
        """)
        return actions_label

    def create_QTextEdit(self, string="", height=0):
        box = QTextEdit()
        box.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 250, 240, 200);
                border: 1px solid #b09060;
                font-family: 'Bookman Old Style';
                font-size: 10pt;
                color: #2a1a0b;
                line-height: 1.4em;
            }
        """)
        box.setReadOnly(False)
        box.setHtml(string)
        
        #if the height is set to greater than 0, set the fixed height
        if height > 0:
            box.setFixedHeight(height)
        
        box.setReadOnly(True)   #make the box non-editable
        
        return box
    
    def update_sheet(self, character: CharacterRow):
        """
        @breif Update the character data in the sheet.
        @param character: CharacterRow object containing the character data.
        """
        self.character = character
        self.setWindowTitle(character.Character_Name or "D&D Character Sheet")

        # remember currently selected tab (if tabs exist)
        current_index = 0
        old_cw = self.centralWidget()
        if isinstance(old_cw, QTabWidget):
            try:
                current_index = old_cw.currentIndex()
            except Exception:
                current_index = 0
        
        # === Main Tabs ===
        tabs = QTabWidget()
        tabs.addTab(self.scrollable(self.build_core_stats_tab()), "Core Stats")
        tabs.addTab(self.scrollable(self.build_features_tab()), "Actions/Feats")
        tabs.addTab(self.scrollable(self.build_spells_tab()), "Spells")
        tabs.addTab(self.scrollable(self.build_equipment_tab()), "Backstory/Equipment")
        tabs.addTab(self.scrollable(self.build_other_info_tab()), "Other Info")
        
        # restore previously selected tab (clamp to valid range)
        if tabs.count() > 0:
            tabs.setCurrentIndex(min(max(0, current_index), tabs.count() - 1))

        # replace central widget and clean up old tabs widget
        self.setCentralWidget(tabs)
        if isinstance(old_cw, QTabWidget):
            old_cw.deleteLater()
        
        self.setCentralWidget(tabs)