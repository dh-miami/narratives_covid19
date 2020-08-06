import argparse
import os
import pandas as pd

def pos_type(string):
    value = int(string)
    if value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not positive")
    return value

# TODO think about not including use cores arg
def prepare_cmd(ncpus, fname):
    cmd = f'parallel --jobs {ncpus} '
    cmd += '"python3 stanza_chunk.py {1} {2} {3}" ' + f'::: {ncpus} '
    cmd += '::: {0..' + str(ncpus - 1) + '} ::: '
    cmd += fname
    return cmd

def lemmatize_in_parallel(ncpus, fname):
    print("calling stanza chunks...")
    os.system(prepare_cmd(ncpus, fname))
    df = pd.read_csv('tmp_0.csv')
    for i in range(1, ncpus):
        df = pd.concat([df, pd.read_csv(f'tmp_{i}.csv')])

    df = df.reset_index(drop=True)
    fname = fname.split(".")[0] + "_stanza.csv"
    os.system("rm tmp_*.csv")
    df = df.drop(columns=["Unnamed: 0"])
    df.to_csv(fname, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-file')
    parser.add_argument('-ncpus', default=8, type=pos_type)
    args = parser.parse_args()
    print("calling stanza chunks...")
    os.system(prepare_cmd(args.ncpus, args.fname))
    df = pd.read_csv('tmp_0.csv')
    for i in range(1, args.ncpus):
        df = pd.concat([df, pd.read_csv(f'tmp_{i}.csv')])

    df = df.reset_index(drop = True)
    fname = args.file.split(".")[0] + "_stanza.csv"
    os.system("rm tmp_*.csv")
    df = df.drop(columns=["Unnamed: 0"])
    df.to_csv(fname, index = False)

