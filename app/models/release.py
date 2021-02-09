from subprocess import check_output
from models.resource import Resource

class Release(Resource):
    def __init__(self, res_id, content, raw):
      super().__init__(res_id, content, raw)

      self.__name         = content['name']
      self.__namespace    = content['namespace']
      self.__version      = content['version']
      self.__chart        = content['chart']
      self.__repo         = content['repo'] if 'repo' in content else None
      self.__values_files = content['valuesFiles'] if 'valuesFiles' in content else []
      self.__wait         = True

    def create(self):
      if '/' not in self.__chart:
        self.__get_chart()
        target = f"/tmp/{ self.__chart }-{ self.__version }.tgz"
      else:
        target = self.__chart

      cmd = ['helm', 'upgrade', '-i', '-n', self.__namespace, self.__name, target]
      for v in self.__values_files:
        cmd += ['-f', v]

      check_output(cmd)

    def remove(self):
      check_output(['helm', 'uninstall', '-n', self.__namespace, self.__name])

    def is_created(self):
      cmd = ['helm', 'list', '-A', '--filter', f"^{ self.name }$"]
      output = check_output(cmd)
      return len(output.decode('utf-8').split('\n')) > 0

    def __get_chart(self):
      cmd = [
        'helm', 'pull',
        '--version', self.__version,
        '--repo', self.__repo,
        '-d', f"/tmp",
        self.__chart
      ]

      check_output(cmd)

    def to_json(self):
      return {
        "name": self.__name,
        "chart": self.__chart,
        "namespace": self.__namespace,
        "version": self.__version
      }
