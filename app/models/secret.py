import logging
import hvac
import random
import re
import string
import os
from typing import Tuple

from models.resource import Resource

logger = logging.getLogger('droid')

class Secret(Resource):
  def __init__(self, res_id, content, raw, vault):
    super().__init__(res_id, content, raw)

    self.__vault = vault

    splitted = content['path'].split("/")

    self.__mount_point = splitted[0]
    self.__path = "/".join(splitted[1:])
    
    self.__k8s = content['k8s'] if 'k8s' in content else None

    self.__values = self.__get_values(content['values'])

  def remove(self):
    self.__vault.delete_secret(self.__path)

  def create(self):
      """
      Check if secret does not exist in vault and/or k8s
      and create it according to the secret definition
      """

      k8s = self.__get_secret_in_k8s()
      vault = self.__get_secret_in_vault()

      creation_values = (
          vault[1] or k8s[1] or self.__values()
      )

      if vault[0]:
          self.__vault.secrets.kv.v2.create_or_update_secret(
            self.__path, secret=creation_values, mount_point=self.__mount_point
        )

      if k8s[0]:
          secret_type = (
              self.__k8s["type"] if "type" in self.__k8s else "generic"
          )
          name = self.__k8s["name"]
          namespace = self.__k8s["namespace"]

          self.k8s.create_k8s_secret(name, creation_values, namespace, secret_type)


  def __get_secret_in_vault(self) -> Tuple[bool, dict]:
      """
      Check if the secret exists in vault and decide whether the secret is to be created

      This function can return: False,None or False,dict or True,None

      :rtype: bool whether the secret should be created
      :rtype: dict the values if they exist, else None
      """
      try:
          secret = self.__vault.secrets.kv.v2.read_secret_version(
              self.__path, mount_point=self.__mount_point
          )

          return secret["data"]["data"] is None, secret["data"]["data"]
      except hvac.exceptions.InvalidPath:
          return True, None


  def __get_secret_in_k8s(self) -> Tuple[bool, dict]:
      """
      Check if the secret is to be created in k8s and
      return the secret values if it already exists

      This function can return: False,None or False,dict or True,None

      :rtype: bool whether to create the secret or not
      :rtype: dict
      """
      if self.__k8s is None:
          return False, None

      values = self.__k8s.get_k8s_secret(
          self.__k8s["name"], self.__k8s["namespace"]
      )

      return values is None, values

  def __get_secret(self):
      """
      Get a secret from k8s and/or vault, depending on the secret definition
      """

      k8s = self.__get_secret_in_k8s()
      vault = self.__get_secret_in_vault()

      return vault[1] or k8s[1] or None

  def is_created(self):
    return self.__get_secret() is not None

  def __get_values(self, vals):
    values = {}

    for k, v in vals.items():
      if 'source' not in v:
        values[k] = v['value']
      elif re.match(r"^gen\[[0-9]{1,4}\]$", v['source']):
        length = re.search(r"\[([0-9]+)\]", v)
        values[k] = self.get_random_string(int(length.group(1)))
      elif v['source'] == "gen":
        values[k] = self.get_random_string()
      elif v['source'] == "env":
        try:
          values[k] = os.environ[v['name']]
        except KeyError:
          logger.fatal(f"Environ value { v['name'] } has not been provided")
          exit(1)
      
    return values

  @staticmethod
  def get_random_string(length=32):
    chars = string.ascii_letters + string.digits
    result_str = "".join(random.choice(chars) for _ in range(length))

    return result_str

  def to_json(self):
    return {
      'path': f"{ self.__mount_point }/{ self.__path }",
      'k8s': self.__k8s,
      'values': self.__values
    }