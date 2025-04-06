# Exploring Ibis


Ibis is a datafame library where instructions (code) are separated from
computation (backends). For instructions, ibis has a syntax very similar
to dplyr. For backends, ibis has high performance dataframe libraries,
multiple RDBM systems, and multiple cloud environments (spark,
snowflake, big query). In general, ibis code is easy to write,
self-optimizing, and multi-threaded. Some engines support streaming flat
files to handle larger than memory data.

This repo runs two benchmarks to answer two questions:

- Is there a major difference in compute speed of the 3 local engines?
- Can I use polars GPU functionality with ibis?
