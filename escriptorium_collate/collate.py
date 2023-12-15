from minineedle import needle, core
from typing import List, Optional, Literal
from pydantic import BaseModel, parse_obj_as, FilePath
from escriptorium_connector import EscriptoriumConnector
import json, subprocess
from nltk.tokenize import WhitespaceTokenizer


class Witness(BaseModel):
    pk: int
    siglum: str
    diplomatic_transcription_pk: int | None
    diplomatic_transcription_name: str | None
    normalized_transcription_pk: int | None
    normalized_transcription_name: str | None


class Witnesses(BaseModel):
    pass


class CollatexArgs(BaseModel):
    algorithm: Literal["needleman-wunsch", "medite", "dekker"] = "needleman-wunsch"
    dot_path: FilePath | None
    format: Literal["tei", "json", "dot", "graphml", "tei"] = "json"
    input_encoding: str | None
    output_encoding: str | None
    input: FilePath = "input.json"
    output: FilePath = "output.json"
    tokenized: bool = False
    token_comparator: Literal["equality", "levenshtein"] = "equality"
    distance: int | None


def get_collatex_input(
    escr: EscriptoriumConnector,
    witnesses: List[Witness],
    collatex_args: CollatexArgs = {},
):
    witnesses = parse_obj_as(List[Witness], witnesses)
    collateX = parse_obj_as(CollatexArgs, collatex_args)

    input = {
        "witnesses": [],
        "algorithm": collateX.algorithm,
        "tokenComparator": {
            "type": collateX.token_comparator,
            "distance": collateX.distance,
        },
    }

    for witness in witnesses:
        doc_pk = witness.pk

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
                        alignment: needle.NeedlemanWunsch[str] = needle.NeedlemanWunsch(normalized_seq, diplomatic_seq)
                        alignment.gap_character = ""
                        alignment.align()
                        (normalized_algn, diplomatic_algn) = alignment.get_aligned_sequences(core.AlignmentFormat.list)
                        normalized_seq = [str(e) for e in normalized_algn]
                        diplomatic_seq = [str(e) for e in diplomatic_algn]
                    for index, value in enumerate(normalized_seq):
                        tokens.append(
                            {
                                "t": diplomatic_seq[index],
                                "n": value,
                                "doc_pk": doc_pk,
                                "line_pk": normalized_line.line,
                                "normalized_transcription_pk": normalized_line.transcription,
                                "normalized_line_transcription_pk": normalized_line.pk,
                                "diplomatic_transcription_pk": diplomatic_line.transcription,
                                "diplomatic_line_transcription_pk": diplomatic_line.pk,
                            }
                        )

        input["witnesses"].append({"id": witness.siglum, "tokens": tokens})

    # with open(collateX.input, "w") as file:
    #     json.dump(input, file, ensure_ascii=False)

    return input


def get_collatex_output(
    collatex_args: CollatexArgs = {},
):
    collateX_args = parse_obj_as(CollatexArgs, collatex_args)
    args = [
        "java",
        "-jar",
        "collatex-tools-1.7.1.jar",
        "-a",
        collateX_args.algorithm,
        "-f",
        "json",
        collateX_args.input,
        # "-t" if collateX_args.tokenized else "",
    ]

    cmd = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = cmd.communicate()
    if err:
        raise Exception(err)

    output = json.loads(out)

    # with open(collateX_args.output, "w") as file:
    #     json.dump(output, file, ensure_ascii=False)

    return output
