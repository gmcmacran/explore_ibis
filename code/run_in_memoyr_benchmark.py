import os
import time

import ibis
import ibis.selectors as s
import numpy as np
from ibis import _
from plotnine import aes, coord_flip, geom_col, ggplot, labs, scale_y_continuous

# Load data
ibis.options.interactive = True

path = os.path.join(os.getcwd(), "data", "stock_data.parquet")
df = ibis.read_parquet(path)
df.head()

# define functions


def run_distinct_benchmark(backend):
    ibis.set_backend(backend)

    start = time.time()
    df.distinct().execute()
    end = time.time()

    return round(end - start, 3)


def run_join_benchmark(backend):
    ibis.set_backend(backend)

    start = time.time()
    temp_df = df.select("stockname").distinct()
    df.inner_join(temp_df, predicates=["stockname"]).execute()
    end = time.time()

    return round(end - start, 3)


def run_group_by_benchmark(backend):
    ibis.set_backend(backend)

    start = time.time()
    df.group_by(_.stockname).aggregate(sum_open=_.open.sum()).execute()
    end = time.time()

    return round(end - start, 3)


def run_order_by_benchmark(backend):
    ibis.set_backend(backend)

    start = time.time()
    df.order_by([ibis.desc("stockname"), ibis.desc("timestamp")]).execute()
    end = time.time()

    return round(end - start, 3)


def run_filter_benchmark(backend):
    ibis.set_backend(backend)

    start = time.time()
    df.filter(_.stockname == "PLTR").execute()
    end = time.time()

    return round(end - start, 3)


backends = ["duckdb", "polars", "datafusion"]

benchmark_df = {
    "backend": backends,
    "distinct": list(map(run_distinct_benchmark, backends)),
    "join": list(map(run_join_benchmark, backends)),
    "group_by": list(map(run_group_by_benchmark, backends)),
    "order_by": list(map(run_order_by_benchmark, backends)),
    "filter": list(map(run_filter_benchmark, backends)),
}
benchmark_df = ibis.memtable(benchmark_df, name="benchmark_df")
benchmark_df = benchmark_df.pivot_longer(
    ~s.cols("backend"), names_to="benchmark", values_to="time"
)
benchmark_df

path = os.path.join(os.getcwd(), "data", "benchmark_df.parquet")
benchmark_df.to_parquet(path)

(
    ggplot(data=benchmark_df, mapping=aes(x="benchmark", y="time", fill="backend"))
    + geom_col(position="dodge", alpha=0.30)
    + labs(x="Benchmark", y="Time (Seconds)")
    + coord_flip()
)
