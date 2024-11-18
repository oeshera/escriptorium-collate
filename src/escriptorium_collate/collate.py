import json
import os
import subprocess
import tempfile

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

try:
    from typing import List, Literal
except ImportError:
    from typing_extensions import List, Literal

from escriptorium_connector import EscriptoriumConnector
from minineedle import core, needle
from nltk.tokenize import WhitespaceTokenizer
from pydantic import BaseModel

from escriptorium_collate.transcription_layers import get_transcription_pk_by_name


class Witness(BaseModel):
    """
    Interface for defining an eScriptorium document as
    a witness to be passed to CollateX
    """

    doc_pk: int
    siglum: str
    diplomatic_transcription_pk: int | None
    diplomatic_transcription_name: str | None
    normalized_transcription_pk: int | None
    normalized_transcription_name: str | None


class CollatexArgs(BaseModel):
    """
    Interface for passing arguments to the CollateX command line interface
    """

    algorithm: Literal["needleman-wunsch", "medite", "dekker"] = "needleman-wunsch"
    distance: int | None
    dot_path: str | None
    format: Literal["tei", "json", "dot", "graphml", "tei"] = "json"
    input: str | None
    input_encoding: str | None
    max_collation_size: int | None
    max_parallel_collations: int | None
    output_encoding: str | None
    output: str | None
    tokenized: bool = False
    token_comparator: Literal["equality", "levenshtein"] = "equality"


def get_collatex_input(
    escr: EscriptoriumConnector,
    witnesses: List[Witness],
    collatex_args: CollatexArgs,
):
    """
    Given two or more Witness instances and a set of CollateX arguments,
    return the input JSON that will be later passed to CollateX.

    Args:
        escr (EscriptoriumConnector): An EscriptoriumConnector instance
        witnesses (List[Witness]): A list of Witness instances to be collated
        collatex_args (CollatexArgs): An instance of CollatexArgs

    Returns:
        dict: CollateX input JSON
    """
    input_json = {
        "witnesses": [],
        "algorithm": collatex_args.algorithm,
        "tokenComparator": {
            "type": collatex_args.token_comparator,
            "distance": collatex_args.distance,
        },
    }

    for witness in witnesses:
        doc_pk = witness.doc_pk

        normalized_transcription_layer_pk = None
        diplomatic_transcription_layer_pk = None

        if witness.diplomatic_transcription_pk:
            normalized_transcription_layer_pk = escr.get_document_transcription(
                doc_pk=doc_pk, transcription_pk=witness.diplomatic_transcription_pk
            )
        elif witness.normalized_transcription_name:
            normalized_transcription_layer_pk = get_transcription_pk_by_name(
                escr=escr,
                doc_pk=doc_pk,
                transcription_name=witness.normalized_transcription_name,
            )

        if witness.diplomatic_transcription_pk:
            diplomatic_transcription_layer_pk = escr.get_document_transcription(
                doc_pk=doc_pk, transcription_pk=witness.diplomatic_transcription_pk
            )
        elif witness.diplomatic_transcription_name:
            diplomatic_transcription_layer_pk = get_transcription_pk_by_name(
                escr=escr,
                doc_pk=doc_pk,
                transcription_name=witness.diplomatic_transcription_name,
            )

        tokens = []
        parts = escr.get_document_parts(doc_pk=doc_pk).results
        for part in parts:
            if not normalized_transcription_layer_pk and not diplomatic_transcription_layer_pk:
                pass
            elif normalized_transcription_layer_pk == diplomatic_transcription_layer_pk:
                lines = escr.get_document_part_lines(doc_pk=doc_pk, part_pk=part.pk).results
                for line in lines:
                    normalized_line = escr.get_document_part_line_transcription_by_transcription(
                        doc_pk=doc_pk,
                        part_pk=part.pk,
                        line_pk=line.pk,
                        transcription_pk=normalized_transcription_layer_pk,
                    )
                    if normalized_line:
                        normalized_seq = WhitespaceTokenizer().tokenize(normalized_line.content)
                        for index, value in enumerate(normalized_seq):
                            token = {
                                "t": value,
                                "doc_pk": doc_pk,
                                "line_pk": normalized_line.line,
                                "normalized_transcription_pk": normalized_line.transcription,
                                "normalized_line_transcription_pk": normalized_line.pk,
                                "diplomatic_transcription_pk": normalized_line.transcription,
                                "diplomatic_line_transcription_pk": normalized_line.pk,
                            }
                            tokens.append(token)
            else:
                lines = escr.get_document_part_lines(doc_pk=doc_pk, part_pk=part.pk).results
                for line in lines:
                    normalized_line = escr.get_document_part_line_transcription_by_transcription(
                        doc_pk=doc_pk,
                        part_pk=part.pk,
                        line_pk=line.pk,
                        transcription_pk=normalized_transcription_layer_pk,
                    )
                    diplomatic_line = escr.get_document_part_line_transcription_by_transcription(
                        doc_pk=doc_pk,
                        part_pk=part.pk,
                        line_pk=line.pk,
                        transcription_pk=diplomatic_transcription_layer_pk,
                    )
                    if normalized_line and diplomatic_line:
                        normalized_seq = WhitespaceTokenizer().tokenize(normalized_line.content)
                        diplomatic_seq = WhitespaceTokenizer().tokenize(diplomatic_line.content)
                        if len(normalized_seq) != len(diplomatic_seq):
                            alignment: needle.NeedlemanWunsch[str] = needle.NeedlemanWunsch(
                                normalized_seq, diplomatic_seq
                            )
                            alignment.gap_character = ""
                            alignment.align()
                            (normalized_algn, diplomatic_algn) = alignment.get_aligned_sequences(
                                core.AlignmentFormat.list
                            )
                            normalized_seq = [str(e) for e in normalized_algn]
                            diplomatic_seq = [str(e) for e in diplomatic_algn]
                        for index, value in enumerate(normalized_seq):
                            token = {
                                "t": diplomatic_seq[index],
                                "n": value,
                                "doc_pk": doc_pk,
                                "line_pk": normalized_line.line,
                                "normalized_transcription_pk": normalized_line.transcription,
                                "normalized_line_transcription_pk": normalized_line.pk,
                                "diplomatic_transcription_pk": diplomatic_line.transcription,
                                "diplomatic_line_transcription_pk": diplomatic_line.pk,
                            }
                            tokens.append(token)
                    elif normalized_line:
                        normalized_seq = WhitespaceTokenizer().tokenize(normalized_line.content)
                        for index, value in enumerate(normalized_seq):
                            token = {
                                "t": value,
                                "doc_pk": doc_pk,
                                "line_pk": normalized_line.line,
                                "normalized_transcription_pk": normalized_line.transcription,
                                "normalized_line_transcription_pk": normalized_line.pk,
                                "diplomatic_transcription_pk": None,
                                "diplomatic_line_transcription_pk": None,
                            }
                            tokens.append(token)
                    elif diplomatic_line:
                        diplomatic_seq = WhitespaceTokenizer().tokenize(diplomatic_line.content)
                        for index, value in enumerate(diplomatic_seq):
                            token = {
                                "t": value,
                                "doc_pk": doc_pk,
                                "line_pk": diplomatic_line.line,
                                "normalized_transcription_pk": None,
                                "normalized_line_transcription_pk": None,
                                "diplomatic_transcription_pk": diplomatic_line.transcription,
                                "diplomatic_line_transcription_pk": diplomatic_line.pk,
                            }
                            tokens.append(token)

        if len(tokens) > 0:
            input_json["witnesses"].append({"id": witness.siglum, "tokens": tokens})

    return input_json


