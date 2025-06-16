class StopAlgorithmException(Exception):
    """
    Raised when user clicks on 'Stop' while the algorithm is running.
    """
    def __init__(self, *args):
        super().__init__(*args)