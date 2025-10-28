from PyQt6.QtWidgets import QMessageBox
import os
import xml.etree.ElementTree as ET  # Import the XML parsing module
from xml.etree.ElementTree import ElementTree, indent
from rowdata import CharacterRow  # Assuming CharacterRow is defined in rowdata.py




"""
@brief update the character names list with characters from the xml file
@param file_path string containing the full path to the xml file
@param parent string containing the parent element to search within the xml file. if blank, use the root
@retval list of character names
"""
def load_character_names_xml(file_path, parent="",):
    """Load characters from the selected XML file into the character list."""
    names = []
    file_name = os.path.basename(file_path)
    if file_name == "Select a file":
        return
    #file_path = os.path.join("./Settings/Characters", file_name)
    try:
        tree = ET.parse(file_path)
        #if there is no parent use the root as the parent:
        if parent == "":
            root = tree.getroot()
        else:
            #find the parent element
            root = tree.getroot().find(parent)
            if root is None:
                #if we didnt find the parent, return a blank character as nothing exists 
                return names  #return a blank list as we didnt find the parent
        
        #loop through all of the characters to get their names
        for character in root.findall("character"):
            name = character.find("character_name").text
            names.append(name)  #add the name to the list
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load characters: {e}")
    # Return a list of character names
    return names

