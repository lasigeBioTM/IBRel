from text.entity import Entity

__author__ = 'Andre'


class ProteinEntity(Entity):
    def __init__(self, tokens, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, *args, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")
        # print self.sid


    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic

    def validate(self, ths, rules):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        # if "stopwords" in rules:
        return True