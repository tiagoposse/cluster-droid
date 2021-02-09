from subprocess import check_output
from models.resource import Resource

class Script(Resource):
  def __init__(self, res_id, content, raw):
    super().__init__(res_id, content, raw)

    self.__source = content['source']
    self.__environment = {}
    
    if 'environment' in content:
      for k, v in content['environment'].items():
        self.__environment[k] = v

  def create(self):
    check_output(self.__source, env=self.__environment)

  def is_created(self):
    return False

  def to_json(self):
    return {
      "source": self.__source
    }