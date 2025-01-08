import csv

def load_entsoe_country_keys(file_path='entsoe_tables/entsoe_country_keys.csv'):
    entsoe_country_keys = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            entsoe_country_keys[row['country']] = row['key']
    return entsoe_country_keys

def load_entsoe_gentype_names(file_path='entsoe_tables/entsoe_gentype_names.csv'):
    entsoe_gentype_names = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            entsoe_gentype_names[row['key']] = row['name']
    return entsoe_gentype_names