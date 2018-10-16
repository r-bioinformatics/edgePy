"""Some macro-level functions for dealing with the mysql library"""

import argparse
from smart_open import smart_open  # type: ignore

from edgePy.data_import.ensembl.mysql_wrapper import MySQLWrapper
from typing import List

CANONICAL_TRANSCRIPT_SQL = """select gene.stable_id as gene, transcript.stable_id as transcript,
t_len.exon_len as length, IF(gene.canonical_transcript_id = transcript.transcript_id, "True", "False") as canonical
from transcript,
(select et.transcript_id, sum(exon.seq_region_end - exon.seq_region_start) as exon_len
from exon, exon_transcript as et where et.exon_id = exon.exon_id group by et.transcript_id ) as t_len, gene
where t_len.transcript_id = transcript.transcript_id and transcript.gene_id = gene.gene_id;"""

GENE_SYMBOL_SQL = """select xref.display_label as symbol, gene.stable_id as gene
from xref, gene
where xref.xref_id = gene.display_xref_id
      and xref.external_db_id = 1100;
"""


def parse_arguments(parser=None):
    if not parser:
        parser = argparse.ArgumentParser()

    parser.add_argument("--host", help="name of the mysql host", default="ensembldb.ensembl.org")
    parser.add_argument("--port", help="name of the mysql port", default=3337)
    parser.add_argument("--username", help="user name for the mysql service", default="anonymous")
    parser.add_argument("--password", help="password for the mysql service", default=None)
    parser.add_argument(
        "--database",
        help="database to use for the query, for example homo_sapiens_core_75_37 or "
        "homo_sapiens_core_93_38 or mus_musculus_core_93_38 ",
        default="homo_sapiens_core_75_37",
    )

    parser.add_argument(
        "--output_transcripts",
        help="where to put the file with the transcript data",
        default="blank",
    )
    parser.add_argument(
        "--output_symbols", help="where to put the file with the gene symbols", default="blank"
    )
    args = parser.parse_args()

    if args.output_transcripts == "blank":
        args.output_transcripts = f"../../data/transcripts_{args.database}.tsv"

    if args.output_symbols == "blank":
        args.output_symbols = f"../../data/symbols_{args.database}.tsv"

    return args


class CanonicalTranscript(object):
    def __init__(self, host, port, user, password, database):
        # needs to go into a config file, but for now:
        self.exon_store = {}

        self.mysql_wrapper = MySQLWrapper(
            host=host, port=port, username=user, password=password, database=database
        )

        print("retrieving canonical transcript data.")
        self.canonical_transcripts = self.mysql_wrapper.run_sql_query(CANONICAL_TRANSCRIPT_SQL)

        print("retrieving gene synonym data.")
        self.gene_symbols = self.mysql_wrapper.run_sql_query(GENE_SYMBOL_SQL)

        print("completed")
        self.mysql_wrapper.close()

    def get_canonical(self) -> List:
        return self.canonical_transcripts

    def get_gene_symbols(self) -> List:
        return self.gene_symbols


def main():
    args = parse_arguments()
    default_class = CanonicalTranscript(
        args.host, args.port, args.username, args.password, args.database
    )
    canonical = default_class.get_canonical()

    with smart_open(args.output_transcripts, 'w') as output:
        for transcript in canonical:
            output.write(
                f"{transcript['gene']}\t{transcript['transcript']}\t"
                f"{transcript['length']}\t{transcript['canonical']}\n"
            )

    symbols = default_class.get_gene_symbols()

    with smart_open(args.output_symbols, 'w') as output:
        for symbol in symbols:
            output.write(f"{symbol['symbol']}\t{symbol['gene']}\n")


if __name__ == "__main__":
    main()
