import os
import time

import ibis
import ibis.selectors as s
import numpy as np
from ibis import _
from plotnine import aes, coord_flip, geom_col, ggplot, labs, scale_y_continuous

# Load data
ibis.set_backend("polars")
ibis.options.interactive = True


# define functions
def load_data():
    path = os.path.join(os.getcwd(), "data", "stock_data.parquet")
    df = ibis.read_parquet(path)
    return df


def run_distinct_benchmark(engine):

    start = time.time()
    df = load_data()
    df.distinct().execute(engine=engine)
    end = time.time()

    return round(end - start, 3)


def run_join_benchmark(engine):

    start = time.time()
    df = load_data()
    temp_df = df.select("stockname").distinct()
    df.inner_join(temp_df, predicates=["stockname"]).execute(engine=engine)
    end = time.time()

    return round(end - start, 3)


def run_group_by_benchmark(engine):

    start = time.time()
    df = load_data()
    df.group_by(_.stockname).aggregate(sum_open=_.open.sum()).execute(engine=engine)
    end = time.time()

    return round(end - start, 3)


def run_order_by_benchmark(engine):

    start = time.time()
    df = load_data()
    df.order_by([ibis.desc("stockname"), ibis.desc("timestamp")]).execute(engine=engine)
    end = time.time()

    return round(end - start, 3)


def run_filter_benchmark(engine):

    start = time.time()
    df = load_data()
    df.filter(_.stockname == "PLTR").execute(engine=engine)
    end = time.time()

    return round(end - start, 3)


# "streaming" engine not supported when GPU installed
engines = ["cpu", "gpu"]

benchmark_df = {
    "backend": engines,
    "distinct": list(map(run_distinct_benchmark, engines)),
    "join": list(map(run_join_benchmark, engines)),
    "group_by": list(map(run_group_by_benchmark, engines)),
    "order_by": list(map(run_order_by_benchmark, engines)),
    "filter": list(map(run_filter_benchmark, engines)),
}
benchmark_df = ibis.memtable(benchmark_df, name="benchmark_df")
benchmark_df = benchmark_df.pivot_longer(
    ~s.cols("backend"), names_to="benchmark", values_to="time"
)
benchmark_df

path = os.path.join(os.getcwd(), "data", "polars_benchmark_df.parquet")
benchmark_df.to_parquet(path)

(
    ggplot(data=benchmark_df, mapping=aes(x="benchmark", y="time", fill="backend"))
    + geom_col(position="dodge", alpha=0.30)
    + labs(x="Benchmark", y="Time (Seconds)")
    + coord_flip()
)
