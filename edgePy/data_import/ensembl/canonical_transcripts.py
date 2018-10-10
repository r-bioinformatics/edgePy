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
        "--output",
        help="database to use for the query",
        default="blank"
    )
    args = parser.parse_args()
    if args.output == "blank":
        args.output = f"../../data/transcripts_{args.database}.tsv"

    return args


class CanonicalTranscript(object):
    def __init__(self, host, port, user, password, database):
        # needs to go into a config file, but for now:
        self.exon_store = {}

        self.mysql_wrapper = MySQLWrapper(
            host=host, port=port, username=user, password=password, database=database
        )

        print("retrieving data.")
        self.canonical_transcripts = self.mysql_wrapper.run_sql_query(CANONICAL_TRANSCRIPT_SQL)
        print("completed")
        self.mysql_wrapper.close()

    def get_canonical(self) -> List:
        return self.canonical_transcripts


def main():
    args = parse_arguments()
    default_class = CanonicalTranscript(
        args.host, args.port, args.username, args.password, args.database
    )
    canonical = default_class.get_canonical()

    with smart_open(args.output, 'w') as output:
        for transcript in canonical:
            output.write(
                f"{transcript['gene']}\t{transcript['transcript']}\t"
                f"{transcript['length']}\t{transcript['canonical']}\n"
            )


if __name__ == "__main__":
    main()