"""
@brief find a chracter within an xml file extract all data from it
@param file_path string containing the full path to the xml file
@param character_name string containg the name of the character in the file we are interested in
@param parent string containing the parent element to search within the xml file. if blank, use the root
@param load_character_ID boolean to indicate if the character ID and player name should be loaded from the file. If false, a new ID will be assigned
@retval character_row CharacterRow object with fully populated data from the xml file. if the current_hp
        feild is set to -9999999999, there was an error reading in the character
"""
def load_character_information_xml(file_path, character_name, parent="", load_character_ID=False):
    character_row = CharacterRow()  # Create an instance to use the method
    file_name = os.path.basename(file_path)
    #if the file name is the default, return a blank character
    if file_name == "Select a file":
        return character_row  #return early as we didnt find a file
    
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(file_path)
        #if there is no parent use the root as the parent:
        if parent == "":
            root = tree.getroot()
        else:
            #find the parent element
            root = tree.getroot().find(parent)
            if root is None:
                #if we didnt find the parent, return a blank character as nothing exists 
                return character_row  #return early as we didnt find the parent
            
        #loop through all of the characters to find the one we want
        for character in root.findall("character"):
            name = character.find("character_name").text
            if name == character_name:
                character_row.character_url = find_in_feild_string(character, "character_url")
                character_row.Character_Name = find_in_feild_string(character, "character_name")
                character_row.Background = find_in_feild_string(character, "background")
                character_row.Class = find_in_feild_string(character, "class_")
                character_row.Species = find_in_feild_string(character, "Species")
                character_row.Subclass = find_in_feild_string(character, "Subclass")
                character_row.Level = find_in_feild_int(character, "level")
                character_row.Armor_Class = find_in_feild_int(character, "armor_class")
                character_row.Hit_Dice = find_in_feild_string(character, "hit_dice")
                character_row.Death_Saves = find_in_feild_int(character, "death_Saves")
                character_row.Proficiency_Bonus = find_in_feild_int(character, "proficiency_bonus")
                character_row.Initiative_Bonus = find_in_feild_int(character, "initiative_bonus")
                character_row.Initiative = find_in_feild_int(character, "initiative")
                character_row.Size = find_in_feild_string(character, "size")
                character_row.Passive_Perception = find_in_feild_int(character, "passive_perception")
                character_row.Max_HP = find_in_feild_int(character, "max_hp")
                character_row.Temporary_Hit_Points = find_in_feild_int(character, "temporary_hit_points")
                character_row.Current_HP = find_in_feild_int(character, "current_hp")
                character_row.Damage = find_in_feild_int(character, "damage")
                character_row.Conditions_Spell_Effects = find_in_feild_string(character, "conditions_spell_effects")
                character_row.Intelligence = find_in_feild_int(character, "intelligence")
                character_row.Arcana = find_in_feild_int(character, "arcana")
                character_row.History = find_in_feild_int(character, "history")
                character_row.Investigation = find_in_feild_int(character, "investigation")
                character_row.Nature = find_in_feild_int(character, "nature")
                character_row.Religion = find_in_feild_int(character, "religion")
                character_row.Strength = find_in_feild_int(character, "strength")
                character_row.Athletics = find_in_feild_int(character, "athletics")
                character_row.Dexterity = find_in_feild_int(character, "dexterity")
                character_row.Acrobatics = find_in_feild_int(character, "acrobatics")
                character_row.Sleight_of_Hand = find_in_feild_int(character, "sleight_of_hand")
                character_row.Stealth = find_in_feild_int(character, "stealth")
                character_row.Wisdom = find_in_feild_int(character, "wisdom")
                character_row.Animal_Handling = find_in_feild_int(character, "animal_handling")
                character_row.Insight = find_in_feild_int(character, "insight")
                character_row.Medicine = find_in_feild_int(character, "medicine")
                character_row.Perception = find_in_feild_int(character, "perception")
                character_row.Survival = find_in_feild_int(character, "survival")
                character_row.Constitution = find_in_feild_int(character, "constitution")
                character_row.Charisma = find_in_feild_int(character, "charisma")
                character_row.Deception = find_in_feild_int(character, "deception")
                character_row.Intimidation = find_in_feild_int(character, "intimidation")
                character_row.Performance = find_in_feild_int(character, "performance")
                character_row.Persuasion = find_in_feild_int(character, "persuasion")
                character_row.Saving_Throws = find_in_feild_string(character, "saving_throws")
                character_row.Damage_Resistance = find_in_feild_string(character, "damage_resistance")
                character_row.Damage_Immunities = find_in_feild_string(character, "damage_immunities")
                character_row.Condition_Immunities = find_in_feild_string(character, "condition_immunities")
                character_row.Languages = find_in_feild_string(character, "languages")
                character_row.Challenge_Rating = find_in_feild_string(character, "challenge_rating")
                character_row.Equipment = find_in_feild_string(character, "equipment")
                character_row.Special_Abilities = find_in_feild_string(character, "special_abilities")
                character_row.Senses = find_in_feild_string(character, "senses")
                character_row.Spell_Save_DC = find_in_feild_int(character, "spell_save_dc")
                character_row.Spell_Attack_Modifier = find_in_feild_int(character, "spell_attack_modifier")
                #deal with the extra feilds - speed, feats, actions, spells etc
                #speed
                element = character.find("speed")   #find the element in the xml file containing the speed data
                character_row.Walk_Speed = find_in_feild_int(element, "walk")
                character_row.Fly_Speed = find_in_feild_int(element, "fly")
                character_row.Swim_Speed = find_in_feild_int(element, "swim")
                character_row.Climb_Speed = find_in_feild_int(element, "climb")
                character_row.Burrow_Speed = find_in_feild_int(element, "burrow")
                
                #spell slots
                try:
                    element = character.find("spell_slots")   #find the element in the xml file containing the spell slot data
                    character_row.Spell_Slots[0] = find_in_feild_int(element, "level_1")
                    character_row.Spell_Slots[1] = find_in_feild_int(element, "level_2")
                    character_row.Spell_Slots[2] = find_in_feild_int(element, "level_3")
                    character_row.Spell_Slots[3] = find_in_feild_int(element, "level_4")
                    character_row.Spell_Slots[4] = find_in_feild_int(element, "level_5")
                    character_row.Spell_Slots[5] = find_in_feild_int(element, "level_6")
                    character_row.Spell_Slots[6] = find_in_feild_int(element, "level_7")
                    character_row.Spell_Slots[7] = find_in_feild_int(element, "level_8")
                    character_row.Spell_Slots[8] = find_in_feild_int(element, "level_9")
                except:
                    #if there was an error, just set all of the spell slots to 0
                    character_row.Spell_Slots = [0]*9
                
                #feats
                character_row.Feats = find_in_feild_GeneralDes(character, "feats")
                
                #actions
                character_row.Actions = find_in_feild_GeneralDes(character, "actions")
                
                #bonus actions
                character_row.Bonus_Actions = find_in_feild_GeneralDes(character, "bonus_actions")
                
                #reactions
                character_row.Reactions = find_in_feild_GeneralDes(character, "reactions")
                
                #legendary_actions
                character_row.Legendary_Actions = find_in_feild_GeneralDes(character, "legendary_actions")
                
                #spells
                character_row.Spells = find_in_feild_SpellsDes(character, "spells")
                
                #load the character ID if recquired
                #also load player name if recquired
                if load_character_ID:
                    character_row.Character_ID = find_in_feild_int(character, "character_ID")
                    #if we are larger than the current ID counter, update the counter to avoid having to characters with the same ID
                    if character_row._id_counter <= character_row.Character_ID:
                        character_row._id_counter = character_row.Character_ID + 1
                    character_row.Player_Name = find_in_feild_string(character, "player_name")
                
                #if we didnt see a current HP, set it to max HP
                if (character_row.Current_HP == -9999999999):
                    character_row.Current_HP = character_row.Max_HP
                
                return character_row #return early as we have found the character we want
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to retrieve character data: {e}")
    #if we got this far, there was an error
    character_row.Current_HP = -9999999999  # Set to a value that indicates an error
    return character_row

