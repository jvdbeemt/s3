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

def get_provider(data):
    cloud_provider = data['provider']['name']
    return (cloud_provider)

def get_provider_services(data):
    svcs= []
    services = data['provider']['services']
    for service in range(len(services)):
      svcs.append(services[service]["name"])
    return(svcs)

def get_provider_secrets(data):
    secrets= []
    data_secrets = data['provider']['secrets']
    for secret in range(len(data_secrets)):
      secrets.append(data_secrets[secret]["name"])
    return(secrets)

def s3_data(backup_region='backupemp'):
   get_buckets = os.environ['s3_buckets']
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

def read_vault(vault,secret):
    client = hvac.Client(url=os.environ['VAULT_ADDR'],token=os.environ['VAULT_TOKEN'])
    client.sys.is_initialized()
    if client.is_authenticated():
      read_response = client.secrets.kv.v1.read_secret(vault_path)
      secret_data=read_response['data'][secret]
    return(secret_data)

def cf_s3_login(api,org,user,password):
    shell_cmd(cmd=f"cf login --skip-ssl-validation -a {api} -u {user} -p {password}")
    shell_cmd(cmd=f"cf target {user} -s services")

def cf_s3_create(data):
    shell_cmd(cmd=f"cf create-service s3-bucket standard {product}-{env} -c s3.json")
    shell_cmd(cmd=f"cf create-service-key {product}-{env} {product}-{env}-key")

data = read_json('data.json')
provider = get_provider(data)
env = data['environment']
services = get_provider_services(data)
vault = data['vault']

if 'cloud_foundry' in provider:
  for service in services:
    if 's3' in service:
      _data = s3_data()
      api = os.environ[f"{provider}_api_{env}"]
      org = os.environ[f"{provider}_org_{env}"]
      user = os.environ[f"{provider}_user_{env}"]
      password = os.environ[f"{provider}_password_{env}"]
      cf_s3_login(api,org,user,password)
