"""Offline catalogue/matcher validation. Does not import vehicle interfaces or access hardware."""
import ast,copy,hashlib,importlib,itertools,json,pathlib,sys,types,collections,difflib,os
root=pathlib.Path(__file__).parent
source=root/'source'
sys.path.insert(0,str(source/'opendbc_repo'))
if os.environ.get('CITY2025_PYTHON_DEPS'):sys.path.insert(1,os.environ['CITY2025_PYTHON_DEPS'])
from opendbc.car.structs import CarParams
from opendbc.car.fw_query_definitions import ESSENTIAL_ECUS
from opendbc.car.honda.values import CAR
Ecu=CarParams.Ecu
fw_path='opendbc_repo/opendbc/car/honda/fingerprints.py'
text=(source/fw_path).read_text(encoding='utf-8')
new_versions=[('eps',0x18da30f1,'39990-T14-B510'),('gateway',0x18daeff1,'38897-T14-M210'),('srs',0x18da53f1,'77959-T14-B810'),('fwdRadar',0x18dab0f1,'8S102-T14-P020'),('vsa',0x18da28f1,'57114-T14-M510'),('transmission',0x18da1ef1,'28101-63B-M510')]
tree=ast.parse(text)
fw_assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FW_VERSIONS' for t in n.targets))
city=next(v for k,v in zip(fw_assignment.value.keys,fw_assignment.value.values) if isinstance(k,ast.Attribute) and k.attr=='HONDA_CITY_7G')
lines=text.splitlines(keepends=True);insert=[]
for ecu,addr,fw in new_versions:
 node=next(v for k,v in zip(city.keys,city.values) if k.elts[0].attr==ecu and ast.literal_eval(k.elts[1])==addr)
 assert (fw.encode()+b'\0\0') not in ast.literal_eval(node)
 insert.append((node.elts[-1].end_lineno,"      b'"+fw+"\\x00\\x00',\n"))
for pos,line in sorted(insert,reverse=True):lines.insert(pos,line)
candidate_text=''.join(lines);ast.parse(candidate_text)
candidate=root/'candidate'/fw_path;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(candidate_text,encoding='utf-8',newline='')
(root/'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),candidate_text.splitlines(True),fromfile='a/'+fw_path,tofile='b/'+fw_path)),encoding='utf-8')
# Load real value classes, schemas, query configuration and all distributed catalogues.
versions={};configs={};failures={}
for p in sorted((source/'opendbc_repo/opendbc/car').glob('*/fingerprints.py')):
 brand=p.parent.name
 try:
  values=importlib.import_module('opendbc.car.'+brand+'.values')
  catalogue=importlib.import_module('opendbc.car.'+brand+'.fingerprints')
  versions[brand]=catalogue.FW_VERSIONS;configs[brand]=values.FW_QUERY_CONFIG
 except Exception as exc:failures[brand]=repr(exc)
assert not failures, failures
baseline={c:d for brand in versions.values() for c,d in brand.items()}
ns={'__name__':'opendbc.car.honda.fingerprints_candidate'}
exec(compile(candidate_text,str(candidate),'exec'),ns)
updated=copy.deepcopy(baseline);updated.update(ns['FW_VERSIONS'])
car=CAR.HONDA_CITY_7G
added=[];removed=[];other=[]
for c in baseline:
 for ecu,fws in baseline[c].items():
  a=set(updated[c][ecu])-set(fws);r=set(fws)-set(updated[c][ecu])
  added.extend((str(c),ecu,fw.hex()) for fw in a);removed.extend((str(c),ecu,fw.hex()) for fw in r)
 if c!=car and updated[c]!=baseline[c]:other.append(str(c))
assert len(added)==6 and not removed and not other
# Execute the pinned functions unchanged; loading every runtime dependency would import hardware/interface code.
matcher=(source/'opendbc_repo/opendbc/car/fw_versions.py').read_text(encoding='utf-8')
keep={'is_brand','build_fw_dict','match_fw_to_car_exact','match_fw_to_car_fuzzy','match_fw_to_car'}
nodes=[n for n in ast.parse(matcher).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in keep]
g={'defaultdict':collections.defaultdict,'CarParams':CarParams,'Ecu':Ecu,'ESSENTIAL_ECUS':ESSENTIAL_ECUS,'FW_QUERY_CONFIGS':configs,'VERSIONS':versions,'FW_VERSIONS':baseline,'MODEL_TO_BRAND':{c:b for b,v in versions.items() for c in v},'carlog':types.SimpleNamespace(error=lambda *a,**k:None)}
exclude=next(n for n in ast.parse(matcher).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FUZZY_EXCLUDE_ECUS' for t in n.targets))
exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),exclude]+nodes,type_ignores=[])),str(source/'opendbc_repo/opendbc/car/fw_versions.py'),'exec'),g)
live={(addr,None):{fw.encode()+b'\0\0'} for ecu,addr,fw in new_versions}
records=[types.SimpleNamespace(brand='honda',logging=False,address=addr,subAddress=0,fwVersion=fw.encode()+b'\0\0') for ecu,addr,fw in new_versions]
results=[]
def record(name,condition,details=None):
 results.append({'test':name,'passed':bool(condition),'details':details})
 assert condition,(name,details)
