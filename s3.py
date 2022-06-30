#!/usr/bin/env python3.9
import json
import os 
import sys
import subprocess
import select
import hvac
import secrets
import string

def shell_cmd(cmd):
    process = subprocess.Popen(['/bin/bash','-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(process)
    while True:
      reads, _, _ = select.select(
          [process.stdout.fileno(), process.stderr.fileno()],
          [], []
      )
      for descriptor in reads:
          if descriptor == process.stdout.fileno():
              read = process.stdout.readline()
              if read:
                  print('stdout: %s' % read)

          if descriptor == process.stderr.fileno():
              read = process.stderr.readline()
              if read:
                  print('stderr: %s' % read)
          sys.stdout.flush()

      if process.poll() is not None:
          break

def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return(data)

def json_to_file(payload,dest):
    data = json.dumps(payload, indent = 4)
    with open(dest, 'w') as f:
        f.write(data)

def get_cf_service():
    data = read_json('data.json')
    for service in  data['cloud_foundry']['services']:
      if 's3' in service:
          generate_cf_s3 = cf_s3()
          cf_s3_login()
          cf_s3_create()

def cf_s3(backup_region='backupemp'):
   get_buckets = os.environ['S3_BUCKETS']
   dest = f"s3.json"

   payload = {
    "buckets": []
   }

   buckets = get_buckets.split()
   for _b in buckets:
    if 'backup' in _b:
      payload['buckets'].append({"name":_b,"region":backup_region})
    else:
      payload['buckets'].append({"name": _b})
   json_to_file(payload,dest)

def read_vault(secrets):
    data = read_json('data.json')
    vault_path = data['vault']
    client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
    client.sys.is_initialized()
    for secret in secrets[0].keys():
        if client.is_authenticated():
            read_response = client.secrets.kv.v1.read_secret(vault_path)
            secret_data=read_response['data'][secret]
    return(secret_data)

def cf_s3_login():
    data = read_json('data.json')
    product = data['product']
    env = data['environment']
    api = os.environ[f"cf_api_{env}"]
    user = os.environ[f"cf_user_{env}"]
    secrets = data['cloud_foundry']['secrets']
    secret_key = 'password'
    get_secret = read_vault(secrets)

    shell_cmd(cmd=f"cf login --skip-ssl-validation -a {api} -u {user} -p {get_secret}")
    shell_cmd(cmd=f"cf target {user} -s services")


def cf_s3_create():
    data = read_json('data.json')
    product = data['product']
    env = data['environment']
    shell_cmd(cmd=f"cf create-service s3-bucket standard {product}-{env} -c s3.json")
    shell_cmd(cmd=f"cf create-service-key {product}-{env} {product}-{env}-key")

cf_s3_login()
cf_s3_create()


