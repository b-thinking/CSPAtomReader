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

from lxml import etree # type: ignore

NS_ATOM = "http://www.w3.org/2005/Atom" # Main namespace Atom
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

NAMESPACE_MAP = {
    "atom": NS_ATOM, # Default namespace, implicit in tags with no namespace prefix
    "at": NS_AT,
    "ns7": NS_NS7,
    "cbc": NS_CBC,
    "cac": NS_CAC,
    "cbc-place-ext": NS_CBC_PLACE_EXT,
    "cac-place-ext": NS_CAC_PLACE_EXT
}

# saxon_processor = PySaxonProcessor(license=False)

class CspEntry:
    """
    :param entry: Atom entry containing the contract
    """

    def __init__(self, entry: etree.Element, id_plataforma: Optional[str] = None) -> None:
        self.entry: etree.Element = entry
        if id_plataforma is not None:
            self._id_plataforma = id_plataforma

    
    @property
    def id_plataforma(self) -> Optional[str]:
        if not hasattr(self, "_id_plataforma"):
            xpath: str = """
                cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/
                cac:Party/cac:PartyIdentification/
                cbc:ID[@schemeName='ID_PLATAFORMA']/
                text()
                """
            self._id_plataforma: Optional[str] = self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)[0]
        return self._id_plataforma
    
    @property
    def cpv(self) -> Optional[str]:
        if not hasattr(self, "_cpv"):
            # xpath: str = """
            #     cac-place-ext:ContractFolderStatus/
            #     cac:ProcurementProject/
            #     cac:RequiredCommodityClassification/
            #     cbc:ItemClassificationCode/
            #     text()
            #     """
            # self._cpv: Optional[str] = self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)[0]
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}ProcurementProject/{{{NS_CAC}}}RequiredCommodityClassification/{{{NS_CBC}}}ItemClassificationCode"
            self._cpv: Optional[str] = self.entry.find(find_path).text

        return self._cpv
    @property
    def title(self) -> Optional[str]:
        if not hasattr(self, "_title"):
            self._title: Optional[str] = self.entry.find(f"{{{NS_ATOM}}}title").text
            # self._title: Optional[str] = self.entry.xpath("atom:title/text()")[0]
        return self._title

    @property
    def total_amount(self) -> Optional[float]:
        if not hasattr(self, "_total_amount"):
            # xpath: str = """
            #     cac-place-ext:ContractFolderStatus/
            #     cac:ProcurementProject/
            #     cac:BudgetAmount/
            #     cbc:TotalAmount/
            #     text()
            #     """
            # self._total_amount: Optional[float] = float(self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)[0])

            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}ProcurementProject/{{{NS_CAC}}}BudgetAmount/{{{NS_CBC}}}TotalAmount"
            self._total_amount: Optional[float] = float(self.entry.find(find_path).text)
        return self._total_amount

    @property
    def technical_docs(self) -> list:
        if not hasattr(self, "_technical_docs"):
            # xpath: str = """
            #     cac-place-ext:ContractFolderStatus/
            #     cac:ProcurementProject/
            #     cac:BudgetAmount/
            #     cbc:TotalAmount/
            #     text()
            #     """
            # self._total_amount: Optional[float] = float(self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)[0])

            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}TechnicalDocumentReference"
            nodes: list = self.entry.findall(find_path)
            self._technical_docs: list[tuple[str,str,str]] = []
            for node in nodes:
                id: str = node.find(f"{{{NS_CBC}}}ID").text
                attachment_uri: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}URI").text
                attachment_hash: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}DocumentHash").text
                self._technical_docs.append((id, attachment_uri, attachment_hash))

        return self._technical_docs

