#!/usr/bin/env python3

from typing import List
import requests
import json
from pypinyin import pinyin


def find_notes(query: str):
  data = {
    "action": "findNotes",
    "version": 6,
    "params": {
        "query": query
    }
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj['result']

def notes_info(notes: List[str]):
  data = {
    "action": "notesInfo",
    "version": 6,
    "params": {
        "notes": notes
    }
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj['result']


def transliterate(hanzi: List[str], heteronym=False):
  return [pinyin(x, heteronym=heteronym)[0] for x in hanzi]

def update_pinyin(note, pin: List[str]):
  actual_pin = pin[0] if len(pin) == 1 else "{" + ','.join(pin) + "}"
  data = {
    "action": "updateNote",
    "version": 6,
    "params": {
        "note": {
          "id": note,
          "fields": {
            "Pinyin": actual_pin
          }
        }
    }
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj
  

def add_pinyin():
  notes = find_notes("tag:RSH2")
  info = notes_info(notes)
  
  hanzi = [x['fields']['Hanzi']['value'] for x in info]
  
  pin = transliterate(hanzi)
  print(notes, pin)
  
  for i in range(len(notes)):
    result = update_pinyin(notes[i], pin[i])
    print(result)
    
    
def deck_names_and_ids():
  data = {
    "action": "deckNamesAndIds",
    "version": 6,
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj['result']


def create_pinyin_deck():
  notes = find_notes('deck:"汉字 3000"')
  info = notes_info(notes)
  hanzi = [x['fields']['Hanzi']['value'] for x in info]
  hanzi = [x for x in hanzi if not x.startswith('p.')]
  pin = transliterate(hanzi, heteronym=False)
  pin = [x[0] for x in pin]
  
  with open('pinyin.txt', 'w', encoding='utf-8') as f:
    f.writelines(f'{hanzi[i]} {pin[i]}\n' for i in range(len(hanzi)))
  
  pin_to_hanzi: dict[str, List] = {}
  for i in range(len(hanzi)):
    if pin[i] not in pin_to_hanzi:
      pin_to_hanzi[pin[i]] = []
    pin_to_hanzi.get(pin[i], []).append(hanzi[i])
  print(pin_to_hanzi)
  
def main():
  create_pinyin_deck()

if __name__ == '__main__':
  main()
