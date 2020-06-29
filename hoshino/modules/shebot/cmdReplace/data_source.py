import json
import os

record_path = os.path.join(os.path.dirname(__file__),'records.json')
print (record_path)

def save_record(rec:dict):
    try:
        with open(record_path,'w',encoding='utf8') as f:
            json.dump(rec,f,ensure_ascii=False,indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False
        
def load_records():
    try:
        with open(record_path,'r',encoding='utf8') as f:
            records = json.load(f)
            return records
    except:
        return {}