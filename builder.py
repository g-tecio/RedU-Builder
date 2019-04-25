import json
import requests
import boto, os
from boto.s3.connection import Location
from boto.s3.key import Key
import sys
import boto.cloudformation



#Get data from GraphQL API
api_token = 'da2-fp2jl3o5vbeujik2p6k26sbshi'
api_url_base = 'https://cs7ammbpdrfmjay76wqwkjuemi.appsync-api.us-east-1.amazonaws.com/graphql'

headers = {
    'Content-Type': 'application/json',
    'x-api-key': api_token
}

query = {
    'query': 'query getPage{ getPage(id:"61f2c4ad-ac22-42a2-bf1a-eebe6d7d59a1" ) { title summary } }'
}

response = requests.post(url=api_url_base, json=query, headers=headers)
response_json = json.loads(json.dumps(response.json()))
obj = response_json["data"]["getPage"]

#Bucket Configuration
LOCAL_PATH = 'tmp/'
AWS_ACCESS_KEY_ID = 'AKIA3XC2ASUZQ5WNC5GE'
AWS_SECRET_ACCESS_KEY = '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'
template_bucket_name = 'red-dgo-templates'
template_id = 'papeleria'
business = 'laescolar'

conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
template_bucket = conn.get_bucket(template_bucket_name)

template_bucket_list = template_bucket.list()

#Download template from bucket
for l in template_bucket_list:
    key_string = str(l.key)
    template_parent = l.key.split("/")[0]
    s3_path = LOCAL_PATH + key_string
    if template_parent == template_id:
        if not os.path.exists(s3_path):
            try:
                separator = "/"
                aux_path = s3_path.split("/")
                aux_path.pop()
                result_path = separator.join(aux_path)
                if not os.path.exists(result_path):
                    os.makedirs(result_path)
            except (OSError) as e:
                pass
    try:
        if template_parent == template_id:
            l.get_contents_to_filename(s3_path)            
    except (OSError) as e:
        pass
        
            


#Fill template with the DB info
index_html = ''
index_path = 'tmp/%s/index.html' % (template_id)

with open(index_path, 'r') as f:
    index_html = f.read()

for key, value in obj.items():
    index_html = index_html.replace("{{" + key + "}}", value)
    owf = open(index_path, 'w')
    owf.write(index_html)

#Create S3 bucket 
website_path = 'tmp/%s/' % (template_id)
bucket_name = "laescolar.reddgo.mx"
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, is_secure=False)
bucket = conn.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT, policy='public-read')

files = []
policy = """{
    "Version": "2012-10-17",
    "Id": "Policy1543528092408",
    "Statement": [
        {
            "Sid": "Stmt1543528090946",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::laescolar.reddgo.mx/*"
        }
    ]
}"""

#Upload files to s3 bucket
for (r, d, f) in os.walk(website_path):
    for file in f:
        if '.' in file:
            files.append(os.path.join(r, file))

def percent_cb(complete, total):
    sys.stdout.flush()

for filename in files:
    sourcepath = os.path.join(filename)
    destpath = os.path.join('/', filename.split('tmp/' + template_id + "/")[1])
    print(filename)

    k = boto.s3.key.Key(bucket)
    k.key = destpath
    k.set_contents_from_filename(sourcepath,
            cb=percent_cb, num_cb=10)

#Setup website
bucket.set_acl('public-read')
bucket.configure_website('index.html', 'error.html')
bucket.set_policy(str(policy), headers=None)
result = bucket.get_website_configuration()

#Create Subdomain
subdomain = '%s.reddgo.mx' % (business)
command_stack = 'aws cloudformation create-stack --stack-name %s --template-body file://subdomain.yaml --parameters ParameterKey=SubdomainName,ParameterValue=%s' % (business, subdomain)
print(command_stack)
os.system(command_stack) 

print("Finished")
