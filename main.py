import sys
from core.config_utils import Config, load_module

if __name__ == '__main__':

    cfg = Config(sys.argv[1])

    ConverterClass = load_module(cfg.converter)
    converter = ConverterClass(**cfg.backup_params)

    converter.run()
