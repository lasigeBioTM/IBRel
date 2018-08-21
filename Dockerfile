FROM ubuntu:latest
MAINTAINER Andre Lamurias <alamurias@lasige.di.fc.ul.pt>
WORKDIR /
COPY bin/ bin/
# RUN apt-get install -y python2.7

# Install Java.
RUN \
  echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
  apt-get update && apt-get install software-properties-common -y && \
  add-apt-repository -y ppa:webupd8team/java && \
  apt-get update && \
  apt-get install -y oracle-java8-installer && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /var/cache/oracle-jdk8-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

RUN apt-get update && apt-get install unzip && apt-get install net-tools
WORKDIR /bin

# Get Stanford NER 3.5.2
RUN wget http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip && unzip stanford-ner-2015-04-20.zip
WORKDIR stanford-ner-2015-04-20

# Get Stanford CORENLP
WORKDIR /bin
RUN wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip && unzip stanford-corenlp-full-2015-12-09.zip
WORKDIR stanford-corenlp-full-2015-12-09
 



# Install Genia Sentence Splitter (requires ruby and make)
WORKDIR /bin
RUN apt-get update &&  apt-get install -y ruby
RUN wget http://www.nactem.ac.uk/y-matsu/geniass/geniass-1.00.tar.gz && \
    tar -xvzf geniass-1.00.tar.gz && \
    rm geniass-1.00.tar.gz
WORKDIR /bin/geniass
RUN apt-get update -y && apt-get install -y build-essential g++ make && make

WORKDIR bin/
RUN wget https://files.pythonhosted.org/packages/db/ee/087a1b7c381041403105e87d13d729d160fa7d6010a8851ba051b00f7c67/jsre-1.1.0.zip && unzip jsre-1.1.0.zip
WORKDIR jsre

# Download sample data
RUN mkdir /corpora
RUN mkdir /corpora/CHEMDNER-patents
WORKDIR /corpora/CHEMDNER-patents

RUN wget http://www.biocreative.org/media/store/files/2015/chemdner_patents_sample_v02.tar.zip && \
    unzip chemdner_patents_sample_v02.tar.zip && \
    tar -xvf chemdner_patents_sample_v02.tar && \
    mkdir chemdner_cemp_sample_v02 && \
    mv chemdner_patents_sample_v02/chemdner_cemp_sample/* chemdner_cemp_sample_v02/
    
 

# For Stanford CoreNLP
EXPOSE 9000
WORKDIR /bin/stanford-corenlp-full-2015-12-09
ENV CLASSPATH="`find . -name '*.jar'`"
RUN nohup java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 &


# Install python libraries
WORKDIR /
RUN apt-get update -y && apt-get -y install git liblapack-dev liblapack3 libopenblas-base libopenblas-dev
COPY requirements.txt /
RUN apt-get update -y && apt-get install -y python-pip libmysqlclient-dev python-mysqldb && pip install -r requirements.txt

# Copy repository dirs
WORKDIR /
COPY src/ src/
COPY benchmarks/ benchmarks/
RUN chmod u+x benchmarks/check_setup.sh
RUN pip install -e git+https://github.com/garydoranjr/misvm.git#egg=misvm
#RUN pip install word2vec

# Initial configuration
COPY settings_base.json /
RUN python src/config/config.py default
RUN pip install --upgrade beautifulsoup4
RUN pip install --upgrade html5lib
RUN pip install python-Levenshtein 
ENV RUBYOPT="-KU -E utf-8:utf-8"
RUN mkdir models
# Define default command.
ENTRYPOINT bash
