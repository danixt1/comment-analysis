from .graphic import BaseGraphic
from src.comment import Comment

class PieGraphic(BaseGraphic):
    gname = 'pie'
    def _makeData(self, data:list[Comment]):
        problems = {}
        for comment in data:
            data = comment.getData()
            if "problems" not in data:
                continue
            if not isinstance(data["problems"],list):
                continue
            
            for problem in data["problems"]:
                if problem in problems:
                    problems[problem] += 1
                else:
                    problems[problem] = 1
        return list(problems.values()), list(problems.keys())
    def _plot(self, data, ax):
        ax.pie(data[0], labels=data[1], autopct='%1.1f%%')