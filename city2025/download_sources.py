import pathlib,json,urllib.request,hashlib,concurrent.futures
root=pathlib.Path(__file__).parent
index=json.loads((root/'source-index.json').read_text())
def fetch(f):
 p=root/'source'/f['path'];p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():b=p.read_bytes()
 else:
  req=urllib.request.Request(f"https://raw.githubusercontent.com/{index['repo']}/{index['commit']}/{f['path']}",headers={'User-Agent':'City2025-offline-validation'})
  with urllib.request.urlopen(req,timeout=45) as r:b=r.read()
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['sha'],f['path']
 p.write_bytes(b)
 return len(b)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:sizes=list(pool.map(fetch,index['files']))
print(json.dumps({'files':len(sizes),'bytes':sum(sizes),'git_blob_hashes':'all_verified','base':index['commit']}))
