import os
import json
import pandas as pd

class SBOMParser:

    def __init__(self, root_directory_path):
        self.root_directory_path = root_directory_path
        self.data = {
            "bom_ref":[],
            "depended_by_ref": [],
            "component_name": [],
            "component_version":[],
            "component_description": [],
            "external_reference_type":[],
            "external_reference_url":[],
            "hash_algorithm": [],
            "hash_content": [],
            "component_supplier_name": [],
            "component_type": [],
            "component_archival_path": [],
            "component_author":[],
            "component_license_name":[]
        }
        self.component_index = 0

    def parse_json_files(self):
        for dirpath, _, filenames in os.walk(self.root_directory_path):
            for filename in filenames:
                # print(dirpath)
                if filename.endswith('.json'):
                    # print(filename)
                    self._process_json_file(os.path.join(dirpath, filename))
    
    def _process_json_file(self, file_path):
        with open(file_path) as file:
            sbom_data = json.load(file)

            metadata = sbom_data.get('metadata', {})
            component_data = metadata.get('component', {})
            author=component_data.get('author','')
            bom_ref=component_data.get('bom-ref','')
            component_version=component_data.get('version','')
            component_name = component_data.get('name', '')
            component_description = component_data.get('description', '')
            hash_algorithm = ','.join([hashes['alg'] for hashes in component_data.get('hashes', [{}]) if hashes.get('alg')])
            hash_content = ','.join([hashes['content'] for hashes in component_data.get('hashes', [{}]) if hashes.get('content')])
            component_type = component_data.get('type', '')
            supplier_name = component_data.get('supplier', {}).get('name', '')
            archival_path = ''.join([prop.get('value') for prop in component_data.get('properties',[{}]) if prop.get('name')=='componentArchivalPath'])
            
            self.component_index=self.get_index(component_name,component_version)

            if self.component_index!=-1:
                self._update_existing_component(component_description,component_type, supplier_name, archival_path,author)
            
            else:
                self._add_new_component(component_name, component_description, hash_algorithm, hash_content, component_type, supplier_name, archival_path,component_version,bom_ref,author)
            
            self._process_dependencies(sbom_data.get("components", []),bom_ref)

    def _update_existing_component(self,description,comp_type, supplier, archival_path,author):
        
        self.data["component_description"][self.component_index] = description
        self.data["component_type"][self.component_index] = comp_type
        self.data["component_supplier_name"][self.component_index] = supplier
        self.data["component_archival_path"][self.component_index] = archival_path
        self.data["component_author"][self.component_index]=author

    def _add_new_component(self, name, description, hash_alg, hash_content, comp_type, supplier, archival_path,component_version,bom_ref,author):
        self.data["bom_ref"].append(bom_ref)
        self.data["depended_by_ref"].append(None)
        self.data["component_name"].append(name)
        self.data["component_author"].append(author)
        self.data["component_description"].append(description)
        self.data["hash_algorithm"].append(hash_alg)
        self.data["hash_content"].append(hash_content)
        self.data["component_type"].append(comp_type)
        self.data["component_supplier_name"].append(supplier)
        self.data["component_archival_path"].append(archival_path)
        self.data["component_version"].append(component_version)
        self.data["component_license_name"].append(None)
        self.data['external_reference_type'].append(None)
        self.data['external_reference_url'].append(None)

    def _process_dependencies(self, dependencies, bom_ref):
        
        for dependency in dependencies:
           
            ind=self.get_index(dependency.get('name',''),dependency.get('version',''),bom_ref)
            if ind==-1:
                self.data["bom_ref"].append(dependency.get('bom-ref',''))
                self.data["component_name"].append(dependency.get('name',''))
                self.data["component_version"].append(dependency.get('version',''))
                self.data["depended_by_ref"].append(bom_ref)
                self.data["component_description"].append(None)
                self.data["component_type"].append(None)
                self.data["component_supplier_name"].append(None)
                self.data["component_archival_path"].append(None)
                self.data['component_author'].append(None)

                external_reference_type = ','.join([ref['type'] for ref in dependency.get('externalReferences',[{}]) if ref.get('type')])
                external_reference_url = ','.join([ref['url'] for ref in dependency.get('externalReferences',[{}]) if ref.get('url')]) 
                component_license_name=','.join([license['license']['name'] for license in dependency.get('licenses',[{}]) if license.get('license',{}).get('name','')])
                hash_algorithm = ','.join([hashes['alg'] for hashes in dependency.get('hashes', [{}]) if hashes.get('alg','')])
                hash_content = ','.join([hashes['content'] for hashes in dependency.get('hashes', [{}]) if hashes.get('content','')])

                self.data['component_license_name'].append(component_license_name)
                self.data['external_reference_type'].append(external_reference_type)
                self.data['external_reference_url'].append(external_reference_url)
                self.data["hash_algorithm"].append(hash_algorithm)
                self.data["hash_content"].append(hash_content)


    def get_index(self, comp_name, version, depended_by_ref=None):
        for i in range(len(self.data.get('component_name')) - 1, -1, -1):
            if (self.data.get('component_name')[i] == comp_name and
                self.data.get('component_version')[i] == version and
                (depended_by_ref is None or self.data.get('depended_by_ref')[i] == depended_by_ref)):
                return i
        return -1     

    def save_to_csv(self, output_file):
        df = pd.DataFrame(self.data)
        for col in df.columns:
            print(col,len(df[col]))
        df.to_csv(output_file, index=False)


if __name__ == "__main__":
    root_directory_path = 'Sample_Telematics_Files - New Version -Provided by Teams'
    output_file = 'components_raw_data2.csv'

    parser = SBOMParser(root_directory_path)
    parser.parse_json_files()
    parser.save_to_csv(output_file)

