#!/usr/bin/env python3

from typing import Dict, List, Optional, Text, Tuple
import requests
import json
import pypinyin
from collections import namedtuple


class CardInfo:
  def __init__(self, hanzi: str, pinyin: str) -> None:
    self.hanzi = hanzi if not hanzi.startswith('p.') else hanzi[2:]
    self.pinyin = [pinyin] if not pinyin.startswith('{') else pinyin[1:-1].split(',')
    self.pinyin_t = pypinyin.pinyin(self.hanzi, heteronym=True)[0]
    self.pinyin2 = pypinyin.pinyin(self.hanzi, style=pypinyin.Style.TONE3, heteronym=True)[0]
    tones = [x[-1] if x[-1] in ('1', '2', '3', '4') else '5' for x in self.pinyin2]
    self.tones = [f'tone{i}' for i in tones]


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
  return [pypinyin.pinyin(x, heteronym=heteronym)[0] for x in hanzi]

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
  
  for i in range(len(notes)):
    result = update_pinyin(notes[i], pin[i])
    
    
def deck_names_and_ids():
  data = {
    "action": "deckNamesAndIds",
    "version": 6,
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj['result']


def get_hanzi(query: Text) -> Dict[Text, CardInfo]:
  notes = find_notes(query)
  info = notes_info(notes)
  return {x['noteId']: CardInfo(x['fields']['Hanzi']['value'], x['fields']['Pinyin']['value']) 
          for x in info if not x['fields']['Hanzi']['value'].startswith('p.<')}
  
  
def get_pinyin_to_hanzi(hanzi:  Dict[Text, CardInfo]) -> Dict[Text, List[Text]]:
  pin_to_hanzi: dict[str, List[str]] = {}
  for card in hanzi.values():
    pinyin = card.pinyin_t[0]
    if card.hanzi == pinyin: 
      continue
    pin_to_hanzi.setdefault(pinyin, []).append(card.hanzi)
  return pin_to_hanzi


def add_pinyin_notes(notes):
  data = {
    "action": "addNotes",
    "version": 6,
    "params": {
        "notes": notes
    }
  }
  
  x = requests.post('http://localhost:8765', data=json.dumps(data))
  content_obj = json.loads(x.content)
  return content_obj


def create_pinyin_deck():
  # hanzi = get_hanzi('deck:"汉字 3000"')
  # hanzi = get_hanzi('tag:RSH1-01')
  # with open('pinyin.txt', 'w', encoding='utf-8') as f:
  #   f.writelines(f'{v.hanzi} {v.pinyin_t} {v.pinyin}\n' for v in hanzi.values() if set(v.pinyin) != set(v.pinyin_t) and v.pinyin[0] != v.pinyin_t[0])
    # f.writelines(f'{v.hanzi} {v.pinyin_t} {v.pinyin}\n' for v in hanzi.values() if v.pinyin[0] != v.pinyin_t[0])
  
  # hanzi = get_hanzi('tag:RSH2-01')
  hanzi = get_hanzi('deck:"汉字 3000"')
  hanzi_to_card = {x.hanzi: x for x in hanzi.values()}
  pin_to_hanzi = get_pinyin_to_hanzi(hanzi)
  deck_name = '汉字 Pronunciation'

  notes = [
    {
      "deckName": deck_name,
      "modelName": "Pinyin",
      "fields": {
                "Pinyin": p,
                "Hanzi": " ".join(h),
                "Tone": hanzi_to_card[h[0]].tones[0],
                "Pinyin2": hanzi_to_card[h[0]].pinyin2[0]
      },
    } for p, h in pin_to_hanzi.items()]
  notes = sorted(notes, key=lambda x : x["fields"]["Pinyin2"])
  
  result = add_pinyin_notes(notes)
  print(result)


def main():
  print('call a function')

if __name__ == '__main__':
  main()
