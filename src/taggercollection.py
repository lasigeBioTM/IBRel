import logging
import Queue

from simpletagger import feature_extractors
from results import ResultSetNER
from stanfordner import StanfordNERModel
from process_type import process_type
import multiprocessing

__author__ = 'Andre'
chemdnerModels = "bc_systematic bc_formula bc_trivial bc_abbreviation bc_family"


class TaggerCollection(object):
    '''
    Collection of tagger classifiers used to train and test specific subtype models
    '''
    CHEMDNER_TYPES =  ["IDENTIFIER", "MULTIPLE", "FAMILY", "FORMULA", "SYSTEMATIC", "ABBREVIATION", "TRIVIAL"]
    GPRO_TYPES = ["NESTED", "IDENTIFIER", "FULL_NAME", "ABBREVIATION"]
    DDI_TYPES = ["drug", "group", "brand", "drug_n"]


    def __init__(self, basepath, baseport = 9191, **kwargs):
        self.models = {}
        self.basepath = basepath
        self.corpus = kwargs.get("corpus")
        submodels = []
        #if "submodels" in kwargs:
        #    for s in kwargs.get("submodels"):
        #        submodels.append(s)
        #else:
        #    submodels.append("")
        self.baseport = baseport
        self.types = []
        #for s in submodels:
        if basepath.split("/")[-1].startswith("chemdner+ddi"):
            self.types = self.DDI_TYPES + self.CHEMDNER_TYPES + ["chemdner", "ddi"]
        elif basepath.split("/")[-1].startswith("ddi"):
            self.types = self.DDI_TYPES + ["all"]
        elif basepath.split("/")[-1].startswith("chemdner") or basepath.split("/")[-1].startswith("cemp"):
            self.types = ["all"] + self.CHEMDNER_TYPES
        elif basepath.split("/")[-1].startswith("gpro"):
            self.types = self.GPRO_TYPES + ["all"]
        #self.basemodel = SimpleTaggerModel(self.basepath)
        self.basemodel = StanfordNERModel(self.basepath)

    def train_types(self):
        """
        Train models for each subtype of entity, and a general model.
        :param types: subtypes of entities to train individual models, as well as a general model
        """
        self.basemodel.load_data(self.corpus, feature_extractors.keys(), subtype="all")
        for t in self.types:
            typepath = self.basepath + "_" + t
            model = StanfordNERModel(typepath, subtypes=self.basemodel.subtypes)
            model.copy_data(self.basemodel, t)
            logging.info("training subtype %s" % t)
            model.train()
            self.models[t] = model

    def load_models(self):
        for i, t in enumerate(self.types):
            model = StanfordNERModel(self.basepath + "_" + t, subtypes=self.basemodel.subtypes)
            model.load_tagger(self.baseport + i)
            self.models[t] = model

    def test_types(self, corpus):
        '''
        Classify the corpus with multiple classifiers from different subtypes
        :return ResultSetNER object with the results obtained for the models
        '''
        #self.allresults = []
        results = ResultSetNER(corpus, self.basepath)
        self.basemodel.load_data(corpus, feature_extractors.keys(), subtype="all", mode="test")
        all_results = []
        multiprocessing.log_to_stderr(logging.DEBUG)
        jobs = []
        #output_p, input_p = multiprocessing.Pipe()
        tasks = [(self.models[t], t, corpus, self.basemodel, self.basepath, self.baseport + i) for i, t in enumerate(self.types)]
        #pool = multiprocessing.Pool(processes=8)
        #output = [pool.apply_async(process_type, t) for t in tasks]
        #all_results = [p.get() for p in output]
        """for t in tasks:
            #t = threading.Thread(target=process_type, args = t)
            p = multiprocessing.Process(target=process_type, args=t)
            jobs.append(p)
            p.start()
            #t.daemon = True
            #t.start()
            #q.close()"""
        all_results = []
        for t in tasks:
            r = process_type(*t)
            all_results.append(r)
        #logging.debug("getting the queue...")
        #all_results = [q.get() for t in self.types]
        #all_results = []
        logging.info("adding results...")
        for res, i in enumerate(all_results):
            #res.save("results/multiple_" + t + ".pickle")
            #logging.debug("adding these results: {}".format(self.types[i]))
            results.add_results(res)
        return results

