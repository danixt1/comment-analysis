from ..comment import Comment
from .promptInfo import PromptInfo

from abc import ABC
class ClientObserver(ABC):
    """
    Override the functions to get the state of call
    """
    def notify_batchs_generated(self,batchs:list[list[Comment]]):
        """Notify after comments being separated in batchs to send to the AI, pass the batchs generated"""
        pass
    def notify_new_prompt_generated(self,prompt:PromptInfo):
        pass
    def notify_data_added_to_comment(self,data:dict,targetComment:Comment):
        pass
    def notify_max_retrys_reached(self,comments:list[Comment],prompt):
        pass
    def notify_tokens_cost_from_analyze(self,tokens:int):
        """pass the total cost of all prompts sended to AI to by analyzed after calling `analyze` function"""
        pass