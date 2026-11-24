import xml.etree.ElementTree as ET, re, unicodedata, collections, sys, json
root = ET.parse('x.xml').getroot()
fonts = {}; pages = {}
for page in root.iter('page'):
    pn = int(page.get('number'))
    for fs in page.iter('fontspec'): fonts[fs.get('id')] = (int(fs.get('size')), fs.get('family').split('+')[1], fs.get('color'))
    L = []
    for t in page.findall('text'):
        top, left, w = int(t.get('top')), int(t.get('left')), int(t.get('width'))
        if top < 70 or top > 1105: continue
        size, fam, col = fonts[t.get('font')]
        s = unicodedata.normalize('NFKC', ''.join(t.itertext())).replace(' ', ' ')
        L.append(dict(top=top, left=left, right=left + w, size=size, fam=fam, col=col, i=t.find('.//i') is not None, b=t.find('.//b') is not None, t=s))
    pages[pn] = L
json.dump(pages, open('pages.json', 'w'))
if __name__ == '__main__':
    c = collections.Counter(); ex = {}
    for pn in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        for d in pages[pn]:
            k = (d['size'], d['fam'], d['col'], d['i'], d['b'])
            c[k] += 1; ex.setdefault(k, (pn, d['left'], d['t'][:60]))
    for k, n in c.most_common(60): print(n, k, ex[k])
