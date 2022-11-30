import colorlog


def setup_loger():
    logger = colorlog.getLogger('FAMILY_TREE_APP')
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s %(asctime)s %(name)s: %(message)s'))
    logger.setLevel('INFO')
    logger.addHandler(handler)
    return logger
