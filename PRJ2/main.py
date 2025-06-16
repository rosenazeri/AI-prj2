import pygame
import pygame_gui
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from myCSP.mycsp import *
from sudoku import *
from exceptions import StopAlgorithmException

# Constants
WIDTH, HEIGHT = 450, 650
GRID_WIDTH, GRID_HEIGHT = 450, 450
GRID_SIZE = 9
CELL_SIZE = GRID_WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_GRAY = (200, 200, 200)

button_width = 120
button_height = 40
selection_list_height = 30
button_y = 475
spacing = 20

class SudokuGUI:
    """
    A graphical user interface (GUI) for solving Sudoku puzzles using Constraint Satisfaction Problem (CSP) techniques.

    This class integrates Pygame and Pygame GUI elements to provide an interactive way to load, visualize,
    and solve Sudoku puzzles using different CSP strategies.
    
    Attributes:
        root (tk.Tk): A hidden Tkinter root window used for file dialogs.
        screen (pygame.Surface): The main Pygame display surface.
        font (pygame.Font): Standard font used for rendering numbers.
        small_font (pygame.Font): Smaller font used for displaying possible numbers in each cell.
        clock (pygame.time.Clock): Pygame clock for controlling frame rate.
        manager (pygame_gui.UIManager): Manages the UI elements.
        layout_path (str): Path to the current Sudoku layout file.
        solve_button (UIButton): Button to start (or stop) solving the Sudoku.
        load_button (UIButton): Button to load a new Sudoku puzzle.
        library_dropdown (UIDropDownMenu): Dropdown menu for selecting the CSP solver (mycsp or pycsp).
        unary_checkbox, arc_checkbox, realtime_checkbox, mrv_checkbox, lcv_checkbox (UISelectionList): Checkboxes for enabling/disabling different CSP heuristics.
        board (Board): Represents the Sudoku board state.
        running (bool): Controls the main event loop.
    """
    def __init__(self):
        # Create a hidden root window using Tkinter (for file dialogs)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku CSP")
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))

        # Set up fonts
        self.font = pygame.font.Font(None, 40)          # Main font for numbers
        self.small_font = pygame.font.Font(None, 15)    # Smaller font for possible numbers

        # Improve ui theme
        pygame.font.init()
        self.manager.get_theme().load_theme('theme.json')

        # Create UI elements and initialize them
        self.create_ui_elements()

        # Default Sudoku layout path
        self.layout_path = 'layouts/peaceful.sudoku'

    def get_button_rect(self, i, j):
        """Returns a rectangle for button placement based on grid position."""
        return pygame.Rect((30 + j * (button_width + spacing), button_y + i * 50), (button_width, button_height))

    def get_selection_list_rect(self, i, j):
        """Returns a rectangle for selection list placement based on grid position."""
        return pygame.Rect((30 + j * (button_width + spacing), button_y + i * 50), (button_width, selection_list_height))

    def create_ui_elements(self):
        """Creates all UI elements such as buttons and selection lists."""
        # row 0
        self.solve_button = pygame_gui.elements.UIButton(relative_rect=self.get_button_rect(0, 0), 
                                                    text='Solve', manager=self.manager)
        self.load_button = pygame_gui.elements.UIButton(relative_rect=self.get_button_rect(0, 1), 
                                                text='Load', manager=self.manager)

        self.library_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=['pycsp', 'mycsp'], starting_option='mycsp', 
                                                            relative_rect=self.get_button_rect(0, 2), manager=self.manager)

        # row 1
        self.unary_checkbox = pygame_gui.elements.UISelectionList(relative_rect=self.get_selection_list_rect(1, 0), 
                                                            item_list=['Unary Checker'], manager=self.manager)
        self.arc_checkbox = pygame_gui.elements.UISelectionList(relative_rect=self.get_selection_list_rect(1, 1), 
                                                        item_list=['Arc Consistency'], manager=self.manager)
        self.realtime_checkbox = pygame_gui.elements.UISelectionList(relative_rect=self.get_selection_list_rect(1, 2), 
                                                                item_list=['real-time'], manager=self.manager,
                                                                default_selection='real-time')
        
        # row 2
        self.mrv_checkbox = pygame_gui.elements.UISelectionList(relative_rect=self.get_selection_list_rect(2, 0), 
                                                                item_list=['MRV'], manager=self.manager)
        self.lcv_checkbox = pygame_gui.elements.UISelectionList(relative_rect=self.get_selection_list_rect(2, 1), 
                                                                item_list=['LCV'], manager=self.manager)

    def draw_grid(self):
        """Draws the Sudoku grid on the screen."""
        self.screen.fill(WHITE)
        for i in range(GRID_SIZE + 1):
            thickness = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (0, i * CELL_SIZE), (GRID_WIDTH, i * CELL_SIZE), thickness)
            pygame.draw.line(self.screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, GRID_HEIGHT), thickness)

    def draw_numbers(self, prev_board, board, color):
        """Draws numbers on the Sudoku board."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board[row][col] != 0 and prev_board[row][col] == 0:
                    text = self.font.render(str(board[row][col]), True, color)
                    text_rect = text.get_rect(center=((col + 0.5) * CELL_SIZE, (row + 0.5) * CELL_SIZE))
                    self.screen.blit(text, text_rect)

    def draw_remaining_domains(self, board, remaining_domains, color):
        """Draws possible numbers (remaining domains) in each cell."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board[row][col] == 0:  # Only show for empty cells
                    possibilities = sorted(remaining_domains[row][col])  # Sort for consistent display
                    for idx, num in enumerate(possibilities):
                        pos_x = col * CELL_SIZE + (idx % 3) * (CELL_SIZE // 3) + 5
                        pos_y = row * CELL_SIZE + (idx // 3) * (CELL_SIZE // 3) + 5
                        text = self.small_font.render(str(num), True, GRAY)
                        self.screen.blit(text, (pos_x, pos_y))
    
    def solve_clicked(self, time_delta):
        """Handles the Solve button click event."""
        self.solve_button.set_text('Stop')
        self.manager.update(time_delta)
        self.sudoku = Layout(self.layout_path)

        # Determine which solving techniques to use
        algorithm = self.library_dropdown.selected_option[0] # 'pycsp' / 'mycsp'
        do_unary_check = self.unary_checkbox.get_single_selection() is not None
        do_arc_consistency = self.arc_checkbox.get_single_selection() is not None
        real_time = self.realtime_checkbox.get_single_selection() is not None
        do_mrv = self.mrv_checkbox.get_single_selection() is not None
        do_lcv = self.lcv_checkbox.get_single_selection() is not None

        # clear the board
        self.board.guess_board = self.board.empty_board
        self.board.answer_board = self.board.empty_board

        # Attempt to solve the puzzle
        try:
            success = self.sudoku.solve(algorithm, 
                                        do_unary_check, 
                                        do_arc_consistency, 
                                        do_mrv,
                                        do_lcv,
                                        real_time, 
                                        self.board,
                                        self.refresh,
                                        self.get_stop_event)
        except StopAlgorithmException:
            success = None

        if success is not None and not success:
            messagebox.showerror("Error", "The puzzle was not solvable!")

        self.solve_button.set_text('Solve')

    def load_clicked(self):
        """Handles the Load button click event."""
        path = filedialog.askopenfilename(title="Select a sudoku layout")
        if path is not None and path != "":
            self.layout_path = path
        print(self.layout_path)
        self.sudoku = Layout(self.layout_path)
        self.board.layout_board = self.sudoku.get_clues()
        self.board.guess_board = self.board.empty_board
        self.board.answer_board = self.board.empty_board
        self.board.remaining_domains = [[[] for i in range(9)] for j in range(9)]

    def get_stop_event(self) -> bool:
        """Checks for user interaction events to determine if solving should stop."""
        time_delta = self.clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return True
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.solve_button:
                    return True
            self.manager.process_events(event)

        self.manager.update(time_delta)
        return False

    def refresh(self):
        """Refreshes the UI by redrawing the Sudoku board and UI elements."""
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_numbers(self.board.empty_board, self.board.layout_board, BLACK)
        self.draw_numbers(self.board.layout_board, self.board.guess_board, BLUE)
        self.draw_numbers(self.board.combine_boards(
            self.board.layout_board, self.board.guess_board), 
            self.board.answer_board, 
            RED)
        self.draw_remaining_domains(self.board.combine_boards(
            self.board.combine_boards(self.board.layout_board, self.board.guess_board), self.board.answer_board), 
            self.board.remaining_domains, GRAY)
        self.manager.draw_ui(self.screen)
        pygame.display.flip()

    def main(self):
        """Main loop for the Sudoku CSP GUI."""
        """Main loop of the Sudoku CSP."""

        self.board = Board()
        
        self.running = True
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.solve_button:
                        self.solve_clicked(time_delta)
                    elif event.ui_element == self.load_button:
                        self.load_clicked()
                self.manager.process_events(event)

            self.manager.update(time_delta)
            
            self.refresh()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sudoku_gui = SudokuGUI()
    sudoku_gui.main()
