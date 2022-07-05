#!/usr/bin/env python3.9
import json
import os 
import sys
import subprocess
import select
import hvac

class Component:

    def __init__(self,file_name='data.json'):
        """Wrapper for each component in provider 
        """
        self.file_name = file_name

    def read_json(self):
      with open(self.file_name, 'r') as f:
        data = json.load(f)
      return(data)

    def write_json(self,payload,dest):
      data = json.dumps(payload, indent = 4)
      with open(dest, 'w') as f:
          f.write(data)

    def read_vault(self,vault,secret):
        client = hvac.Client(url=os.environ['VAULT_ADDR'],token=os.environ['VAULT_TOKEN'])
        
        client.sys.is_initialized()
        
        if client.is_authenticated():
          read_response = client.secrets.kv.v1.read_secret(vault_path)
          secret_data=read_response['data'][secret]

        return(secret_data)

    def command(self,cmd):
      process = subprocess.Popen(['/bin/bash','-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      
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
                      exit(1)
              sys.stdout.flush()

          if process.poll() is not None:
              break

    def provider(self):
        data = self.read_json()
        provider = data['provider']['name']
        return(provider)
    
    def environment(self):
        data = self.read_json()
        env = data['environment']
        return(env)

    def services(self):
        data = self.read_json()
        svcs= []
        services = data['provider']['services']
        for service in range(len(services)):
          svcs.append(services[service]["name"])
        return(svcs)
