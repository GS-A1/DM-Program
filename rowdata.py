from dataclasses import dataclass, field

@dataclass
class CharacterRow:
    """
    @class CharacterRow
    @brief Data class representing a single character row in the table.
    
    This class holds all the data fields for a character, including a unique Character_ID,
    stats, abilities, and other relevant information for each row in the DM program.
    """
    
    class SpellsDes:
        spell_level = 0
        spell_name = ""
        spell_description = ""
        times_per_day = 0      #some monsters can cast spells a certain number of times per day (unlike a player). Replaces spell slots
        
        def __repr__(self):
            return f"SpellsDes(level={self.spell_level}, name='{self.spell_name}', description='{self.spell_description}')"
    
    class GeneralDes:
        name = ""
        description = ""
        
        def __repr__(self):
            return f"GeneralDes(name='{self.name}', description='{self.description}')"

    Character_ID: int = field(default_factory=lambda: CharacterRow._get_next_id())
    """@brief Unique identifier for each character row."""

    _id_counter: int = 0
    """@brief Class variable to keep track of the last used Character_ID."""

    # Character variables with default values
    X: str = ""
    character_url: str = ""       #if the character/monster if taken from a website, store the link here
    Player_Name: str = "NPC"
    Character_Name: str = ""
    Background: str = ""
    Class: str = ""
    Species: str = ""
    Subclass: str = ""
    Level: int = 0
    Armor_Class: int = 0
    Temporary_AC: int = 0
    Hit_Dice: str = ""
    Death_Saves: int = 0
    Proficiency_Bonus: int = 0
    Initiative_Bonus: int = 0
    Initiative: int = 0
    Walk_Speed: int = 0
    Fly_Speed: int = 0
    Swim_Speed: int = 0
    Climb_Speed: int = 0
    Burrow_Speed: int = 0
    Size: str = ""
    Passive_Perception: int = 0
    Max_HP: int = 0
    Temporary_Hit_Points: int = 0
    Current_HP: int = 0
    Damage: int = 0
    Conditions_Spell_Effects: str = ""
    Select: str = ""
    Intelligence: int = 0
    Arcana: int = 0
    History: int = 0
    Investigation: int = 0
    Nature: int = 0
    Religion: int = 0
    Strength: int = 0
    Athletics: int = 0
    Dexterity: int = 0
    Acrobatics: int = 0
    Sleight_of_Hand: int = 0
    Stealth: int = 0
    Wisdom: int = 0
    Animal_Handling: int = 0
    Insight: int = 0
    Medicine: int = 0
    Perception: int = 0
    Survival: int = 0
    Constitution: int = 0
    Charisma: int = 0
    Deception: int = 0
    Intimidation: int = 0
    Performance: int = 0
    Persuasion: int = 0
    Saving_Throws: str = ""
    Damage_Resistance: str = ""
    Damage_Immunities: str = ""
    Condition_Immunities: str = ""
    Languages: str = ""
    Senses: str = ""
    Challenge_Rating: str = ""
    Equipment: str = ""
    Special_Abilities: str = ""
    Spell_Save_DC: int = 0
    Spell_Attack_Modifier: int = 0
    Spells: list[SpellsDes] = field(default_factory=list)
    Spell_Slots: list[int] = field(default_factory=lambda: [0]*9)
    Feats: list[GeneralDes] = field(default_factory=list)
    Actions: list[GeneralDes] = field(default_factory=list)
    Bonus_Actions: list[GeneralDes] = field(default_factory=list)
    Reactions: list[GeneralDes] = field(default_factory=list)
    Legendary_Actions: list[GeneralDes] = field(default_factory=list)
    is_button: str = ""
    """@brief Set if the row is a button to the name of the button."""

    def _set_generic(self):
        """
        @brief sets generic values for the character
        This method can be called to set the values to a generic character.
        """
        self.Player_Name = "NPC"
        self.Character_Name = "Character " + str(self.Character_ID-3)
        self.Level = 1
        self.Armor_Class = 10
        self.Temporary_AC = 0
        self.Hit_Dice = "1d6"
        self.Walk_Speed = 30
        self.Size = "Medium"
        self.Max_HP = 10
        self.Current_HP = 10
        self.Intelligence = 10
        self.Strength = 10
        self.Dexterity = 10
        self.Wisdom = 10
        self.Constitution = 10
        self.Charisma = 10
    
    @classmethod
    def _get_next_id(cls):
        """
        @brief Generate the next unique Character_ID for a new CharacterRow.
        @return The next available integer Character_ID.
        """
        result = cls._id_counter
        cls._id_counter += 1
        return result

# Names of the columns in the table
ColumnNames = [
    "X",
    "Character ID",
    "Player Name",
    "Character Name",
    "Background",
    "Class",
    "Species",
    "Subclass",
    "Level",
    "AC",
    "Temp. AC",
    "Hit Dice",
    "Death Saves",
    "Proficiency Bonus",
    "Initiative Bonus",
    "Initiative",
    "Speed",
    "Size",
    "Passive Perception",
    "Max HP",
    "Temp. HP",
    "Current HP",
    "Damage",
    "Conditions/Spell Effects",
    "Select",  # Placeholder for the conditions combo box column
    "Intelligence",
    "Arcana",
    "History",
    "Investigation",
    "Nature",
    "Religion",
    "Strength",
    "Athletics",
    "Dexterity",
    "Acrobatics",
    "Sleight of Hand",
    "Stealth",
    "Wisdom",
    "Animal Handling",
    "Insight",
    "Medicine",
    "Perception",
    "Survival",
    "Constitution",
    "Charisma",
    "Deception",
    "Intimidation",
    "Performance",
    "Persuasion",
    "Saving Throws",
    "Damage Resistance",
    "Languages",
    "Challenge Rating",
    "Equipment",
    "Special Abilities",
    "Spells",
    "Spell Slots",
    "Feats",
    "Actions",
    "Bonus Actions",
    "Reactions",
    "Legendary Actions",
]