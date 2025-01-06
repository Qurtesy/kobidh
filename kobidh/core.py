from click import echo


class Apps:
    def __init__(self, name: str, region: str = None):
        self.name = name
        self.region = region
        pass

    def create(self):
        echo(f'Creating app "{self.name}"..')
        pass
