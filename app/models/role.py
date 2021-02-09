from models.resource import Resource
import hvac
import logging

logger = logging.getLogger('droid')

class Role(Resource):
  def __init__(self, res_id, content, raw, vault):
    super().__init__(res_id, content, raw)

    self.__vault = vault
    self.__name = content['name']

    if not isinstance(content['namespaces'], list):
      logger.fatal(f"Provided namespaces for { self.__name } is not a list")
    if not isinstance(content['service_accounts'], list):
      logger.fatal(f"Provided serv accounts for { self.__name } is not a list")
    if not isinstance(content['policies'], list):
      logger.fatal(f"Provided policies for { self.__name } is not a list")

    self.__namespaces = [ ns for ns in content['namespaces'] ]    
    self.__service_accounts = [ sa for sa in content['service_accounts'] ]
    self.__policies = [ pol for pol in content['policies'] ]

  def remove(self):
    self.__vault.delete_vault_kubernetes_role(self.__name)

  def create(self):
    self.__vault.create_kubernetes_role(
      self.__name,
      self.__service_accounts,
      self.__namespaces,
      policies=self.__policies
    )

  def is_created(self):
    try:
      self.__vault.get_kubernetes_role(self.__name)
      return True
    except hvac.exceptions.InvalidPath as e:
      return False

  def to_json(self):
    return {
      "name": self.__name,
      "namespaces": self.__namespaces,
      "service_accounts": self.__service_accounts,
      "policies": self.__policies
    }