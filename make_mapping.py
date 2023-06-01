# CLI for generating orthographic replacement mappings for Bokmål and Nynorsk from Norsk ordbank
# Author: Per Erik Solberg
# License: Apache 2.0

import pandas as pd
import re
import json


def get_mappings(gb):
    """Get mappings between alternate forms from a groupby"""
    words = list(gb.OPPSLAG)
    firstw = words[0]
    return [(x, firstw) for x in words[1:] if x != firstw]


if __name__ == "__main__":
    language = input(
        "Please write which language you want to make mappings for, bm (default) or nn:"
    )
    if language != "nn":
        language = "bm"

    if language == "bm":
        ordbank_df = pd.read_table("fullformsliste.txt")
        # remove mask/fem distinction in Bokmål to handle gender variatiation
        ordbank_df["TAG"] = ordbank_df.TAG.apply(
            lambda x: x.replace("subst fem appell", "subst mask appell")
        )
    else:
        ordbank_df = pd.read_table("fullformsliste_nn.txt")

    # clean the df
    ordbank_df = ordbank_df.dropna(subset=["TAG", "OPPSLAG"]).query(
        "~TAG.str.contains(r'fork|symb') & ~OPPSLAG.str.contains(r'[\.\s]') & ~OPPSLAG.str.contains(r'^\-.*')"
    )

    # find duplicated forms and make list of mappings
    ordbank_df["duplicated"] = ordbank_df.duplicated(
        subset=["LEMMA_ID", "TAG"], keep=False
    )
    dups = (
        ordbank_df.query("duplicated")
        .dropna()
        .groupby(["LEMMA_ID", "TAG"])
        .apply(lambda x: get_mappings(x))
        .to_list()
    )
    dups = [y for x in dups for y in x if x != []]

    # clean mappings and make mapping dict
    mappings = {}
    for t in dups:
        if t[0] not in mappings.keys():
            if (
                t[1] in mappings.keys() and mappings[t[1]] == t[0]
            ):  # Avoid circular mappings
                pass
            else:
                mappings[t[0]] = t[1]
        else:
            pass

    # write mappings to file
    if language == "bm":
        print("Writing Bokmål mapping")
        with open("bokmal.json", "w") as outf:
            json.dump(mappings, outf, ensure_ascii=False)
    else:
        print("Writing Nynorsk mapping")
        with open("nynorsk.json", "w") as outf:
            json.dump(mappings, outf, ensure_ascii=False)
