import abc
import logging

logger = logging.getLogger('droid')

class Resource(metaclass=abc.ABCMeta):
  __dependencies = None
  __after = None
  __id = None

  def __init__(self, res_id, content, raw):
    self.__raw_resources = raw
    content = self.preprocess(content)

    self.__id = res_id

    if 'after' in content:
      if not isinstance(content['after'], list):
        raise Exception(f"After hook for { self.__id } is not a list")

      self.__after = content['after']
    
    if 'depends_on' in content:
      self.__dependencies = content['depends_on']

  def get_after(self):
    return self.__after

  def get_dependencies(self):
    return self.__dependencies

  def get_id(self):
    return self.__id

  def preprocess(self, item):
    if isinstance(item, dict):
      for k, v in item.items():
        if k in ['after', 'depends_on']:
          self.__validate_ref_field(v)
          item[k] = v
        else:
          item[k] = self.preprocess(v)
    elif isinstance(item, list):
      item = [ self.preprocess(item_val) for item_val in item ]
    else:
      item = str(item)
      while item.startswith(">>"):
        item = self.__get_reference(item[2:])

    return item

  def __validate_ref_field(self, v):
    return [ self.__get_reference(val) for val in v ]

  def __get_reference(self, v):
    info = v.split('.')

    v = self.__raw_resources
    for i in info:
      try:
        v = v[i]
      except KeyError:
        logger.fatal(f"{ '.'.join(info) } is a reference to an unknown resource")
        exit(1)

    return v