"""
@breif Write character information to an xml file
@param file_path string containing the full path to the xml file
@param character CharacterRow object containing the character data to write
@param parent string containing the parent element to search within the xml file. if blank, use the root
@param save_character_ID boolean to indicate if the character ID and player name should be saved to the file.
"""
def write_character_information_to_xml(file_path, character=CharacterRow(), parent="", save_character_ID=False):
    """
    @brief Write or update a character in the XML file. If a character with the same name exists, it is deleted first.
    Then, the character is added with at least the armor class field.
    @param file_path Path to the XML file.
    @param character CharacterRow object to write.
    """    
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        #if there is no parent use the root as the parent:
        if parent == "":
            root = tree.getroot()
        else:
            #find the parent element
            root = tree.getroot().find(parent)
            if root is None:
                #if we didnt find the parent, create it
                root = ET.SubElement(tree.getroot(), parent)
        
        # Remove any existing character with the same name
        for char_elem in root.findall("character"):
            name = char_elem.find("character_name")
            if name is not None and name.text == character.Character_Name:
                root.remove(char_elem)
                break  # Remove only the first match (assuming unique names)

        # Create new character element
        new_char_elem = ET.Element("character")
        ET.SubElement(new_char_elem, "character_url").text = character.character_url
        ET.SubElement(new_char_elem, "character_name").text = character.Character_Name
        ET.SubElement(new_char_elem, "background").text = character.Background
        ET.SubElement(new_char_elem, "class_").text = character.Class
        ET.SubElement(new_char_elem, "Species").text = character.Species
        ET.SubElement(new_char_elem, "Subclass").text = character.Subclass
        ET.SubElement(new_char_elem, "level").text = str(character.Level)
        ET.SubElement(new_char_elem, "armor_class").text = str(character.Armor_Class)
        ET.SubElement(new_char_elem, "hit_dice").text = character.Hit_Dice
        ET.SubElement(new_char_elem, "death_Saves").text = str(character.Death_Saves)
        ET.SubElement(new_char_elem, "proficiency_bonus").text = str(character.Proficiency_Bonus)
        ET.SubElement(new_char_elem, "initiative_bonus").text = str(character.Initiative_Bonus)
        ET.SubElement(new_char_elem, "initiative").text = str(character.Initiative)
        ET.SubElement(new_char_elem, "size").text = character.Size
        ET.SubElement(new_char_elem, "passive_perception").text = str(character.Passive_Perception)
        ET.SubElement(new_char_elem, "max_hp").text = str(character.Max_HP) 
        ET.SubElement(new_char_elem, "temporary_hit_points").text = str(character.Temporary_Hit_Points)
        ET.SubElement(new_char_elem, "current_hp").text = str(character.Current_HP)
        ET.SubElement(new_char_elem, "damage").text = str(character.Damage)
        ET.SubElement(new_char_elem, "conditions_spell_effects").text = character.Conditions_Spell_Effects
        ET.SubElement(new_char_elem, "intelligence").text = str(character.Intelligence)
        ET.SubElement(new_char_elem, "arcana").text = str(character.Arcana)
        ET.SubElement(new_char_elem, "history").text = str(character.History)
        ET.SubElement(new_char_elem, "investigation").text = str(character.Investigation)
        ET.SubElement(new_char_elem, "nature").text = str(character.Nature)
        ET.SubElement(new_char_elem, "religion").text = str(character.Religion)
        ET.SubElement(new_char_elem, "strength").text = str(character.Strength)
        ET.SubElement(new_char_elem, "athletics").text = str(character.Athletics)
        ET.SubElement(new_char_elem, "dexterity").text = str(character.Dexterity)
        ET.SubElement(new_char_elem, "acrobatics").text = str(character.Acrobatics)
        ET.SubElement(new_char_elem, "sleight_of_hand").text = str(character.Sleight_of_Hand)
        ET.SubElement(new_char_elem, "stealth").text = str(character.Stealth)
        ET.SubElement(new_char_elem, "wisdom").text = str(character.Wisdom)
        ET.SubElement(new_char_elem, "animal_handling").text = str(character.Animal_Handling)
        ET.SubElement(new_char_elem, "insight").text = str(character.Insight)
        ET.SubElement(new_char_elem, "medicine").text = str(character.Medicine)
        ET.SubElement(new_char_elem, "perception").text = str(character.Perception)
        ET.SubElement(new_char_elem, "survival").text = str(character.Survival)
        ET.SubElement(new_char_elem, "constitution").text = str(character.Constitution)
        ET.SubElement(new_char_elem, "charisma").text = str(character.Charisma)
        ET.SubElement(new_char_elem, "deception").text = str(character.Deception)
        ET.SubElement(new_char_elem, "intimidation").text = str(character.Intimidation)
        ET.SubElement(new_char_elem, "performance").text = str(character.Performance)
        ET.SubElement(new_char_elem, "persuasion").text = str(character.Persuasion)
        ET.SubElement(new_char_elem, "saving_throws").text = character.Saving_Throws
        ET.SubElement(new_char_elem, "damage_resistance").text = character.Damage_Resistance
        ET.SubElement(new_char_elem, "damage_immunities").text = character.Damage_Immunities
        ET.SubElement(new_char_elem, "condition_immunities").text = character.Condition_Immunities
        ET.SubElement(new_char_elem, "languages").text = character.Languages
        ET.SubElement(new_char_elem, "challenge_rating").text = character.Challenge_Rating
        ET.SubElement(new_char_elem, "equipment").text = character.Equipment
        ET.SubElement(new_char_elem, "special_abilities").text = character.Special_Abilities
        ET.SubElement(new_char_elem, "senses").text = character.Senses
        ET.SubElement(new_char_elem, "spell_save_dc").text = str(character.Spell_Save_DC)
        ET.SubElement(new_char_elem, "spell_attack_modifier").text = str(character.Spell_Attack_Modifier)
        # Create the speed parent element
        speed_elem = ET.SubElement(new_char_elem, "speed")
        # Add sub-tags under speed
        ET.SubElement(speed_elem, "walk").text = str(character.Walk_Speed)
        ET.SubElement(speed_elem, "fly").text = str(character.Fly_Speed)
        ET.SubElement(speed_elem, "swim").text = str(character.Swim_Speed)
        ET.SubElement(speed_elem, "climb").text = str(character.Climb_Speed)
        ET.SubElement(speed_elem, "burrow").text = str(character.Burrow_Speed)
        
        # Create the spell_slots parent element
        spell_slots_elem = ET.SubElement(new_char_elem, "spell_slots")
        # Add sub-tags under spell_slots
        ET.SubElement(spell_slots_elem, "level_1").text = str(character.Spell_Slots[0])
        ET.SubElement(spell_slots_elem, "level_2").text = str(character.Spell_Slots[1])
        ET.SubElement(spell_slots_elem, "level_3").text = str(character.Spell_Slots[2])
        ET.SubElement(spell_slots_elem, "level_4").text = str(character.Spell_Slots[3])
        ET.SubElement(spell_slots_elem, "level_5").text = str(character.Spell_Slots[4])
        ET.SubElement(spell_slots_elem, "level_6").text = str(character.Spell_Slots[5])
        ET.SubElement(spell_slots_elem, "level_7").text = str(character.Spell_Slots[6])
        ET.SubElement(spell_slots_elem, "level_8").text = str(character.Spell_Slots[7])
        ET.SubElement(spell_slots_elem, "level_9").text = str(character.Spell_Slots[8])
        
        # Add feats
        feats_elem = ET.SubElement(new_char_elem, "feats")
        for feat in character.Feats:
            feat_elem = ET.SubElement(feats_elem, "feat")
            ET.SubElement(feat_elem, "name").text = feat.name
            ET.SubElement(feat_elem, "description").text = feat.description
        
        # Add actions
        actions_elem = ET.SubElement(new_char_elem, "actions")
        for action in character.Actions:
            action_elem = ET.SubElement(actions_elem, "action")
            ET.SubElement(action_elem, "name").text = action.name
            ET.SubElement(action_elem, "description").text = action.description
        
        # Add bonus actions
        bonus_actions_elem = ET.SubElement(new_char_elem, "bonus_actions")
        for bonus_action in character.Bonus_Actions:
            bonus_action_elem = ET.SubElement(bonus_actions_elem, "bonus_action")
            ET.SubElement(bonus_action_elem, "name").text = bonus_action.name
            ET.SubElement(bonus_action_elem, "description").text = bonus_action.description
            
        # Add reactions
        reactions_elem = ET.SubElement(new_char_elem, "reactions")
        for reaction in character.Reactions:
            reaction_elem = ET.SubElement(reactions_elem, "reaction")
            ET.SubElement(reaction_elem, "name").text = reaction.name
            ET.SubElement(reaction_elem, "description").text = reaction.description
        
        # Add legendary actions
        legendary_actions_elem = ET.SubElement(new_char_elem, "legendary_actions")
        for legendary_action in character.Legendary_Actions:
            legendary_action_elem = ET.SubElement(legendary_actions_elem, "legendary_action")
            ET.SubElement(legendary_action_elem, "name").text = legendary_action.name
            ET.SubElement(legendary_action_elem, "description").text = legendary_action.description
        
        # Add spells
        spells_elem = ET.SubElement(new_char_elem, "spells")
        for spell in character.Spells:
            spell_elem = ET.SubElement(spells_elem, "spell")
            ET.SubElement(spell_elem, "level").text = str(spell.spell_level)
            ET.SubElement(spell_elem, "name").text = spell.spell_name
            ET.SubElement(spell_elem, "description").text = spell.spell_description
            ET.SubElement(spell_elem, "times_per_day").text = str(spell.times_per_day)
        
        #if the character IF needs to be saved (eg saving row and data information)
        #also save the player name here, as it is most lickly a call from the main app
        if save_character_ID:
            ET.SubElement(new_char_elem, "character_ID").text = str(character.Character_ID)
            ET.SubElement(new_char_elem, "player_name").text = str(character.Player_Name)

        # Add the new character to the root
        root.append(new_char_elem)

        # Indent and write back to file
        indent(root)
        tree.write(file_path, encoding="unicode", xml_declaration=True)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to write character: {e}")
        
