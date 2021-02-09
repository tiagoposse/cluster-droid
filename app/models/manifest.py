from subprocess import check_output
from models.resource import Resource

class Manifest(Resource):
  def __init__(self, res_id, content, raw):
    super().__init__(res_id, content, raw)

    self.__source = content['source'] if 'source' in content else None
    self.__content = content['content'] if 'content' in content else None

    if self.__content is None and self.__source is None:
      raise Exception(f"Manifest { res_id } is empty")

  def create(self):
    cmd = ['kubectl', 'apply', '-f', self.__source]
    check_output(cmd)

  def remove(self):
    cmd = ['kubectl', 'delete', '-f', self.__source]
    check_output(cmd)

  def is_created(self):
    return False

  def to_json(self):
    return {
      'source': self.__source
    }