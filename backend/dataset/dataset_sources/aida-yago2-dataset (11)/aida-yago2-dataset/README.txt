CoNLL-2003 with YAGO2 annotations
---------------------------------

This tool creates YAGO2 [1], Freebase [2], and Wikipedia [3] entity annotations of the CoNLL 2003 dataset, used in [4].
The annotations were created using YAGO2 based on a Wikipedia dump from 2010-08-17.

Creating the Dataset
--------------------

Requirements:
 - Java 1.6
 - AIDA-YAGO2-annotations.tsv (included in this zip file)
 - The CoNLL 2003 [5] dataset, specifically three files: eng.testa, eng.testb, eng.train
    
To create these files, you need the Reuters Corpus RCV1, instructions are given here: http://www.cnts.ua.ac.be/conll2003/ner/000README or in the included README_CoNLL_2003.txt

Once you have the CoNLL dataset, execute the included jar like this:

java -jar aida-yago2-dataset.jar

It will ask you for paths to the CoNLL data you created above as well as our annotation file.

The final dataset will be written to the folder that contains the AIDA-YAGO2-annotations.tsv


Dataset Partition
-----------------

The original CoNLL 2003 data is split into 3 parts: TRAIN, TESTA, TESTB. We keep the ordering among the documents as in the original CoNLL data,
where the parts contain the following docids:

TRAIN: '1 EU' to '946 SOCCER'
TESTA: '947testa CRICKET' to '1162testa Dhaka'
TESTB: '1163testb SOCCER' to '1393testb SOCCER'

Notice the testa and testb suffixes directly after the digits.

In [4] we train our weighting parameters on TRAIN, our hyper-parameters are
estimated on TESTA, and the experimental results are given for TESTB.


File Format
-----------

The format of the final file is the following:

- Each document starts with a line: -DOCSTART- (<docid>)
- Each following line represents a single token, sentences are separated by an empty line
  
Lines with tabs are tokens the are part of a mention:
- column 1 is the token
- column 2 is either B (beginning of a mention) or I (continuation of a mention)
- column 3 is the full mention used to find entity candidates
- column 4 is the corresponding YAGO2 entity (in YAGO encoding, i.e. unicode characters are backslash encoded and spaces are replaced by underscores, see also the tools on the YAGO2 website), OR --NME--, denoting that there is no matching entity in YAGO2 for this particular mention, or that we are missing the connection between the mention string and the YAGO2 entity.
- column 5 is the corresponding Wikipedia URL of the entity (added for convenience when evaluating against a Wikipedia based method)
- column 6 is the corresponding Wikipedia ID of the entity (added for convenience when evaluating against a Wikipedia based method - the ID refers to the dump used for annotation, 2010-08-17)
- column 7 is the corresponding Freebase mid, if there is one (thanks to Massimiliano Ciaramita from Google Zürich for creating the mapping and making it available to us)


License
-------

The AIDA-YAGO2 dataset is licensed under the Creative Commons Attribution 3.0 License (http://creativecommons.org/licenses/by/3.0/)


References
----------

[1] J. Hoffart, F. M. Suchanek, K. Berberich, E. Lewis-Kelham, G. de Melo, and G. Weikum. YAGO2: Exploring and Querying World Knowledge in Space, Context, and Many Languages. In Proceedings of the 20th international conference companion on World Wide Web, WWW 2011, Hyderabad, India, 2011
[2] http://wiki.freebase.com/wiki/Machine_ID
[3] http://www.wikipedia.org
[4] Johannes Hoffart, Mohamed Amir Yosef, Ilaria Bordino, Hagen Fürstenau, Manfred Pinkal, Marc Spaniol, Bilyana Taneva, Stefan Thater, and Gerhard Weikum, Robust Disambiguation of Named Entities in Text, Proceedings of the Conference on Empirical Methods in Natural Language Processing, EMNLP 2011, Edinburgh, Scotland, 2011
[5] Erik F. Tjong Kim Sang, Fien De Meulder: Introduction to the CoNLL-2003 Shared Task: Language-Independent Named Entity Recognition. CoNLL 2003