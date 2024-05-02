class InconsistentKeyError(KeyError):
    """Exception raised when the provided option sequence for a run is not consistent."""
    def __init__(self, message="Options specified for the run are inconsistent with the system prompts. Revisit the arguments."):
        self.message = message
        super().__init__(self.message)
