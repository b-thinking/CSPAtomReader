"""
name: readatom.py
description: Read file from 'Plataforma de Contratación del Sector Público'
    and select items by contractor ID and CPV (Common Procurement Value)
author: Jose M Albarrán (b-Thinking software)
date: 2025-11-11
"""
from __future__ import annotations
from typing import Iterator, Optional

import os
import sys
import logging

from datetime import datetime
from dotenv import load_dotenv


import requests
from urllib.parse import urlparse

# Doc: https://www.saxonica.com/saxon-c/documentation12/index.html#!api/saxon_c_python_api
from saxonche import PySaxonProcessor, PyXdmNode, PyXdmValue


NS = "http://www.w3.org/2005/Atom" # Main namespace Atom
NS_AT = "http://purl.org/atompub/tombstones/1.0" # Namespace Atom Tombstones 1.0. IETF (RFC 6721)


# Namespaces UBL
# NS_UBL_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
# NS_UBL_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
NS_NS7 = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"


# Namespaces CODICE Spanish extension
NS_CBC = "urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
NS_CAC = "urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2"
NS_CBC_PLACE_EXT = "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2"
NS_CAC_PLACE_EXT = "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2"


saxon_processor = PySaxonProcessor(license=False)

class CspEntry:
    """
    :param entry: Atom entry containing the contract
    """
    entry_xpath_processor = saxon_processor.new_xpath_processor()
    entry_xpath_processor.declare_namespace("", NS)
    entry_xpath_processor.declare_namespace("at", NS_AT)
    entry_xpath_processor.declare_namespace("ns7", NS_NS7)
    entry_xpath_processor.declare_namespace("cbc", NS_CBC)
    entry_xpath_processor.declare_namespace("cac", NS_CAC)
    entry_xpath_processor.declare_namespace("cbc-place-ext", NS_CBC_PLACE_EXT)
    entry_xpath_processor.declare_namespace("cac-place-ext", NS_CAC_PLACE_EXT)
    
    def __init__(self, entry: PyXdmNode, id_plataforma: Optional[str] = None):
        self.entry = entry
        if id_plataforma is not None:
            self._id_plataforma = id_plataforma

    @property
    def id_plataforma(self) -> Optional[str]:
        if not hasattr(self, "_id_plataforma"):
            CspEntry.entry_xpath_processor.set_context(xdm_item=self.entry)
            self._id_plataforma: Optional[str] = CspEntry.entry_xpath_processor.evaluate_single("cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='ID_PLATAFORMA']").string_value
        return self._id_plataforma
    
    @property
    def cpv(self) -> Optional[str]:
        if not hasattr(self, "_cpv"):
            CspEntry.entry_xpath_processor.set_context(xdm_item=self.entry)
            self._cpv: Optional[str] = CspEntry.entry_xpath_processor.evaluate_single("cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:RequiredCommodityClassification/cbc:ItemClassificationCode").string_value
        return self._cpv
    
    # title: str = CspDoc.xpath_processor.evaluate_single("title").string_value
    # totalAmount = CspDoc.xpath_processor.evaluate_single("cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:BudgetAmount/cbc:TotalAmount").typed_value.head.double_value
    @property
    def title(self) -> Optional[str]:
        if not hasattr(self, "_cpv"):
            CspEntry.entry_xpath_processor.set_context(xdm_item=self.entry)
            self._title: Optional[str] = CspEntry.entry_xpath_processor.evaluate_single("title").string_value
        return self._title

    @property
    def total_amount(self) -> Optional[str]:
        if not hasattr(self, "_total_amount"):
            CspEntry.entry_xpath_processor.set_context(xdm_item=self.entry)
            self._total_amount: Optional[str] = CspEntry.entry_xpath_processor.evaluate_single("cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:BudgetAmount/cbc:TotalAmount").typed_value.head.double_value
        return self._total_amount


