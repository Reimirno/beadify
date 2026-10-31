config = {
    'GUI': False,
    'K': 5,
    'CELL_SIZE': 20,
    'SOLID_ONLY': True,
    'AVAILABLE_ONLY': True,
}

class Config:
    def __init__(self, config):
        self.__dict__ = config

config = Config(config)

def main():
    if config.GUI:
        import gui
        gui.main()
    else:
        import cli
        cli.main()

if __name__ == "__main__":
    main()
