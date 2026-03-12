import argparse
import re

AI_PATTERNS = [r'\bdelve into\b', r'\bin conclusion\b', r'\bmoreover\b', r'\bleverage\b']


def detect(text):
    hits = []
    for p in AI_PATTERNS:
        if re.search(p, text, re.I):
            hits.append(p)
    return hits


def rewrite(text, channel='generic'):
    out = text
    replacements = {
      r'\bdelve into\b':'look at',
      r'\bin conclusion\b':'to wrap up',
      r'\bmoreover\b':'also',
      r'\bleverage\b':'use'
    }
    for k, v in replacements.items():
        out = re.sub(k, v, out, flags=re.I)
    if channel == 'x':
        out = out[:260]
    elif channel == 'linkedin':
        out = out.replace('. ', '.\n\n')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('text')
    ap.add_argument('--channel', choices=['x','linkedin','blog','email','generic'], default='generic')
    ap.add_argument('--rationale', action='store_true')
    a = ap.parse_args()
    h = detect(a.text)
    r = rewrite(a.text, a.channel)
    print(r)
    if a.rationale:
        print({'detected': h, 'changes': 'rule-based simplification + channel tuning'})
