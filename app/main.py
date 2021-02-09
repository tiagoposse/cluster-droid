import hcl
import os
import logging
import hvac
import glob

from execution import get_resources, get_execution_list
from utils import merge


logger = logging.basicConfig(level=logging.DEBUG)


LOAD_PATH = "."

def get_vault_client():
    with open(os.environ['VAULT_TOKEN'], "r") as f:
        token = f.read().rstrip()

    client = hvac.Client(url=os.environ['VAULT_ADDR'], token=token)
    if client.is_authenticated():
        return client
    else:
        raise Exception("Authentication to vault unsuccessful")


def main():
  files = glob.glob(f"{ LOAD_PATH }/*.hcl")

  content = {}
  for path in files:
    with open(path, 'r') as f:
      content = merge(content, hcl.load(f))

  vault = get_vault_client()
  resources = get_resources(content, vault)
  execution = get_execution_list(resources)

  for elem in execution:
    print(elem.to_json())
    elem.create()


if __name__ == "__main__":
  main()