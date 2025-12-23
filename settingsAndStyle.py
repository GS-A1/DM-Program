class StyleInfo:
    """
    @class StyleInfo
    @brief Data class used to hold styling information for UI elements.
    """
    #Font information
    font_general_size = 0
    font_general_style = ""
    font_button_size = 0
    font_button_style = ""
    font_table_size = 0
    font_table_style = ""
    
    colour_general = ""
    colour_minor = ""
    colour_button = ""
    
    colour_general_text = ""
    colour_table_text = ""
    colour_button_text = ""
    
    colour_current_turn = ""
    colour_full_hp = ""
    colour_critical_hp = ""
    colour_no_hp = ""
    
    def __init__(self, parent=None):
        """
        @brief Constructor for StyleInfo class.
        Initializes style information to default values.
        """
        self.resetLayout()
    
    def resetLayout(self):
        """
        @brief Resets all style information to default values.
        """
        self.font_general_size = 9
        self.font_general_style = "Bookman Old Style"
        self.font_button_size = 9
        self.font_button_style = "Bookman Old Style"
        self.font_table_size = 9
        self.font_table_style = "Bookman Old Style"
        self.colour_general_text = "#ff2a1a0b"
        self.colour_table_text = "#ff2a1a0b"
        self.colour_button_text = "#ffffffff"
        self.colour_button = "#ffa02b2b"
        self.colour_general = "#fffaf2dc"
        self.colour_minor = "#fffdfbf4"
        
        self.colour_current_turn = "#ffffff00"
        self.colour_full_hp = "#ff00ff00"
        self.colour_critical_hp = "#ffffaa00"
        self.colour_no_hp = "#ffff0000"
    
    def findHover(self, hex_color, amount=28):
        """
        @breif Adjusts the given hex color to create a hover effect.
        Lightens or darkens the color based on its perceived brightness.
        @param hex_color: The original color in hex format (#RRGGBB or #AARRGGBB).
        @param amount: The base amount to adjust the color by.
        """
        hex_color = hex_color.lstrip('#')

        # Detect alpha
        if len(hex_color) == 8:
            a = int(hex_color[0:2], 16)
            r, g, b = [int(hex_color[i:i+2], 16) for i in (2, 4, 6)]
        elif len(hex_color) == 6:
            a = 255
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        else:
            raise ValueError("Invalid hex color format. Use #RRGGBB or #AARRGGBB.")

        # Compute perceived brightness
        brightness = 0.2126*r + 0.7152*g + 0.0722*b  # sRGB luminance

        # Adjust the light/dark change magnitude based on brightness
        if brightness < 64:       # very dark
            delta = amount + 12
            direction = 1         # lighten
        elif brightness < 128:    # mid-dark
            delta = amount + 6
            direction = 1         # lighten
        elif brightness < 192:    # mid-light
            delta = amount - 4
            direction = -1        # darken slightly
        else:                     # very bright
            delta = amount - 10
            direction = -1        # darken more

        change = delta * direction

        # Apply and clamp
        r = min(max(int(r + change), 0), 255)
        g = min(max(int(g + change), 0), 255)
        b = min(max(int(b + change), 0), 255)

        # Return with or without alpha
        if len(hex_color) == 8:
            return f"#{a:02x}{r:02x}{g:02x}{b:02x}"
        else:
            return f"#{r:02x}{g:02x}{b:02x}"

class Settings:
    """
    @class StyleInfo
    @brief Data class used to hold settings information.
    """
    
    roll_pc_initiative = False
    
    def __init__(self, parent=None):
        """
        @brief Constructor for Settings class.
        Initializes settings information to default values.
        """
        self.resetSettings()
    
    def resetSettings(self):
        """
        @brief Resets all settings information to default values.
        """
        self.roll_pc_initiative = False