def get_collatex_output(collatex_args: CollatexArgs):
    """
    Pass a given instance of CollatexArgs to the CollateX JAR.

    Args:
        collatex_args (CollatexArgs): An instance of CollatexArgs

    Raises:
        RuntimeError: An error is raised if CollateX fails.

    Returns:
        dict: CollateX output JSON
    """

    jar_path = str(files("escriptorium_collate") / "__assets__" / "collatex-tools-1.7.1.jar")

    args = [
        "java",
        "-jar",
        jar_path,
        "-a",
        collatex_args.algorithm,
        "-f",
        collatex_args.format,
    ]

    if collatex_args.tokenized:
        args.append("-t")

    if collatex_args.dot_path:
        args.extend(["-dot", collatex_args.dot_path])

    if collatex_args.input_encoding:
        args.extend(["-ie", collatex_args.input_encoding])

    if collatex_args.output_encoding:
        args.extend(["-oe", collatex_args.output_encoding])

    if collatex_args.max_collation_size:
        args.extend(["-mcs", collatex_args.max_collation_size])

    if collatex_args.max_parallel_collations:
        args.extend(["-mpc", collatex_args.max_parallel_collations])

    args.append(collatex_args.input)

    with subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as cmd:
        out, err = cmd.communicate()

        if cmd.returncode != 0:
            error = f"CollateX failed: {cmd.returncode} {out} {err}"
            raise RuntimeError(error)

    output = json.loads(out)

    return output


def collate(
    escr: EscriptoriumConnector,
    witnesses: List[Witness],
    collatex_args: CollatexArgs,
):
    """
    Run the complete collation pipeline via one function call.

    Args:
        escr (EscriptoriumConnector): An EscriptoriumConnector instance
        witnesses (List[Witness]): A list of Witness instances
        collatex_args (CollatexArgs): An instance of CollatexArgs

    Returns:
        dict: CollateX JSON output
    """
    if not collatex_args.input or not os.path.exists(collatex_args.input):
        input_json = get_collatex_input(
            escr=escr,
            witnesses=witnesses,
            collatex_args=collatex_args,
        )

    if collatex_args.input:
        with open(collatex_args.input, "w", encoding="UTF-8") as file:
            json.dump(input_json, file, ensure_ascii=False)
        output_json = get_collatex_output(collatex_args=collatex_args)
    else:
        with tempfile.NamedTemporaryFile(mode="w") as file:
            json.dump(input_json, file, ensure_ascii=False)
            collatex_args.input = file.name
            file.flush()
            output_json = get_collatex_output(collatex_args=collatex_args)

    if collatex_args.output:
        with open(collatex_args.output, "w", encoding="UTF-8") as file:
            json.dump(output_json, file, ensure_ascii=False)

    return output_json
