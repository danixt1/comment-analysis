from .graphic import BaseGraphic
from src.comment import Comment

class PieGraphic(BaseGraphic):
    gname = 'pie'
    def _makeData(self, data):
        raise NotImplementedError("do not call this function direct.")
    def _plot(self, data, ax):
        total = sum(data[0])
        def autopct(pct):
            val = int(round(pct*total/100.0))
            return '{:.2f}%\n({v:d})'.format(pct, v=val)
        ax.pie(data[0], labels=data[1], autopct=autopct)

class ProblemsPieGraphic(PieGraphic):
    gname = "problemsPie"

    def _makeData(self, data:list[Comment]):
        problems = {}
        for comment in data:
            data = comment.getData()
            if data == None or "problems" not in data:
                continue
            if not isinstance(data["problems"],list):
                continue
            
            for problem in data["problems"]:
                if problem in problems:
                    problems[problem] += 1
                else:
                    problems[problem] = 1
        return list(problems.values()), list(problems.keys())

class BehaviorPieGraphic(PieGraphic):
    gname = "behaviorPie"

    def _makeData(self, data:list[Comment]):
        behaviors = {}
        for comment in data:
            data = comment.getData()
            if data == None or "behavior" not in data:
                continue
            if not isinstance(data["behavior"], str):
                continue
            behavior = data["behavior"]
            if behavior in behaviors:
                behaviors[behavior] += 1
            else:
                behaviors[behavior] = 1
        return list(behaviors.values()), list(behaviors.keys())