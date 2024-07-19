import json
import pandas as pd

with open('6366786_SBOM/6366786_SBOM.json','r') as f:
    data=json.load(f)
    metadata=data.get('metadata')
    bom_ref=metadata.get('component').get('bom_ref')
    comp_descr=metadata.get('component').get('description')
    hash_alg=metadata.get('component').get('hashes')[0].get('alg')
    hash_content=metadata.get('component').get('hashes')[0].get('content')
    version=metadata.get('component').get('version')
    type=metadata.get('component').get('type')
    supplier=metadata.get('component').get('supplier').get('name')
    for i in metadata.get('component').get('properties'):
        if i.get('name')=='componentArchivalPath':
            archivalPath = i.get('value') 
    
data={
    'bom_ref':bom_ref,
    "description":comp_descr,
    "hash_alg":hash_alg,
    "hash_content":hash_content,
    "version":version,
    "type":type,
    "archival_path":archivalPath
}
print(data)
df=pd.DataFrame([data])
df.to_csv("component.csv")