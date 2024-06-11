from escriptorium_connector import EscriptoriumConnector
from escriptorium_connector.dtos import (
    PostAbbreviatedTranscription,
    PostTranscription,
    PutTranscription,
)


def create(
    escr: EscriptoriumConnector,
    doc_pk: int,
    layer_name: str,
):
    transcription = escr.create_document_transcription(
        doc_pk=doc_pk,
        transcription_name=PostAbbreviatedTranscription(layer_name),
    )
    parts = escr.get_document_parts(doc_pk=doc_pk).results
    for part in parts:
        lines = escr.get_document_part_lines(
            doc_pk=doc_pk,
            part_pk=part.pk,
        ).results
        escr.bulk_create_transcriptions(
            doc_pk=doc_pk,
            part_pk=part.pk,
            transcriptions=[
                PostTranscription(
                    line=line.pk,
                    transcription=transcription.pk,
                    content="",
                )
                for line in lines
            ],
        )


def copy(
    escr: EscriptoriumConnector,
    doc_pk: int,
    source_transcription_layer_name: str,
    target_transcription_layer_name: str,
    overwrite: bool,
):
    transcriptions = escr.get_document_transcriptions(doc_pk=doc_pk)
    source_transcription_layer_pk = None
    target_transcription_layer_pk = None
    for t in transcriptions:
        if t.name == source_transcription_layer_name:
            source_transcription_layer_pk = t.pk
        elif t.name == target_transcription_layer_name:
            target_transcription_layer_pk = t.pk

    if not source_transcription_layer_pk:
        raise Exception("Source Transcription Layer Not Found")
    elif not target_transcription_layer_pk:
        raise Exception("Target Transcription Layer Not Found")

    parts = escr.get_document_parts(doc_pk=doc_pk).results
    for part in parts:
        lines = escr.get_document_part_lines(
            doc_pk=doc_pk,
            part_pk=part.pk,
        ).results
        update_transcriptions = []
        create_transcriptions = []
        for line in lines:
            source_transcription = escr.get_document_part_line_transcription_by_transcription(
                doc_pk=doc_pk,
                part_pk=part.pk,
                line_pk=line.pk,
                transcription_pk=source_transcription_layer_pk,
            )
            target_transcription = escr.get_document_part_line_transcription_by_transcription(
                doc_pk=doc_pk,
                part_pk=part.pk,
                line_pk=line.pk,
                transcription_pk=target_transcription_layer_pk,
            )
            if target_transcription:
                if target_transcription.content and not overwrite:
                    pass
                else:
                    update_transcriptions.append(
                        PutTranscription(
                            line=line.pk,
                            pk=target_transcription.pk,
                            transcription=target_transcription_layer_pk,
                            content=source_transcription.content if source_transcription else "",
                        )
                    )
            else:
                create_transcriptions.append(
                    PostTranscription(
                        line=line.pk,
                        transcription=target_transcription_layer_pk,
                        content=source_transcription.content if source_transcription else "",
                    )
                )
        escr.bulk_update_transcriptions(
            doc_pk=doc_pk,
            part_pk=part.pk,
            transcriptions=update_transcriptions,
        )
        escr.bulk_create_transcriptions(
            doc_pk=doc_pk,
            part_pk=part.pk,
            transcriptions=create_transcriptions,
        )


def get_transcription_pk_by_name(
    escr: EscriptoriumConnector,
    doc_pk: int,
    transcription_name: str,
):
    transcriptions = escr.get_document_transcriptions(doc_pk=doc_pk)
    for t in transcriptions:
        if t.name == transcription_name:
            return t.pk
    raise ValueError("No transcription layer matches provided name")
