#!/usr/bin/env python3
"""Convert EDRDG JMdict_e.gz into a compact offline Kotoba Meteor lexicon.
Usage: python3 build_meteor_lexicon.py path/to/JMdict_e.gz
Output: meteor-lexicon.json (run from this standalone project root).
"""
import gzip, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

TOPICS = {
 'education': r'school|university|college|student|teacher|classroom|lesson|education|examination|textbook|kindergarten',
 'fruit': r'fruit|apple|pear|peach|strawberry|grape|orange|melon|cherry|persimmon|plum|banana',
 'plants': r'plant|tree|flower|leaf|leaves|root|branch|grass|forest|bamboo|blossom',
 'transport': r'train|car|vehicle|bus|airplane|aircraft|bicycle|subway|ship|boat|transport|traffic',
 'weather': r'weather|rain|snow|wind|cloud|thunder|storm|typhoon|fog|sunshine',
 'food': r'food|meal|rice|meat|fish|vegetable|egg|milk|bread|cheese|cooking',
 'medicine': r'medicine|hospital|doctor|nurse|patient|illness|disease|treatment|medical',
 'government': r'government|politics|minister|parliament|election|law|policy|mayor',
 'nature': r'mountain|river|sea|lake|island|valley|ocean|desert|landscape',
 'time': r'morning|evening|night|today|tomorrow|yesterday|week|month|year|hour',
 'people': r'person|people|man|woman|child|family|parent|friend|worker',
 'movement': r'walk|run|swim|fly|climb|move|travel|advance|descend|jump',
 'communication': r'speak|say|tell|talk|write|read|ask|answer|communicat|explain',
 'emotion': r'happy|sad|fear|angry|love|worry|surpris|lonely|joy',
 'commerce': r'shop|store|bank|money|buy|sell|price|market|business|trade',
 'technology': r'computer|software|machine|internet|technology|data|device',
}
TOPIC_RE={k:re.compile(r'\b(?:'+v+r')\b',re.I) for k,v in TOPICS.items()}
VERB_POS={'v1','v1-s','v2a-s','v2b-k','v2b-s','v2d-k','v2d-s','v2g-k','v2g-s','v2h-k','v2h-s','v2k-k','v2k-s','v2m-k','v2m-s','v2n-s','v2r-k','v2r-s','v2s-s','v2t-k','v2t-s','v2w-s','v2y-k','v2y-s','v2z-s','v4b','v4g','v4h','v4k','v4m','v4n','v4r','v4s','v4t','v5aru','v5b','v5g','v5k','v5k-s','v5m','v5n','v5r','v5r-i','v5s','v5t','v5u','v5u-s','v5uru','vi','vk','vn','vr','vs','vs-c','vs-i','vs-s','vz'}
def pos_info(tags,jp):
 if any(t in VERB_POS or t.startswith(('v5','v1','vs-')) for t in tags):
  if any(t.startswith('v5') for t in tags):return 'verb','godan'
  if any(t.startswith('v1') for t in tags):return 'verb','ichidan'
  if any(t.startswith('vs') for t in tags):return 'verb','suru'
  return 'verb','irregular'
 if any(t.startswith('adj-i') for t in tags):return 'adjective','i'
 if any(t in ('adj-na','adj-no','adj-t','adj-f') for t in tags):return 'adjective','na'
 if any(t.startswith('adv') for t in tags):return 'adverb',None
 if any(t.startswith(('n','ctr','suf','pref')) for t in tags):return 'noun',None
 return None,None

def main():
 if len(sys.argv)<2:
  raise SystemExit('Usage: python3 build_meteor_lexicon.py ~/Downloads/JMdict_e.gz')
 source=Path(sys.argv[1]);op=Path('meteor-lexicon.json')
 opener=gzip.open if source.suffix=='.gz' else open
 words={}
 with opener(source,'rb') as stream:
  for _,elem in ET.iterparse(stream,events=('end',)):
   if elem.tag!='entry':continue
   kanji=[x.text for x in elem.findall('./k_ele/keb') if x.text]
   readings=[x.text for x in elem.findall('./r_ele/reb') if x.text]
   if not readings:elem.clear();continue
   senses=elem.findall('./sense');tags=[];glosses=[]
   for sense in senses:
    tags += [x.text for x in sense.findall('pos') if x.text]
    glosses += [x.text for x in sense.findall('gloss') if x.text and (x.attrib.get('{http://www.w3.org/XML/1998/namespace}lang','eng')=='eng')]
   if not glosses:elem.clear();continue
   jp=kanji[0] if kanji else readings[0]
   reading=readings[0]
   pos,verbclass=pos_info(tags,jp)
   if not pos or len(jp)>9 or len(reading)>14:elem.clear();continue
   meaning=glosses[0][:95]
   topics=[name for name,pattern in TOPIC_RE.items() if pattern.search(' '.join(glosses[:4]))]
   priority=bool(elem.findall('./k_ele/ke_pri') or elem.findall('./r_ele/re_pri'))
   w={'jp':jp,'reading':reading,'en':meaning,'pos':pos}
   if verbclass:w['verbClass']=verbclass
   if pos=='verb':w['ending']=reading[-1]
   if topics:w['topics']=topics[:3]
   # Prefer priority forms, but retain broad coverage for unfamiliar NHK vocabulary.
   if jp not in words or (priority and not words[jp][0]):words[jp]=(priority,w)
   elem.clear()
 entries=[w for _,w in sorted(words.values(),key=lambda p:(not p[0],p[1]['jp']))]
 # Bound embedded Worker size; prioritize common dictionary entries.
 entries=entries[:18000]
 op.write_text(json.dumps(entries,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print(f'Wrote {len(entries):,} entries to {op} ({op.stat().st_size/1024/1024:.2f} MiB)')
 print('Source: JMdict © EDRDG, CC BY-SA 4.0 — https://www.edrdg.org/edrdg/licence.html')
if __name__=='__main__':main()
