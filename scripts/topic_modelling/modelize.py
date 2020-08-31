#!/usr/bin/env python
"""
Usage:
    modelize.py --csv-path=PATH [--sample-n=INT --overwrite]
"""
from docopt import docopt
from topic_modelling import modelize

def main(csv_path, sample_n, overwrite):
    modelize(csv_path, sample_n, overwrite)

if __name__ == "__main__":
    args = docopt(__doc__)
    n_arg = args["--sample-n"]
    n = int(n_arg) if n_arg else None
    main(
        csv_path=args["--csv-path"],
        sample_n=n,
        overwrite=args["--overwrite"]
    )
