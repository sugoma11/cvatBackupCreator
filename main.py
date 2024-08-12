from utils import Config, load_module

if __name__ == '__main__':
    cfg = Config('config.yaml')

    ConverterClass = load_module(cfg.converter)
    converter = ConverterClass(**cfg.backup_params)

    converter.run()
