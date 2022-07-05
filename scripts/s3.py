#!/usr/bin/env python3.9
from component import Component
import os

if __name__ == '__main__':
  s3 = Component()
  provider = s3.provider()
  env = s3.environment()
  services = s3.services()

  if 'cloud_foundry' in provider:
    for service in services:
      if 's3' in service:

        def s3_bucket_data(backup_region='backupemp'):
          get_buckets = os.environ['s3_buckets']
            
          payload = {
            "buckets": []
          }

          buckets = get_buckets.split()
          for b in buckets:
            if 'backup' in b:
              payload['buckets'].append({"name": b,"region":backup_region})
            else:
              payload['buckets'].append({"name": b})
          return(payload)

      s3_data = s3_bucket_data()
      s3_file = 's3.json'
      s3.write_json(s3_data,s3_file)

      api = os.environ[f"{provider}_api_{env}"]
      org = os.environ[f"{provider}_org_{env}"]
      user = os.environ[f"{provider}_user_{env}"]
      password = os.environ[f"{provider}_password_{env}"]
      
      s3.command(cmd=f"cf login --skip-ssl-validation -a {api} -u {user} -p {password}")
      s3.command(cmd=f"cf target {user} -s services")
      s3.command(cmd=f"cf create-service s3-bucket standard {product}-{env} -c s3.json")
      s3.command(cmd=f"cf create-service-key {product}-{env} {product}-{env}-key")
