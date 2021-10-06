import configparser


def read_config(config_filepath: str, section: str) -> dict:
    parser = configparser.ConfigParser()
    parser.read(config_filepath)

    if not parser.has_section(section):
        raise Exception(f'No section \'{section}\' in config file: \'{config_filepath}\'!')

    config = dict()
    params = parser.items(section)
    for param in params:
        config[param[0]] = param[1]
    return config