class CspDoc:
    """
    Represent an Atom file containing contracts. In Spain, open data publish contracts in Atom files.
    Details in https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx

    :param file_name: Name of Atom file
    :param file_location: Location of Atom file (WEB or LOCAL)
    :param url_prefix: URL prefix (WEB only)
    :param file_prefix: File prefix (LOCAL only)
    """

    def __init__(
        self,
        file_name: str,
        file_location: str,
        prefix_url: Optional[str] = None,
        prefix_path: Optional[str] = None,
        updated_after: Optional[datetime] = None
    ):

        # self.doc: PyXdmNode
        if file_location not in ["WEB", "LOCAL"]:
            raise ValueError("file_location must be 'WEB' or 'LOCAL'")

        self.file_name = file_name
        self.file_location = file_location
        self.prefix_url = prefix_url
        self.prefix_path = prefix_path
        self.updated_after = updated_after

        self.doc: etree._ElementTree
        if file_location == "WEB":
            if prefix_url is None:
                raise ValueError("url_prefix is required when file_location is 'WEB'")
            xml_url = f"{prefix_url}/{file_name}"
            logger.debug(f"Loading atom web file {xml_url}")

            # xml_text: str = requests.get(xml_url).text
            xml_content: bytes = requests.get(xml_url).content
            self.doc = etree.ElementTree(etree.fromstring(xml_content)) # Convert Element to ElementTree (for typing consistency)
        else:  # file_location == "LOCAL"
            if prefix_path is None:
                raise ValueError("file_prefix is required when file_location is 'WEB'")
            xml_file_name: str = f"{prefix_path}/{file_name}"
            logger.debug(f"Loading atom local file {xml_file_name}")
            self.doc = etree.parse(xml_file_name)


        if updated_after is not None:
            updated_str = self.doc.xpath("/atom:feed/atom:updated/text()", namespaces=NAMESPACE_MAP)[0]
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
            xpath = f"/atom:feed/atom:entry[cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='ID_PLATAFORMA']='{id_plataforma}']"
            #  and cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:RequiredCommodityClassification/cbc:ItemClassificationCode='{cpv}'


            found: list[etree.Element] = self.doc.xpath(xpath, namespaces=NAMESPACE_MAP)
            if found is not None:
                node: etree.Element
                for node in found:
                    entry = CspEntry(node)
                    logger.debug(f"Contractor Id: {entry.id_plataforma} - CPV: {entry.cpv} - Title: {entry.title}  - Total Amount {entry.total_amount:,.2f}")

                    logger.debug(entry.technical_docs)
                    ret.append(node)

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
            except ValueError as ve:
                logger.debug(f"Next document is not valid: {ve}")
                return None
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
        xpath = "/atom:feed/atom:link[@rel='next']/@href"

        items = self.doc.xpath(xpath, namespaces=NAMESPACE_MAP)
        if items is None or len(items) == 0:
            return None

        return items[0]

    
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
    # logger.debug(f"Saxon Processor:  {saxon_processor.version}")

    file: str = os.getenv(
        "FILE", "licitacionesPerfilesContratanteCompleto3.atom"
    )
    file_location: str = os.getenv("FILE_LOCATION", "WEB")
    prefix_url: Optional[str] = os.getenv("PREFIX_URL")
    prefix_path: Optional[str] = os.getenv("PREFIX_PATH")
    contractor_ids: list[str] = os.getenv("ENTRY_CONTRACTOR_IDS","").split(",")
    doc_updated_after: datetime = datetime.fromisoformat(os.getenv("DOC_UPDATED_AFTER",""))

    try: 
        atom_doc: CspDoc = CspDoc(file, file_location, prefix_url, prefix_path, doc_updated_after)
        entries: list[CspEntry] = []
        for doc in atom_doc:
            logger.debug(f"Searching in file: {doc.file_name}")
            doc_entries: list[CspEntry] = doc.search_entry(contractor_ids)
            entries.extend(doc_entries)

        logger.debug(f"Found {len(entries)} entries")
    except ValueError as ve:
        logger.error(f"Error loading document {file}: {ve}")



