from budgetkey_api.modules.search import TYPES, DATAPACKAGE_BASE
import requests
import os

SRC_DATAPACKAGE_BASE = 'http://next.obudget.org/datapackages/budgetkey/{}/datapackage.json'

if __name__ == '__main__':
    for t in TYPES:
        print('Fetching', t)
        os.makedirs('/'.join(DATAPACKAGE_BASE.split('/')[:-1]), exist_ok=True)
        r = requests.get(SRC_DATAPACKAGE_BASE.format(t))
        with open(DATAPACKAGE_BASE.format(t), 'wb') as f:
            f.write(r.content)
