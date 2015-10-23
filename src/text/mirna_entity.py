from text.entity import Entity

__author__ = 'Andre'


class MirnaEntity(Entity):
    def __init__(self, tokens, **kwargs):
        # Entity.__init__(self, kwargs)
        super(MirnaEntity, self).__init__(tokens, **kwargs)
        self.type = "mirna"
        self.subtype = kwargs.get("subtype")
        self.mirna_acc = None
        self.mirna_name = 0