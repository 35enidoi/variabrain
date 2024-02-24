class BrainException(Exception):
    pass

class SpeinpTooGetError(BrainException):
    pass

class PointError(BrainException):
    pass

class BracketError(BrainException):
    pass

class OpenBracketError(BracketError):
    pass

class CloseBracketError(BracketError):
    pass