import argparse
import os
import yaml

DEFAULT_ACTION = "store"


class ArgsParsing:
    # The arguments are declared here purely for autocompletion.
    # .appargs.yml is still source of truth
    action = None
    vault_addr = None
    vault_token = None
    v_ca = None
    dry_run = None

    def __init__(self, args=None, path=None):
        if args is not None:
            arguments = args
        else:
            if path is None:
                path = f"{ os.path.dirname(__file__) }/../.appargs.yml"

            try:
                arguments = self.__load_app_args_file(path)
            except Exception:
                print("No arguments provided")
                exit(1)

        #  Set defaults
        for a in arguments:
            a["access_key"] = a["calls"][0] if "dest" not in a else a["dest"]
            setattr(self, a["access_key"], None if "default" not in a else a["default"])

        self.arguments = arguments

    @staticmethod
    def __load_app_args_file(path):
        with open(path, "r") as f:
            return yaml.safe_load(f.read())

    def get_args(self):
        return self.arguments

    def __parse_cli(self):
        cli_parser = argparse.ArgumentParser()

        cli_parser.add_argument(
            "--env-file",
            action="store",
            dest="env",
            default=None,
            help="Path to an env file",
        )

        for a in self.arguments:
            if "--env-file" in a["calls"]:
                print("--env-file is already declared as a base feature of this app.")
            else:
                params = {
                    "default": None,
                    "action": a["action"] if "action" in a else DEFAULT_ACTION,
                    "help": a["help"] if "help" in a else "",
                }
                if "dest" in a:
                    params["dest"] = a["dest"]

                cli_parser.add_argument(*a["calls"], **params)

        cli_args = cli_parser.parse_args()
        final_args = {}
        for a in self.arguments:
            if getattr(cli_args, a["access_key"]) is not None:
                final_args[a["access_key"]] = getattr(cli_args, a["access_key"])

        return final_args

    def __parse_env(self):
        if "env" in os.environ:
            pass

        args = {}
        for a in self.arguments:
            if "env" in a and a["env"] in os.environ:
                args[a["access_key"]] = os.environ[a["env"]]

        return args

    @classmethod
    def validate_args(self, args, val_list):
        for a in val_list:
            if getattr(args, a) is None:
                raise Exception(f"Argument { a } is not valid.")

    def __parse_conf(self, conf_path):
        args = {}

        with open(conf_path, "r") as f:
            args_as_str = f.readlines()

        env_var_args = {}
        for line in args_as_str:
            kv = line.split("=")
            args[kv[0]] = kv[1:]

        for a in self.arguments:
            if a["env"] in env_var_args:
                args[a["access_key"]] = env_var_args[a["env"]]

        return args

    def parse(self):
        env_args = self.__parse_env()
        cli_args = self.__parse_cli()

        if "env" in cli_args:
            conf_args = self._parse_conf(cli_args["env"])
        elif "env" in env_args:
            conf_args = self._parse_conf(env_args["env"])
        else:
            conf_args = {}

        for k, v in conf_args.items():
            setattr(self, k, v)
        for k, v in env_args.items():
            setattr(self, k, v)
        for k, v in cli_args.items():
            setattr(self, k, v)
