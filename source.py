from linkedin_library import Query as PersonQuery
from constants import headers, cookies
import requests
import json
from product_hunt_library import Query as ProductQuery

print('Querying LinkedIn')

person_query = PersonQuery(headers, cookies)

leads = person_query.pull_results()

print('Queried LinkedIn')

url = 'https://www.mylasso.app/person/'

for lead in leads:
    myobj = {'data': json.dumps([lead])}
    x = requests.post(url, data=myobj)
    print("People Post Response: ", x.text)

print('Querying Product Hunt')

product_query = ProductQuery(20, 5)
product_leads = product_query.pull_leads()

url = 'https://www.mylasso.app/product/'
myobj = {'data': json.dumps(product_leads)}

x = requests.post(url, data=myobj)

print("Product Post Response: ", x.text)
print('Good Hunting!')
