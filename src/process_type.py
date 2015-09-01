from results import ResultsNER
import logging
__author__ = 'Andre'


def process_type(modelst, t, corpus, basemodel, basepath, port):
    #def process_type(args):
    #q, modelst, t, corpus, basemodel, basepath = args
    #l.acquire()
    # load data into the model format
    # load data only for one model since this takes at least 5 minutes each time
    logging.debug("{}: copying data...".format(t))
    modelst.copy_data(basemodel)
    # run the classifier on the data
    #logging.debug("pre test %s" % model)
    logging.debug("{}: testing...".format(t))
    res = modelst.test(corpus, port)
    #logging.debug("%post test s" % model)
    #logging.info("{}:copying corpus...".format(t))
    #this_corpus = self.corpus # deepcopy
    #logging.info("{}: processing results...".format(t))
    #res = ResultsNER(basepath + "_" + t)
    #res.get_ner_results(corpus, modelst)
    logging.info("{}:done...".format(t))
    #l.release()
    #q.put(res)
    #print "{}:closing queue...".format(t)
    #q.close()
    #print "{}:closed...".format(t)
    return res