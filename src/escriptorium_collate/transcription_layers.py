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
    """
    Create an arbitrarily named transcription layer
    for a given eScriptorium document.

    Args:
        escr (EscriptoriumConnector): An EscriptoriumConnector instance
        doc_pk (int): Primary key of an eScriptorium document
        layer_name (str): Name of the transcription layer to be created
    """
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
    """
    Copy the content of one transcription layer
    to another for a given eScriptorium document.

    Args:
        escr (EscriptoriumConnector):
            An EscriptoriumConnector instance
        doc_pk (int):
            Primary key of an eScriptorium document
        source_transcription_layer_name (str):
            Name of the transcription layer to be copied
        target_transcription_layer_name (str):
            Name of the transcription layer to be written
        overwrite (bool):
            If true, content of the target transcription layer is overwritten
    """

    source_transcription_layer_pk = get_transcription_pk_by_name(
        escr=escr,
        doc_pk=doc_pk,
        transcription_name=source_transcription_layer_name,
    )

    target_transcription_layer_pk = get_transcription_pk_by_name(
        escr=escr,
        doc_pk=doc_pk,
        transcription_name=target_transcription_layer_name,
    )

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
    """
    Given the name of a transcription layer within a given document,
    return the transcription layer's primary key.

    Args:
        escr (EscriptoriumConnector): An EscriptoriumConnector instance
        doc_pk (int): Primary key of an eScriptorium document
        transcription_name (str): Name of the desired transcription layer

    Raises:
        ValueError: If no transcription layer is found with the given name
            is found in the given document, a value error is raised

    Returns:
        int: Primary key of the transcription layer
    """
    transcriptions = escr.get_document_transcriptions(doc_pk=doc_pk)
    for t in transcriptions:
        if t.name == transcription_name:
            return t.pk
    raise ValueError("No transcription layer matches provided name")
