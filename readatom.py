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
import csv


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

    def __init__(self, entry: etree.Element, id_plataforma: Optional[str] = None, dir3: Optional[str] = None) -> None:
        self.entry: etree.Element = entry
        if id_plataforma is not None:
            self._id_plataforma = id_plataforma
        if dir3 is not None:
            self._dir3 = dir3
    @property
    def id(self) -> Optional[str]:
        if not hasattr(self, "_id"):
            self._id: Optional[str] = self.entry.find(f"{{{NS_ATOM}}}id").text
        return self._id

    @property
    def link(self) -> Optional[str]:
        if not hasattr(self, "_link"):
            self._link: Optional[str] = self.entry.find(f"{{{NS_ATOM}}}link").get("href")
        return self._link

    @property
    def title(self) -> Optional[str]:
        if not hasattr(self, "_title"):
            self._title: Optional[str] = self.entry.find(f"{{{NS_ATOM}}}title").text
        return self._title

    @property
    def id_plataforma(self) -> Optional[str]:
        if not hasattr(self, "_id_plataforma"):
            xpath: str = """
                cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/
                cac:Party/cac:PartyIdentification/
                cbc:ID[@schemeName='ID_PLATAFORMA']/
                text()
                """
            list = self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)
            self._id_plataforma: Optional[str] = list[0] if list and len(list) > 0 else None
        return self._id_plataforma
    
    @property
    def dir3(self) -> Optional[str]:
        if not hasattr(self, "_dir3"):
            xpath: str = """
                cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/
                cac:Party/cac:PartyIdentification/
                cbc:ID[@schemeName='DIR3']/
                text()
                """
            list = self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)
            self._dir3: Optional[str] = list[0] if list and len(list) > 0 else None
        return self._dir3
    
    
    @property
    def cpv(self) -> Optional[str]:
        if not hasattr(self, "_cpv"):
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}ProcurementProject/{{{NS_CAC}}}RequiredCommodityClassification/{{{NS_CBC}}}ItemClassificationCode"
            self._cpv: Optional[str] = self.entry.find(find_path).text
        return self._cpv


    @property
    def updated(self) -> Optional[datetime]:
        if not hasattr(self, "_updated"):
            self._updated: Optional[datetime] = datetime.fromisoformat(self.entry.find(f"{{{NS_ATOM}}}updated").text)
        return self._updated

    @property
    def total_amount(self) -> Optional[float]:
        if not hasattr(self, "_total_amount"):

            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}ProcurementProject/{{{NS_CAC}}}BudgetAmount/{{{NS_CBC}}}TotalAmount"
            self._total_amount: Optional[float] = float(self.entry.find(find_path).text)
        return self._total_amount
    # Get tenders with code 8 (Awarded)
    @property
    def tender_name(self) -> Optional[str]:
        if not hasattr(self, "_tender_name"):
            xpath: str =  """
                cac-place-ext:ContractFolderStatus/
                cac:TenderResult[cbc:ResultCode='8']/
                cac:WinningParty/
                cac:PartyName/
                cbc:Name/
                text()
                """
            list = self.entry.xpath(xpath,namespaces=NAMESPACE_MAP)
            self._tender_name: Optional[str] = "|".join(list) if list and len(list) > 0 else None
        return self._tender_name
    
    @property
    def tender_accepted_count(self) -> int:
        if not hasattr(self, "_tender_accepted_count"):
            xpath: str =  """
                count(
                cac-place-ext:ContractFolderStatus/
                cac:TenderResult
                    [
                    cbc:ResultCode='8' or cbc:ResultCode='3'
                    ]
                )
                """
            count: int = int(self.entry.xpath(xpath,namespaces=NAMESPACE_MAP))
            self._tender_accepted_count: int = count
        return self._tender_accepted_count
    
    @property
    def tender_excluded_count(self) -> int:
        if not hasattr(self, "_tender_excluded_count"):
            xpath: str =  """
                count
                (
                    cac-place-ext:ContractFolderStatus/
                    cac:TenderResult
                        [
                        cbc:ResultCode='1'
                        ]
                )
                """
            count: int = int(self.entry.xpath(xpath,namespaces=NAMESPACE_MAP))
            self._tender_excluded_count: int = count
        return self._tender_excluded_count
    
    @property
    def tender_other_count(self) -> int:
        if not hasattr(self, "_tender_other_count"):
            xpath: str =  """
                count
                (
                    cac-place-ext:ContractFolderStatus/
                    cac:TenderResult
                    [
                        cbc:ResultCode!='1' and cbc:ResultCode!='3' and cbc:ResultCode!='8'
                    ]
                )
                """
            count: int = int(self.entry.xpath(xpath,namespaces=NAMESPACE_MAP))
            self._tender_other_count: int = count
        return self._tender_other_count
    @property
    def contract_folder_id(self) -> Optional[str]:
        if not hasattr(self, "_contract_folder_id"):
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CBC}}}ContractFolderID"
            self._contract_folder_id: Optional[str] = self.entry.find(find_path).text
        return self._contract_folder_id
    
    @property
    def technical_docs(self) -> list[tuple[str,str,str]]:
        if not hasattr(self, "_technical_docs"):
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}TechnicalDocumentReference"
            nodes: list = self.entry.findall(find_path)
            self._technical_docs: list[tuple[str,str,str]] = []
            for node in nodes:
                id: str = node.find(f"{{{NS_CBC}}}ID").text.strip()
                attachment_uri: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}URI").text.strip()
                attachment_hash: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}DocumentHash").text.strip()
                self._technical_docs.append((id, attachment_uri, attachment_hash))

        return self._technical_docs

    @property
    def additional_docs(self) -> list[tuple[str,str,str]]:
        if not hasattr(self, "_additional_docs"):
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC}}}AdditionalDocumentReference"
            nodes: list = self.entry.findall(find_path)
            self._additional_docs: list[tuple[str,str,str]] = []
            for node in nodes:
                id: str = node.find(f"{{{NS_CBC}}}ID").text.strip()
                attachment_uri: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}URI").text.strip()
                attachment_hash: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}DocumentHash").text.strip()
                self._additional_docs.append((id, attachment_uri, attachment_hash))

        return self._additional_docs    
    @property
    def general_docs(self) -> list[tuple[str,str,str]]:
        
        if not hasattr(self, "_general_docs"):
            find_path: str = f"{{{NS_CAC_PLACE_EXT}}}ContractFolderStatus/{{{NS_CAC_PLACE_EXT}}}GeneralDocument/{{{NS_CAC_PLACE_EXT}}}GeneralDocumentDocumentReference"
            nodes: list = self.entry.findall(find_path)
            self._general_docs: list[tuple[str,str,str]] = []
            for node in nodes:
                id: str = node.find(f"{{{NS_CBC}}}ID").text.strip()
                attachment_uri: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}URI").text.strip()
                attachment_file_name: str = node.find(f"{{{NS_CAC}}}Attachment/{{{NS_CAC}}}ExternalReference/{{{NS_CBC}}}FileName").text.strip()
                self._general_docs.append((id, attachment_uri, attachment_file_name))

        return self._general_docs

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


    def search_entry(self, id_plataforma_list: list[str], dir3_list: list[str]) -> list[CspEntry]:
        """
        Search entries for a given list of platform ids and, for every platform id, a list of CPVs

        :param id_plataforma_list: List of platform ids

        :return entries: list of found entries, with platform id, cpv, title, amount and full entry as PyXdmNode
        """
        def add_entries(found: list[etree.Element], csp_entries: list[CspEntry], id_plataforma: Optional[str] = None, dir3: Optional[str] = None):
            if found is not None:
                node: etree.Element
                for node in found:
                    entry = CspEntry(node, id_plataforma=id_plataforma, dir3=dir3)
                    logger.debug(f"Contractor Id: {entry.id_plataforma} - Contract Folder Id {entry.contract_folder_id} - CPV: {entry.cpv} - Title: {entry.title} - Updated {entry.updated.isoformat() if entry.updated is not None else 'N/A'} - Total Amount {entry.total_amount:,.2f}")
                    logger.debug(entry.technical_docs)
                    csp_entries.append(entry)

        ret: list[CspEntry] = []

        # Search entries by ID_PLATAFORMA          
        for id_plataforma in id_plataforma_list:
            xpath = f"/atom:feed/atom:entry[cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='ID_PLATAFORMA']='{id_plataforma}']"
            found: list[etree.Element] = self.doc.xpath(xpath, namespaces=NAMESPACE_MAP)
            add_entries(found, ret, id_plataforma=id_plataforma)

        # Search entries by DIR3          
        for dir3 in dir3_list:
            xpath = f"/atom:feed/atom:entry[cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='DIR3']='{dir3}']"
            found: list[etree.Element] = self.doc.xpath(xpath, namespaces=NAMESPACE_MAP)
            add_entries(found, ret, dir3=dir3)


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
    loghandler = logging.StreamHandler(sys.stderr)
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
    dir3_ids: list[str] = os.getenv("ENTRY_DIR3_IDS","").split(",")
    doc_updated_after: datetime = datetime.fromisoformat(os.getenv("DOC_UPDATED_AFTER",""))

    try: 
        atom_doc: CspDoc = CspDoc(file, file_location, prefix_url, prefix_path, doc_updated_after)
        # Entry can be duplicated in several files, due to changes. Every change publish a new entry in atom files
        entry_ids: list[str] = []
        total_entries: int = 0
        csv_writer = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["ID_PLATAFORMA","DIR3","Contract Folder Id","CPV","Title","Date","Total Amount","Id","URI","Tender Name/Document Hash/Filename", "# Tender Accepted", "# Tender Excluded", "# Tender Other"])         
        for doc in atom_doc:
            logger.debug(f"Searching in file: {doc.file_name}")
            doc_entries: list[CspEntry] = doc.search_entry(contractor_ids, dir3_ids)
            for entry in doc_entries:
                if entry.id is not None and entry.id not in entry_ids:
                    entry_ids.append(entry.id)
                    csv_writer.writerow([entry.id_plataforma,entry.dir3,entry.contract_folder_id,entry.cpv,entry.title,(entry.updated.isoformat() if entry.updated is not None else "N/A"),entry.total_amount,entry.id,entry.link,entry.tender_name, entry.tender_accepted_count, entry.tender_excluded_count, entry.tender_other_count])
                    for technical_doc in entry.technical_docs:
                        csv_writer.writerow([entry.id_plataforma,entry.dir3,entry.contract_folder_id,entry.cpv,entry.title,(entry.updated.isoformat() if entry.updated is not None else "N/A"),"TechnicalDoc:",technical_doc[0],technical_doc[1],technical_doc[2]])
                    for additional_doc in entry.additional_docs:
                        csv_writer.writerow([entry.id_plataforma,entry.dir3,entry.contract_folder_id,entry.cpv,entry.title,(entry.updated.isoformat() if entry.updated is not None else "N/A"),"AdditionalDoc:",additional_doc[0],additional_doc[1],additional_doc[2]])
                    for general_doc in entry.general_docs:
                        csv_writer.writerow([entry.id_plataforma,entry.dir3,entry.contract_folder_id,entry.cpv,entry.title,(entry.updated.isoformat() if entry.updated is not None else "N/A"),"GeneralDoc:",general_doc[0],general_doc[1],general_doc[2]])

            total_entries += len(doc_entries)

        logger.debug(f"Found {total_entries} entries")

  
    except ValueError as ve:
        logger.error(f"Error loading document {file}: {ve}")



