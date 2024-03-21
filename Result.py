from enum import Enum
from abc import abstractmethod
class ResultType(Enum):
    TEXT = 0
    IMAGE = 1
    HYPER_TEXT = 2

class IResult:
    def __init__(self) -> None:
        pass
    @abstractmethod
    def GetResultType(self):
        return None
    @abstractmethod
    def SetResult(self,result)->None:
        pass
    @abstractmethod
    def GetResult(self):
        pass

class TextResult(IResult):
    def __init__(self,result=None) -> None:
        super().__init__()
        self.result = result
    def GetResultType(self):
        return ResultType.TEXT
    def SetResult(self,result)->None:
        self.result = result
    def GetResult(self):
        return self.result 

