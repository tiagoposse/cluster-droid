import hvac
import logging
from models.resource import Resource

logger = logging.getLogger('')

class Policy(Resource):
  def __init__(self, res_id, content, raw, vault):
    super().__init__(res_id, content, raw)

    self.__vault = vault
    self.__name = content['name']
    self.__content = ""

    for p in content['content']:
        caps = p["capabilities"] if "capabilities" in p else ["read", "list"]
        path = p['path'].split('/')
        if path[1] != "data":
          path.insert(1, 'data')

        self.__content += (
            f"path \"{ '/'.join(path) }\" {{\n  capabilities = {caps}\n}}\n".replace(
                "'", '"'
            )
        )

  def create(self):
    logger.debug(f"Creating policy {self.__name}")
    self.__vault.sys.create_or_update_policy(self.__name, self.__content)

  def remove(self):
    self.__vault.delete_policy(self.__name)

  def is_created(self):
    try:
      self.__vault.sys.read_policy(name=self.__name)
      return True
    except hvac.exceptions.InvalidPath as e:
      return False