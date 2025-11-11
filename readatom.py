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
from typing import Iterable, Optional
from dotenv import load_dotenv


import requests
from urllib.parse import urlparse

from saxonche import PySaxonProcessor, PyXdmNode


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
            logger.debug(f"Loading atom local file {prefix_url}/{file_name}")

            xml_text: str = requests.get(f"{prefix_url}/{file_name}").text
            self.doc = AtomFeedDoc.proc.parse_xml(xml_text=xml_text)
        else:  # file_location == "LOCAL"
            if prefix_path is None:
                raise ValueError("file_prefix is required when file_location is 'WEB'")
            xml_file_name: str = f"{prefix_path}/{file_name}"
            logger.debug(f"Loading atom web file {xml_file_name}")
            self.doc = AtomFeedDoc.proc.parse_xml(xml_file_name=xml_file_name)

    # ------------------------------------------------------------------
    # Run XQuery
    # ------------------------------------------------------------------
    def run_xquery(self, query: str):
        xq = self.proc.new_xquery_processor()
        xq.set_context(xdm_item=self.doc)
        xq.set_query(query)
        return xq.run_query_to_value()


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
    def iterate(self) -> Iterable:
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
        xpath_processor = self.proc.new_xpath_processor()
        xpath_processor.declare_namespace("", NS)

        xpath_processor.set_context(xdm_item=self.doc)

        item_single = xpath_processor.evaluate_single(xpath)

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
    file_name: str = os.getenv(
        "FILE_NAME", "licitacionesPerfilesContratanteCompleto3.atom"
    )
    file_location: str = os.getenv("FILE_LOCATION", "WEB")
    prefix_url: Optional[str] = os.getenv("PREFIX_URL")
    prefix_path: Optional[str] = os.getenv("PREFIX_PATH")
    atom_doc = AtomFeedDoc(file_name, file_location, prefix_url, prefix_path)
    for i, doc in enumerate(atom_doc.iterate()):
        logger.debug(f"File {i}: {doc.file_name}")
