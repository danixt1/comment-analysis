### Helper python file to add new data to dataset.
### init this file IN THE DATASET FOLDER and edit inserter.txt after saving the inserter.txt all changes is automatic added to dataset.csv

import os
import time
import csv
import re
from pathlib import Path
inserter_filename = "inserter.txt"
info_messages = [
    "A mensagem/comentario/avaliação do usuario",
    "tipo(social,worker->avaliacao de funcionario,comment)",
    "o comportamento analisado na mensagem(positive,negative,neutral)",
    "Se a mensagem é ou não spam(true,false)",
    "quantidades de problemas minimos que a IA deverá indentificar",
    "um comentario adicional para auto ánalise de prompt da IA (não obrigatório)"
]
def toPrint(message):
    if __name__ == '__main__':
        print(message)
def invalidOp(data):
    toPrint("Attention you have one invalid option possible options: "+ ",".join(data))
    return None
def printAndRetNone(message):
    toPrint(message)
    return None
strLambda = lambda x: x
inLambda = lambda x,y:x.lower() if x.lower() in y else invalidOp(y)
info = {
    "message":strLambda,
    "type":lambda x:inLambda(x,["social","worker","comment"]),
    "behavior":lambda x:inLambda(x,["positive","negative","neutral","question"]),
    "spam": lambda x:"1" if x == "true" or x == "1"  else "0",
    "problems": lambda x:x if x.isnumeric() else printAndRetNone("Expected numeric value in problems collum"),
    "comment": strLambda
}
insertOrder = ["message","type","behavior","spam","problems","comment"]
titlesInFile = ["# {} {}".format(insertOrder[pos],info_messages[pos]) for pos in range(len(insertOrder))]

def clearInserterFiler():
    with open(inserter_filename,"w", encoding="utf-8") as inserter:
        inserter.write("\n\n".join(titlesInFile) + '\n\n')
        
def extractDataFrom(text:str):
    data = {}
    for title in insertOrder:
        data[title] = None
    data["comment"] = ""
    lines = text.splitlines()
    prop = ""
    content = ""
    for line in lines:
        isTitle = re.match(r'#\s+(\w+)',line)
        if not isTitle == None:
            content = content.strip()
            if content and prop:
                data[prop] =info[prop](content)
                content = ""
            prop =isTitle[1]
            continue
        content += line + '\n'
    if content and prop:
        data[prop] =info[prop](content.strip())
    return data
if __name__ == '__main__':
    print("started!, awaiting for files changes...")
    if(not os.path.isfile(inserter_filename)):
        clearInserterFiler()

    last_modify = os.path.getmtime(inserter_filename)
    while True:
        time.sleep(0.4)
        current_mtime = os.path.getmtime(inserter_filename)
        if(current_mtime == last_modify):
            continue
        print("modifications detected!")

        data = extractDataFrom(Path(inserter_filename).read_text(encoding='utf-8'))
        if all([x is not None for x in data]):
            last_modify = current_mtime
            print("Not finished yet...")
            continue
            
        with open("dataset.csv","a",newline='') as dataset:
            writer = csv.writer(dataset)
            writer.writerow([data[x] for x in insertOrder])
            print("Data saved!")
        time.sleep(0.1)
        last_modify = os.path.getmtime(inserter_filename)
        clearInserterFiler()
