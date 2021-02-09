import fnmatch

from models.secret import Secret
from models.policy import Policy
from models.role import Role
from models.release import Release
from models.script import Script
from models.manifest import Manifest

INIT_ORDER = ['secret', 'policy', 'role', 'script', 'manifest', 'release']

REC_TYPES = {
  'secret': Secret,
  'policy': Policy,
  'role': Role,
  'release': Release,
  'script': Script,
  'manifest': Manifest
}

def where_to_insert(resource, exec_list):
  for index, r in enumerate(reversed(exec_list)):
    for after_pattern in resource.get_after():
      if fnmatch.fnmatch(r.get_id(), after_pattern):
        return len(exec_list) - index

  return -1

def get_execution_list(resources):
  locks = []
  exec = []

  for res in resources.values():
    if res.get_after() is None:
      exec.append(res)
    else:
      locks.append(res)

  while len(locks) > 0:
    l = locks.pop(0)
    
    index = where_to_insert(l, exec)
    if index > -1:
      exec.insert(index, l)

    # if not found:
    #   for a in l.get_after():
    #     found = False

    #     for k in resources.keys():
    #       if fnmatch.fnmatch(k, a):
    #         locks.append(l)
    #         found = True
    #         break
        
    #     if not found:
    #       raise Exception(f"Dependency '{ a }' for '{ l.get_id() }' not found")
  
  for e in exec:
    print(e.get_id())

  return exec

def get_resources(raw_resources, vault):
  resources = {}

  for key in INIT_ORDER:
    if key not in raw_resources:
      continue

    for name, v in raw_resources[key].items():
      res_id = f"{key}.{name}"

      if name in resources:
        raise Exception(f"Resource { res_id } already exists")

      rec = REC_TYPES[key](res_id, v, raw_resources, vault) if key in ['secret', 'policy', 'role'] else REC_TYPES[key](res_id, v, raw_resources)
      
      resources[f"{ res_id }"] = rec

  return resources