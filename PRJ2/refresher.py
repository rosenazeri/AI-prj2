from myCSP.mycsp import *
from exceptions import StopAlgorithmException

class Refresher:
    """
    Handles real-time visualization updates for the CSP solver.
    Tracks changes in variable assignments and remaining domains, 
    refreshing the display when necessary.
    """
    
    def __init__(self, vars: myVarArray, board: Board, real_time: bool, refresh: Callable[[],None], get_stop_event: Callable[[], bool]):
        """
        Initializes the Refresher.

        Args:
            vars (myVarArray): The array of CSP variables (board numbers).
            board (Board): The board representation used for visualization.
            real_time (bool): Whether updates should be displayed in real time.
            refresh (Callable[[], None]): Function to refresh the visualization.
            get_stop_event (Callable[[], bool]): Function to check if the algorithm should stop.
            It also handles UI events.
        """
        self.vars = vars
        self.board = board
        self.real_time = real_time
        self.refresh = refresh
        self.get_stop_event = get_stop_event

        # Stores the previous state of the board to detect changes.
        self.prev_guess_board = board.guess_board
        self.prev_remaining_domains = board.remaining_domains

    def refresh_screen(self):
        """
        Refreshes the screen if real-time updates are enabled.
        Checks for changes in variable assignments or domain reductions.
        If changes occur, updates the visualization and checks for stop conditions.
        """
        if not self.real_time:
            return
        
        # Retrieve current variable assignments.
        values: List[List] = my_values(self.vars)
        # Replace None values with 0 for visualization.
        values = [[0 if u is None else u for u in v] for v in values]

        # Retrieve current remaining domains for all variables.
        remaining_domains: List[List[List]] = my_remaining_domains(self.vars)

        # Update the board state.
        self.board.guess_board = values
        self.board.remaining_domains = remaining_domains

        # If the board state has changed, refresh the visualization.
        if self.changed():
            self.refresh()
            # If a stop event is triggered, raise an exception to halt execution.
            if self.get_stop_event():
                raise StopAlgorithmException()
            
        # Update the previous board state for future comparisons.
        self.prev_guess_board = self.board.guess_board
        self.prev_remaining_domains = self.board.remaining_domains

    def changed(self) -> bool:
        """
        Checks whether the board state has changed since the last update.

        Returns:
            bool: True if either the variable assignments or remaining domains have changed, False otherwise.
        """
        return self.prev_guess_board != self.board.guess_board or \
               self.prev_remaining_domains != self.board.remaining_domains