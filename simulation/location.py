class Location:
    def __init__(self, name, usage, pos=(0,0), agents=[], objects=[], audios=[]):
        self.name = name
        self.usage = usage
        self.pos = pos
        self.agents = agents
        self.objects = objects
        self.audios = audios