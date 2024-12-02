from pathlib import Path
import json
import re
import itertools
import random

commentsData = json.loads((Path(__file__).parent / 'comments_data.json').read_text(encoding='utf-8'))

MATCH_POSITIONS = r"\[([^\]]+)\]"
MATCH_FULL_POSITIONS = r"\[[^\]]+\]"
MATCH_VARIATIONS = r"[^|]+"


def makeData(limit:int,exclude_tags = [],searchIn = commentsData):
    counts ={'positive':0, 'negative':0,'-':0}
    totalCount = 0
    stopProcess = False
    maxPositives = int(limit * 0.70)
    comments = []
    addComment = lambda data,msg = None: comments.append(
        {
            'message':data['message'] if msg is None else msg, 
            'type':data['type'] if 'type' in data else 'comment', 
            'origin':'test',
            'expected':{
                'spam':data['spam'] if 'spam' in data else False,
                'behavior':data['behavior'] if 'behavior' in data else '-',
                'min_problems':data['min_problems'] if 'min_problems' in data else 0
            }
        })
    def addToCount(behavior):
        nonlocal totalCount, stopProcess
        if behavior == 'positive' and counts['positive'] >= maxPositives:
            return False
        if totalCount >= limit:
            stopProcess = True
            return False
        counts[behavior] += 1
        totalCount += 1
        return True
    def fromMessages(c):
        for message in c['messages']:
            variations = getVariations(message)
            for variation in variations:
                
                if stopProcess:
                    return
                if not addToCount(behavior):
                    break
                addComment(c,variation)

    for c in searchIn:
        behavior = c['behavior']
        if stopProcess:
            break
        if 'message' in c:
            if addToCount(behavior):
                addComment(c)
        elif 'messages' in c:
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

def makeCSV(outFile:str,config:dict = {'limit':100},useData = commentsData):
    import csv
    data = makeData(**config,searchIn=useData)
    with open(outFile, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['message', 'type','origin'])
        writer.writeheader()
        for row in data:
            del row['expected']
            writer.writerow(row)