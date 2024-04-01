from enum import Enum
from abc import abstractmethod
from PyQt5.QtGui import QImage
class ResultType(Enum):
    TEXT = 0
    IMAGE = 1
    TEXT_AND_NUM = 2

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

class TextWithNumResult(IResult):
    def __init__(self,num:int,result:str) -> None:
        super().__init__()
        self.result = self.gen_result(num,result)
    def GetResultType(self):
        return ResultType.TEXT_AND_NUM
    def SetResult(self,result)->None:
        self.result = result
    def GetResult(self):
        return self.result 
    def gen_result(self,num:int,result:str)->str:
        return str(num)+":*:"+result

class ImageResult(IResult):
    def __init__(self,result:QImage) -> None:
        super().__init__()
        self.result = result
    def GetResultType(self):
        return ResultType.IMAGE
    def SetResult(self,result)->None:
        self.result = result
    def GetResult(self):
        return self.result 