"""
@brief find a int using a feild for a single character within the xml file
@param xml_element Element object containing feilds we want to search
@param feild the feild (including the s) you are looking for in the xml file
@retval value a int containing the data in the associated feild
"""
def find_in_feild_int(xml_element, feild):
    elem = xml_element.find(feild)
    if elem is not None and elem.text is not None:
        try:
            #if the first value does not equal a '+' (some may have + for say survival (+2))
            if elem.text[0] == '+':
                value = int(elem.text[1:]) #ignore the first character
            else:
                value = int(elem.text)
        except ValueError:
            value = 0  # not a valid integer
    else:
        #tag does not exist, or does not contain a value
        # a specical case for current hp as somtimes it may not exist in a new character
        if (feild == "current_hp"):
            value = -9999999999   #return an error we can detect
        else:
            value = 0
    return value

"""
@brief find a string using a feild for a single character within the xml file
@param xml_element Element object containing feilds we want to search
@param feild the feild (including the s) you are looking for in the xml file
@retval value a string containing the data in the associated feild
"""
def find_in_feild_string(xml_element, feild):
    elem = xml_element.find(feild)
    if elem is not None and elem.text is not None:
        try:
            value = elem.text
        except ValueError:
            value = ""  # or any default value you prefer
    else:
        value = ""  # or any default value you prefer
    return value

