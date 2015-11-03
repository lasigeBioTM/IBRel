from text.entity import Entity

__author__ = 'Andre'


class ProteinEntity(Entity):
    def __init__(self, tokens, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")


    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic