from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QGridLayout, QScrollArea, QWidget, QCheckBox, QSizePolicy
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
import random
import os

class DiceRollerWindow(QDialog):
    """
    @class DiceRollerWindow
    @brief Dialog window for rolling dice, displaying results, and managing dice sets.
    """

    def __init__(self, parent=None):
        """
        @brief Constructor for DiceRollerWindow.
        @param parent The parent widget.
        Initializes the UI, dice selection, display area, and connects signals.
        """
        super().__init__(parent)
        self.setWindowTitle("Dice Roller")
        self.resize(800, 600)  # Set an initial size
        self.setWindowModality(Qt.WindowModality.NonModal)  # Allow interaction with the main window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Dice selection layout
        self.dice_selection_layout = QVBoxLayout()
        self.add_dice_selection()  # Add the first dice selection by default
        main_layout.addLayout(self.dice_selection_layout)

        # Add Dice and Remove Dice buttons
        button_layout = QHBoxLayout()
        self.add_dice_button = QPushButton("Add Dice")
        self.add_dice_button.clicked.connect(self.add_dice_selection)
        button_layout.addWidget(self.add_dice_button)

        self.remove_dice_button = QPushButton("Remove Dice")
        self.remove_dice_button.clicked.connect(self.remove_last_dice_selection)
        button_layout.addWidget(self.remove_dice_button)

        main_layout.addLayout(button_layout)

        # Roll button
        self.roll_button = QPushButton("Roll")
        self.roll_button.clicked.connect(self.roll_dice)
        main_layout.addWidget(self.roll_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Scrollable dice display area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.dice_display_widget = QWidget()
        self.dice_display_layout = QGridLayout(self.dice_display_widget)
        self.dice_display_widget.setLayout(self.dice_display_layout)
        self.scroll_area.setWidget(self.dice_display_widget)
        main_layout.addWidget(self.scroll_area)

        # Result label
        self.result_label = QLabel("Result: ")
        self.result_label.setFont(QFont("Arial", 14))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.result_label)

        # Path to the dice images folder
        self.dice_images_path = os.path.join(os.path.dirname(__file__), "Settings", "Dice")

        # Store rolled dice results for redrawing
        self.rolled_dice_sets = []

        # Track the dice size
        self.dice_size = 80

        # Track the number of columns
        self.max_columns = 10

        # Recalculate layout on resize
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        @brief Handle window resize events to recalculate dice layout.
        @param source The event source.
        @param event The event object.
        @return True if the event was handled, otherwise calls the base implementation.
        """
        if event.type() == QEvent.Type.Resize:
            self.redraw_dice()
        return super().eventFilter(source, event)

    def add_dice_selection(self):
        """
        @brief Add a new dice selection dropdown row to the UI.
        """
        dice_selection_row = QHBoxLayout()

        # Number of Dice dropdown
        num_dice_label = QLabel("Number of Dice:")
        num_dice_dropdown = QComboBox()
        num_dice_dropdown.addItems([str(i) for i in range(1, 51)])  # Allow selection of 1 to 50 dice
        num_dice_dropdown.setFixedWidth(100)
        num_dice_label.setBuddy(num_dice_dropdown)  # Attach the dropdown to the label

        # Dice Type dropdown
        dice_type_label = QLabel("Dice Type:")
        dice_type_dropdown = QComboBox()
        dice_type_dropdown.addItems(["d4", "d6", "d8", "d10", "d12", "d20", "d100"])  # Supported dice types
        dice_type_dropdown.setFixedWidth(100)
        dice_type_label.setBuddy(dice_type_dropdown)  # Attach the dropdown to the label

        # Highlight Max Roll checkbox
        highlight_max_checkbox = QCheckBox("Highlight Max Roll")
        highlight_max_checkbox.setChecked(False)

        # Highlight Min Roll checkbox
        highlight_min_checkbox = QCheckBox("Highlight Min Roll")
        highlight_min_checkbox.setChecked(False)

        # Add widgets to the row
        dice_selection_row.addWidget(num_dice_label)
        dice_selection_row.addWidget(num_dice_dropdown)
        dice_selection_row.addWidget(dice_type_label)
        dice_selection_row.addWidget(dice_type_dropdown)
        dice_selection_row.addWidget(highlight_max_checkbox)
        dice_selection_row.addWidget(highlight_min_checkbox)

        # Store the widgets for later use
        dice_selection_row.num_dice_dropdown = num_dice_dropdown
        dice_selection_row.dice_type_dropdown = dice_type_dropdown
        dice_selection_row.highlight_max_checkbox = highlight_max_checkbox
        dice_selection_row.highlight_min_checkbox = highlight_min_checkbox

        # Add the row to the layout
        self.dice_selection_layout.addLayout(dice_selection_row)

    def remove_last_dice_selection(self):
        """
        @brief Remove the last added dice selection row from the UI and update the display.
        """
        if self.dice_selection_layout.count() > 0:
            # Remove the last row from the layout
            last_row = self.dice_selection_layout.takeAt(self.dice_selection_layout.count() - 1)
            if last_row:
                while last_row.count():
                    widget = last_row.takeAt(0).widget()
                    if widget:
                        widget.deleteLater()

            # Remove the last set of dice from the rolled dice sets
            if self.rolled_dice_sets:
                self.rolled_dice_sets.pop()

            # Redraw the dice to reflect the updated sets
            self.redraw_dice()

    def roll_dice(self):
        """
        @brief Roll all dice according to the current selections and store the results.
        """
        self.rolled_dice_sets = []  # Clear previous results

        # Iterate through all dice selections
        for i in range(self.dice_selection_layout.count()):
            dice_selection_row = self.dice_selection_layout.itemAt(i)
            if isinstance(dice_selection_row, QHBoxLayout):
                num_dice = int(dice_selection_row.num_dice_dropdown.currentText())
                dice_type = dice_selection_row.dice_type_dropdown.currentText()
                num_sides = int(dice_type[1:])  # Extract the number of sides from the dice type (e.g., "d6" -> 6)
                highlight_max = dice_selection_row.highlight_max_checkbox.isChecked()
                highlight_min = dice_selection_row.highlight_min_checkbox.isChecked()

                # Roll the dice for this set
                current_set = []
                for _ in range(num_dice):
                    roll = random.randint(1, num_sides)
                    current_set.append((dice_type, roll, highlight_max, highlight_min))

                # Add the current set to the rolled dice sets
                self.rolled_dice_sets.append(current_set)

        self.redraw_dice()

    def redraw_dice(self):
        """
        @brief Redraw the dice display area based on the current window size and rolled results.
        """
        # Clear previous dice display
        for i in reversed(range(self.dice_display_layout.count())):
            widget = self.dice_display_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Calculate the number of columns that can fit
        available_width = self.scroll_area.viewport().width()
        self.max_columns = max(1, available_width // self.dice_size)

        # Ensure no dice are partially visible
        if available_width % self.dice_size != 0:
            self.max_columns -= 1

        row, col = 0, 0
        total_sum = 0  # Store the total sum of all dice
        result_text = ""  # Text to display the results

        # Iterate through each set of rolled dice
        for set_index, dice_set in enumerate(self.rolled_dice_sets):
            set_sum = 0  # Sum of the current set
            result_text += f"Set {set_index + 1}: "

            # Start a new row for each set
            if col != 0:
                row += 1
                col = 0

            # Process each dice in the set
            for dice_index, (dice_type, roll, highlight_max, highlight_min) in enumerate(dice_set):
                # If starting a new row within the set, calculate padding
                if col == 0:
                    remaining_dice = len(dice_set) - dice_index
                    if remaining_dice < self.max_columns:
                        padding = (self.max_columns - remaining_dice) // 2
                    else:
                        padding = 0

                    # Add left padding
                    for _ in range(padding):
                        empty_label = QLabel()
                        empty_label.setFixedSize(self.dice_size, self.dice_size)
                        self.dice_display_layout.addWidget(empty_label, row, col)
                        col += 1

                # Load the dice image
                dice_image_path = os.path.join(self.dice_images_path, f"{dice_type}.png")
                if not os.path.exists(dice_image_path):
                    continue

                # Create a new pixmap with a fixed size
                base_pixmap = QPixmap(self.dice_size, self.dice_size)
                base_pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(base_pixmap)

                # Highlight max or min rolls
                if highlight_max and roll == int(dice_type[1:]):
                    painter.fillRect(base_pixmap.rect(), QColor("green"))
                elif highlight_min and roll == 1:
                    painter.fillRect(base_pixmap.rect(), QColor("red"))

                # Draw the dice image centered on the background
                dice_pixmap = QPixmap(dice_image_path)
                scaled_dice_pixmap = dice_pixmap.scaled(self.dice_size - 10, self.dice_size - 10, Qt.AspectRatioMode.KeepAspectRatio)
                x_offset = (base_pixmap.width() - scaled_dice_pixmap.width()) // 2
                y_offset = (base_pixmap.height() - scaled_dice_pixmap.height()) // 2
                painter.drawPixmap(x_offset, y_offset, scaled_dice_pixmap)

                # Draw the roll number on top of the dice
                painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                painter.setPen(QColor("black"))
                painter.drawText(base_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, str(roll))
                painter.end()

                # Create a QLabel for the dice image
                dice_label = QLabel()
                dice_label.setPixmap(base_pixmap)
                dice_label.setFixedSize(self.dice_size, self.dice_size)
                self.dice_display_layout.addWidget(dice_label, row, col)

                # Update the set sum and total sum
                set_sum += roll
                total_sum += roll

                # Update row and column for grid layout
                col += 1
                if col >= self.max_columns:
                    col = 0
                    row += 1

            # Add right padding for the last row of the set
            if col != 0:
                remaining_space = self.max_columns - col
                for _ in range(remaining_space):
                    empty_label = QLabel()
                    empty_label.setFixedSize(self.dice_size, self.dice_size)
                    self.dice_display_layout.addWidget(empty_label, row, col)
                    col += 1

            # Add the set result to the result text
            result_text += f"(Sum: {set_sum})\n"

        # Add the total result to the result text
        result_text += f"Total: {total_sum}"
        self.result_label.setText(result_text)