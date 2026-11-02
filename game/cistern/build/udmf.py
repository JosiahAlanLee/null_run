import re,json,struct
def parse(text):
 d={k:[] for k in ('vertex','linedef','sidedef','sector','thing')}
 for k,b in re.findall(r'\b(vertex|linedef|sidedef|sector|thing)\s*\{([^}]+)\}',text):
  row={}
  for key,v in re.findall(r'(\w+)\s*=\s*("[^"]*"|[^;]+);',b):
   try:row[key]=json.loads(v)
   except ValueError:row[key]=float(v)
  d[k].append(row)
 return d
def emit(d):
 return 'namespace="zdoom";\n'+''.join(k+' { '+ ' '.join(f'{a}={json.dumps(b)};' for a,b in r.items())+' }\n' for k,rows in d.items() for r in rows)
def lumps(data):
 _,n,p=struct.unpack_from('<4sII',data);return [(name.rstrip(b'\0'),data[o:o+s]) for o,s,name in (struct.unpack_from('<II8s',data,p+i*16) for i in range(n))]
def merge(a,b):
 off={k:len(v) for k,v in a.items()}
 for row in b['linedef']:
  for key,kind in [('v1','vertex'),('v2','vertex'),('sidefront','sidedef'),('sideback','sidedef')]:
   if row.get(key,-1)>=0:row[key]+=off[kind]
 for row in b['sidedef']:row['sector']+=off['sector']
 for k in a:a[k]+=b[k]
 return off