"""
@brief find a list of CharacterRow.GeneralDes objects in a xml file
@param xml_element Element object containing feilds we want to search
@param feild the feild (including the s) you are looking for in the xml file
@retval elel_list a list containing all of the CharacterRow.GeneralDes found in the feild
"""
def find_in_feild_GeneralDes(xml_element, feild = ""):
    element = xml_element.find(feild)
    elel_list = []
    if element is not None:
        for elem in element.findall(feild[0:(len(feild)-1)]):
            temp_list = CharacterRow.GeneralDes()
            temp_list.name = elem.findtext("name", "")
            temp_list.description = elem.findtext("description", "")
            elel_list.append(temp_list)
    return elel_list

"""
@brief find a list of CharacterRow.SpellsDes objects in a xml file
@param xml_element Element object containing feilds we want to search
@param feild the feild (including the s) you are looking for in the xml file
@retval elel_list a list containing all of the CharacterRow.SpellsDes found in the feild
"""
def find_in_feild_SpellsDes(xml_element, feild = ""):
    element = xml_element.find(feild)
    elel_list = []
    if element is not None:
        for elem in element.findall(feild[0:(len(feild)-1)]):
            temp_list = CharacterRow.SpellsDes()
            temp_list.spell_level = elem.findtext("level", 0)
            temp_list.spell_name = elem.findtext("name", "")
            temp_list.spell_description = elem.findtext("description", "")
            temp_list.times_per_day = elem.findtext("times_per_day", 0)
            elel_list.append(temp_list)
    return elel_list