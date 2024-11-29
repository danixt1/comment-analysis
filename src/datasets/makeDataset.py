from pathlib import Path
import json
import re
import itertools
import random

commentsData = json.loads((Path(__file__).parent / 'comments_data.json').read_text(encoding='utf-8'))

MATCH_POSITIONS = r"\[([^\]]+)\]"
MATCH_FULL_POSITIONS = r"\[[^\]]+\]"
MATCH_VARIATIONS = r"[^|]+"


def makeData(limit:int,exclude_tags = []):
    counts ={'positive':0, 'negative':0,'-':0}
    maxPositives = int(limit * 0.70)
    searchIn = commentsData
    comments = []
    addComment = lambda msg,commentType,spam,behavior: comments.append(
        {
            'message':msg, 
            'type':commentType, 
            'process':{
                "name":"auto-generated",
                'data':{'spam':spam, 'behavior':behavior}
                }
        })
    def addToCount(behavior):
        if behavior == 'positive' and counts['positive'] >= maxPositives:
            return False
        counts[behavior] += 1
        return True
    def fromMessages(c):
        for message in c['messages']:
            variations = getVariations(message)
            for variation in variations:
                if not addToCount(behavior):
                    break
                addComment(variation, commentType, spam, behavior)

    for c in searchIn:
        behavior = c['behavior']
        commentType = c['type'] if 'type' in c else 'comment'
        spam = c['spam'] if 'spam' in c else False
        if 'message' in c:
            message = c['message']
            if addToCount(behavior):
                addComment(message,commentType,spam,behavior)
            continue
        if 'messages' in c:
            fromMessages(c)
            continue
        raise Exception(f"Unknown comment type: {c}")
    random.shuffle(comments)
    return comments
        
            

def getCombinations(text:str):
    replacers = [re.findall(MATCH_VARIATIONS,x) for x in re.findall(MATCH_POSITIONS, text)]
    return list(itertools.product(*replacers))

def getVariations(text:str,combinations = None):
    combinations =getCombinations(text) if combinations is None else combinations
    texts = []
    for combination in combinations:
        variation = text
        toReplace = re.findall(MATCH_FULL_POSITIONS, text)
        for i in range(len(combination)):
            variation = variation.replace(f"{toReplace[i]}",combination[i])
        texts.append(variation)
    return texts

def makeCSV(outFile:str,config:dict = {}):
    import csv
    data = makeData(**config)
    with open(outFile, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['message', 'type'])
        writer.writeheader()
        for row in data:
            del row['process']
            writer.writerow(row)