def exact(db,data=live):g['FW_VERSIONS']=db;return g['match_fw_to_car_exact'](data,log=False)
record('baseline_no_exact_match',exact(baseline)==set())
record('candidate_unique_exact',exact(updated)=={car})
g['FW_VERSIONS']=updated
record('candidate_generic_fuzzy_unique',g['match_fw_to_car_fuzzy'](live,log=False)=={car})
record('combined_prefers_exact',g['match_fw_to_car'](records,vin='',log=False)==(True,{car}))
record('logging_only_responses_ignored',g['build_fw_dict']([types.SimpleNamespace(**{**vars(x),'logging':True}) for x in records])=={})
successful_subsets=[]
for mask in range(64):
 db=copy.deepcopy(baseline)
 for i,(ecu,addr,fw) in enumerate(new_versions):
  if mask&(1<<i):db[car][(getattr(Ecu,ecu),addr,None)].append(fw.encode()+b'\0\0')
 matches=exact(db)
 record('firmware_subset_'+str(mask),matches==({car} if mask==63 else set()))
 if matches:successful_subsets.append(mask)
for ecu,addr,fw in new_versions:
 data=copy.deepcopy(live);data[(addr,None)]={b'INVALID_TEST_VALUE\0\0'}
 record('unknown_'+ecu+'_rejects_exact',exact(updated,data)==set())
 record('unknown_'+ecu+'_fuzzy_no_other_platform',g['match_fw_to_car_fuzzy'](data,log=False)<={car})
 data=copy.deepcopy(live);data[(addr,None)]={fw.encode()}
 record('missing_terminator_'+ecu+'_rejects_exact',exact(updated,data)==set())
for mask in range(64):
 data={k:v for i,(k,v) in enumerate(live.items()) if mask&(1<<i)}
 before=exact(baseline,data);after=exact(updated,data)
 record('partial_inventory_'+str(mask)+'_no_new_other_platform',(after-before)<={car})
# Complete old Honda fixtures must retain exactly the same matches except the newly supported City candidate.
for c,entries in versions['honda'].items():
 data={}
 for (ecu,addr,sub),fws in entries.items():data.setdefault((addr,sub),set()).update(fws)
 before=exact(baseline,data);after=exact(updated,data)
 record('preserve_catalogue_'+str(c),before<=after and (after-before)<={car})
record('six_additions_zero_deletions',len(added)==6 and not removed and not other)
result={'base':'728f654727be9ecb71c16d95bd869ed051bb147f','branch':'FrogPilot-Testing','catalogues':len(versions),'platforms':len(baseline),'firmware_evidence':'Six address/version pairs reconstructed from public PR #322; not a fresh ECU query or replay of the complete private 17-response inventory.','matching_execution':'Real pinned catalogue/schema/config imports; five unchanged functions selected via AST. This is not a full runtime import/startup test.','passed':len(results),'failed':0,'successful_addition_subsets':successful_subsets,'candidate_blob':hashlib.sha1(b'blob '+str(len(candidate.read_bytes())).encode()+b'\0'+candidate.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'results':results,'limitations':['No full Linux/ARM64 CI or runtime build','No installed-device audit: SSH identity changed and awaiting confirmation','No on-car validation','Brand-specific fuzzy functions only exercised if selected by combined matcher; no exhaustive fuzzy fallback suite','Testing launcher requests AGNOS 12.8; no installation or AGNOS change authorized by test result']}
(root/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
