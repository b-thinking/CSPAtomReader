"""
name: readatom.py
description: Read file from 'Plataforma de Contratación del Sector Público'
    and select items by contractor ID and CPV (Common Procurement Value)
author: Jose M Albarrán (b-Thinking software)
date: 2025-11-11
"""

import os
import logging
import sys
from typing import Iterable, Iterator, Optional
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



class AtomFeedDoc:
    """
    :param file_name: Name of Atom file
    :param file_location: Location of Atom file (WEB or LOCAL)
    :param url_prefix: URL prefix (WEB only)
    :param file_prefix: File prefix (LOCAL only)
    """
    proc = PySaxonProcessor(license=False)
    xpath_processor = proc.new_xpath_processor()
    xpath_processor.declare_namespace("", NS)
    xpath_processor.declare_namespace("at", NS_AT)
    xpath_processor.declare_namespace("ns7", NS_NS7)
    xpath_processor.declare_namespace("cbc", NS_CBC)
    xpath_processor.declare_namespace("cac", NS_CAC)
    xpath_processor.declare_namespace("cbc-place-ext", NS_CBC_PLACE_EXT)
    xpath_processor.declare_namespace("cac-place-ext", NS_CAC_PLACE_EXT)

    def __init__(
        self,
        file_name: str,
        file_location: str,
        prefix_url: Optional[str] = None,
        prefix_path: Optional[str] = None,
    ):

        logger.debug(f"Saxon Processor:  {self.proc.version}")
        self.doc: PyXdmNode
        if file_location not in ["WEB", "LOCAL"]:
            raise ValueError("file_location must be 'WEB' or 'LOCAL'")

        self.file_name = file_name
        self.file_location = file_location
        self.prefix_url = prefix_url
        self.prefix_path = prefix_path

        if file_location == "WEB":
            if prefix_url is None:
                raise ValueError("url_prefix is required when file_location is 'WEB'")
            logger.debug(f"Loading atom web file {prefix_url}/{file_name}")

            xml_text: str = requests.get(f"{prefix_url}/{file_name}").text
            self.doc = AtomFeedDoc.proc.parse_xml(xml_text=xml_text)
        else:  # file_location == "LOCAL"
            if prefix_path is None:
                raise ValueError("file_prefix is required when file_location is 'WEB'")
            xml_file_name: str = f"{prefix_path}/{file_name}"
            logger.debug(f"Loading atom local file {xml_file_name}")
            self.doc = AtomFeedDoc.proc.parse_xml(xml_file_name=xml_file_name)

    # ------------------------------------------------------------------
    # Run XQuery
    # ------------------------------------------------------------------
    # def run_xquery(self, query: str):
    #     xq = self.proc.new_xquery_processor()
    #     xq.set_context(xdm_item=self.doc)
    #     xq.set_query(query)
    #     return xq.run_query_to_value()


    def search_entry(self, id_plataforma_list: list[str], cpvs: list[str]) -> list[tuple[str, str, str, float, PyXdmNode]]:
        """
        Search entries for a given list of platform ids and, for every platform id, a list of CPVs

        :param id_plataforma_list: List of platform ids
        :param cpvs: List of CPVs

        :return entries: list of found entries, with platform id, cpv, title, amount and full entry as PyXdmNode
        """
        ret: list[tuple[str, str, str, float, PyXdmNode]] = []
        for id_plataforma in id_plataforma_list:
            for cpv in cpvs:
                xpath = f"/feed/entry[cac-place-ext:ContractFolderStatus/cac-place-ext:LocatedContractingParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='ID_PLATAFORMA']='{id_plataforma}' and cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:RequiredCommodityClassification/cbc:ItemClassificationCode='{cpv}']"
                AtomFeedDoc.xpath_processor.set_context(xdm_item=self.doc)
                found: PyXdmValue = AtomFeedDoc.xpath_processor.evaluate(xpath)
                if found is not None:
                    # for i in range(found.size):
                    #     record: tuple[str, str, str, float, PyXdmNode] = (
                    #         id_plataforma,
                    #         cpv,
                    #         found[i].get_child("title").string_value,
                    #         float(found[i].get_child("cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:TotalContractAmount/cbc:Amount").string_value),
                    #         found[i],
                            
                    #     )
                    #     ret.append(record)
                    node: PyXdmNode
                    for node in found:
                        AtomFeedDoc.xpath_processor.set_context(xdm_item=node)
                        title: str = AtomFeedDoc.xpath_processor.evaluate_single("title").string_value
                        totalAmount = AtomFeedDoc.xpath_processor.evaluate_single("cac-place-ext:ContractFolderStatus/cac:ProcurementProject/cac:BudgetAmount/cbc:TotalAmount").typed_value.head.double_value

                        logger.debug(f"Contractor Id: {id_plataforma} - CPV: {cpv} - Title: {title} - Total Amount {totalAmount:,.2f}")
                        record: tuple[str, str, str, float, PyXdmNode] = (
                            id_plataforma,
                            cpv,
                            title,
                            totalAmount,
                            node,
                        )
                        ret.append(record)

        return ret



    def next_doc(self) -> Optional[AtomFeedDoc]:
        next_base_name = self._get_next_basename()
        if next_base_name:
            return AtomFeedDoc(
                file_name=next_base_name,
                file_location=self.file_location,
                prefix_url=self.prefix_url,
                prefix_path=self.prefix_path,
            )

        return None
    
    # ------------------------------------------------------------------
    # Get all documents
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[AtomFeedDoc]:
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


        AtomFeedDoc.xpath_processor.set_context(xdm_item=self.doc)

        item_single = AtomFeedDoc.xpath_processor.evaluate_single(xpath)

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
    file: str = os.getenv(
        "FILE", "licitacionesPerfilesContratanteCompleto3.atom"
    )
    file_location: str = os.getenv("FILE_LOCATION", "WEB")
    prefix_url: Optional[str] = os.getenv("PREFIX_URL")
    prefix_path: Optional[str] = os.getenv("PREFIX_PATH")
    atom_doc = AtomFeedDoc(file, file_location, prefix_url, prefix_path)
    for doc in atom_doc:
        logger.debug(f"Searching in file: {doc.file_name}")
        entries: list[tuple[str, str, str, float, PyXdmNode]] = doc.search_entry(['50179410029721'], ['33184100','85120000'])
