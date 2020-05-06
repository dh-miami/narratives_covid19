2020-05-06 Videollamada grupo español
============

SA, GDR, RDL, NH, J


Queries
------------

Tweets recuperados desde el 24 de abril 2020.

* zona de Miami y South Florida en en

* zona de Miami y South Florida en es

* otro para Mexico, Peru, Ecuador, Colombia, España, Argentina

* todo español

Una vez filtrados segun nuestros requisitos, la cantidad de tweets todavia es manejable (~9k Miami english, ~3k Miami español)

Cómo se determina la ubicación? Se toman tuits con longitud y latitud y 600 km a la redonda

~942k en español (sin filtro geográfico), ~70k España

Idioma: o inglés o español, no se recuperan tweets 'und' porque el número no es relevante y tampoco tienen mucho contenido.

lengua  | inglés | español | und
---------------------------------
enero   | 123312 | 41301   | 5310
febrero | 127466 | 43932   | 4984


Modelización de los datos
------------

En una DB, recuperables por usuario, ubicación, etc. → visualizaciones

Dump de todo el texto en un archivo para procesamiento. → NLP


Documentar todo el proceso y replicar en inglés

NH define lista de pasos para normalización