class CspDoc:
    """
    Represent an Atom file containing contracts. In Spain, open data publish contracts in Atom files.
    Details in https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx

    :param file_name: Name of Atom file
    :param file_location: Location of Atom file (WEB or LOCAL)
    :param url_prefix: URL prefix (WEB only)
    :param file_prefix: File prefix (LOCAL only)
    """

    doc_xpath_processor = saxon_processor.new_xpath_processor()
    doc_xpath_processor.declare_namespace("", NS)
    doc_xpath_processor.declare_namespace("at", NS_AT)
    doc_xpath_processor.declare_namespace("ns7", NS_NS7)
    doc_xpath_processor.declare_namespace("cbc", NS_CBC)
    doc_xpath_processor.declare_namespace("cac", NS_CAC)
    doc_xpath_processor.declare_namespace("cbc-place-ext", NS_CBC_PLACE_EXT)
    doc_xpath_processor.declare_namespace("cac-place-ext", NS_CAC_PLACE_EXT)

    def __init__(
        self,
        file_name: str,
        file_location: str,
        prefix_url: Optional[str] = None,
        prefix_path: Optional[str] = None,
        updated_after: Optional[datetime] = None
    ):

        self.doc: PyXdmNode
        if file_location not in ["WEB", "LOCAL"]:
            raise ValueError("file_location must be 'WEB' or 'LOCAL'")

        self.file_name = file_name
        self.file_location = file_location
        self.prefix_url = prefix_url
        self.prefix_path = prefix_path
        self.updated_after = updated_after

        if file_location == "WEB":
            if prefix_url is None:
                raise ValueError("url_prefix is required when file_location is 'WEB'")
            logger.debug(f"Loading atom web file {prefix_url}/{file_name}")

            xml_text: str = requests.get(f"{prefix_url}/{file_name}").text
            self.doc = saxon_processor.parse_xml(xml_text=xml_text)
        else:  # file_location == "LOCAL"
            if prefix_path is None:
                raise ValueError("file_prefix is required when file_location is 'WEB'")
            xml_file_name: str = f"{prefix_path}/{file_name}"
            logger.debug(f"Loading atom local file {xml_file_name}")
            self.doc = saxon_processor.parse_xml(xml_file_name=xml_file_name)

        CspDoc.doc_xpath_processor.set_context(xdm_item=self.doc)

        if updated_after is not None:
            updated_str = CspDoc.doc_xpath_processor.evaluate_single("feed/updated").string_value
            if updated_str is not None:
                updated = datetime.fromisoformat(updated_str)
                if updated < updated_after:
                    raise ValueError(f"File is older than {updated_after}")


    def search_entry(self, id_plataforma_list: list[str]) -> list[CspEntry]:
        """
        Search entries for a given list of platform ids and, for every platform id, a list of CPVs

        :param id_plataforma_list: List of platform ids

        :return entries: list of found entries, with platform id, cpv, title, amount and full entry as PyXdmNode
        """
        ret: list[CspEntry] = []
        for id_plataforma in id_plataforma_list:                
            xpath = f"/feed/entry[cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='ID_PLATAFORMA']='{id_plataforma}']"
            #  and cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:RequiredCommodityClassification/cbc:ItemClassificationCode='{cpv}'
            CspDoc.doc_xpath_processor.set_context(xdm_item=self.doc)

            found: PyXdmValue = CspDoc.doc_xpath_processor.evaluate(xpath)
            if found is not None:
                node: PyXdmNode
                for node in found:
                    entry = CspEntry(node)
                    logger.debug(f"Contractor Id: {entry.id_plataforma} Title: {entry.title} Total Amount {entry.total_amount:,.2f} - CPV: {entry.cpv}")

                    # logger.debug(f"Contractor Id: {id_plataforma} - CPV: {cpv} - Title: {title} - Total Amount {totalAmount:,.2f}")

                    ret.append(entry)

        return ret

    def next_doc(self) -> Optional[CspDoc]:
        next_base_name = self._get_next_basename()
        if next_base_name:
            try:
                next_doc = CspDoc(
                    file_name=next_base_name,
                    file_location=self.file_location,
                    prefix_url=self.prefix_url,
                    prefix_path=self.prefix_path,
                    updated_after=self.updated_after
                )
                return next_doc
            except Exception as e:
                logger.error(f"Error loading next document: {e}")
                return None

        return None
    
    # ------------------------------------------------------------------
    # Get all documents
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[CspDoc]:
        doc = self
        while doc is not None:
            yield doc
            doc = doc.next_doc()



    def _get_next_basename(self) -> Optional[str]:
        next_link = self._get_next_link()
        if next_link:
            parsed_link = urlparse(next_link)

            # Si scheme (http, https, ftp…), is an URL
            if parsed_link.scheme in ("http", "https", "ftp"):
                return str(os.path.basename(parsed_link.path))

            # En otro caso, tratamos como ruta local
            return os.path.basename(next_link)

        return None

    # ------------------------------------------------------------------
    # Get link rel="next"
    # ------------------------------------------------------------------
    def _get_next_link(self) -> Optional[str]:
        xpath = "/feed/link[@rel='next']/@href"


        CspDoc.doc_xpath_processor.set_context(xdm_item=self.doc)

        item_single = CspDoc.doc_xpath_processor.evaluate_single(xpath)

        return item_single.string_value if item_single is not None else None
    
    def __str__(self):
        return self.doc.__str__()


# region: Set logging
logger = logging.getLogger()
if not logger.handlers:
    loghandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)
# endregion: Set logging

if __name__ == "__main__":

    env_loaded = load_dotenv()

    logger.setLevel(os.getenv("LOGLEVEL", "DEBUG"))
    logger.debug(f"Saxon Processor:  {saxon_processor.version}")

    file: str = os.getenv(
        "FILE", "licitacionesPerfilesContratanteCompleto3.atom"
    )
    file_location: str = os.getenv("FILE_LOCATION", "WEB")
    prefix_url: Optional[str] = os.getenv("PREFIX_URL")
    prefix_path: Optional[str] = os.getenv("PREFIX_PATH")
    contractor_ids: list[str] = os.getenv("ENTRY_CONTRACTOR_IDS","").split(",")
    doc_updated_after: datetime = datetime.fromisoformat(os.getenv("DOC_UPDATED_AFTER",""))

    atom_doc = CspDoc(file, file_location, prefix_url, prefix_path, doc_updated_after)
    entries: list[CspEntry] = []
    for doc in atom_doc:
        logger.debug(f"Searching in file: {doc.file_name}")
        doc_entries: list[CspEntry] = doc.search_entry(contractor_ids)
        entries.extend(doc_entries)

    logger.debug(f"Found {len(entries)} entries")



