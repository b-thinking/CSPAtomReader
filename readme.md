# Links
## Plataforma de Contratación del Sector Público

- [Datos Abiertos](https://contrataciondelestado.es/wps/portal/plataforma/datos_abiertos/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziTVz9nZ3dPIwMLIKNXQyMfFxCQ808gFx3U_1wsAJTY2eTMK-wALNgT3cDA08PNxefUENTA3cjM_0oYvQb4ACOBsTpx6MgCr_x4fpR-K0wgirA50VClhTkhoZGGGR6AgA3hHJw/dz/d5/L2dJQSEvUUt3QS80TmxFL1o2XzhONThBQjFBME83OUQwUTNGOTQ2TlBQVDg3/)

- [Licitaciones publicadas en la Plataforma de Contratación del Sector Público](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/licitaciones_plataforma_contratacion.aspx)

- [Licitaciones publicadas en los perfiles del contratante ubicados en la Plataforma de Contratación del Sector Público, excluyendo los contratos menores](https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx)

### Schemas CODICE
- [Documentation page: Main schema CODICE-PLACE-EXT-1.1.xsd](https://contrataciondelestado.es/codice/extension/xsd/1.1/docHTML/)
    - In web page, select Group By "Namespace" 
- xmlns:cbc-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2" 
    - [Schema](https://contrataciondelestado.es/codice/extension/xsd/1.4.0/common/CODICE-PLACE-EXT-CommonBasicComponents-1.4.0.xsd)
- xmlns:cac-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2" 
    - [Schema](https://contrataciondelestado.es/codice/extension/xsd/1.4.0/common/CODICE-PLACE-EXT-CommonAggregateComponents-1.4.0.xsd)
- xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
    - [Schema](https://contrataciondelestado.es/codice/extension/xsd/1.4.0/common/CODICE-CommonBasicComponents-2.7.0.xsd)
- xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2"
    - [Schema](https://contrataciondelestado.es/codice/extension/xsd/1.4.0/common/CODICE-CommonAggregateComponents-2.7.0.xsd)

- xmlns:ns7="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
    - [Schema](https://contrataciondelestado.es/codice/extension/xsd/1.4.0/common/UBL-ExtensionContentDataType-2.3.xsd)
- xmlns:at="http://purl.org/atompub/tombstones/1.0"
    - Elements in Atom Tombstones 1.0. IETF (RFC 6721)
    - Elements at:deleted-entry
        Atributes: 
            Mandatory: ref
            Mandatory: when
            Optional: comment
            Optional: by
            Optional: at


### CPV codes
- [Catalan](https://datos.gob.es/es/catalogo/a09002970-listado-de-codigos-cpv)
- [Español](https://www.hacienda.gob.es/DGPatrimonio/SGCCRC/RCSP/cpv2008.xls)
- [Europe](https://ted.europa.eu/en/simap/cpv)

# Tenant emeasespainsandbox
- Compartment: test_csp
  - OCID: ocid1.compartment.oc1..aaaaaaaax4mu6rezfqyl4gtdqcdmb6dna2nyzeixdps7jsyfxbnucr7hjw5a
- Instance: 
  - AD-3
  - Image: Oracle Linux 9 - 2025.10.23-0
  - Shape: Ampere A2
  - OCPUS: 6
  - Memory in GB: 32
  - Security: None
  - Network
    - VCN: labvch
    - Subnet: private
  - Certificates
    - Private key: oci_emeasespainsandbox_test_csp.key
    - Public key: oci_emeasespainsandbox_test_csp.pub
  - Block volume
    - test_csp_block
    - Size: 256
    - VPU: 20
    - Attachment: iSCSI
    - Mount: /dev/oracleoci/oraclevdb
    - OCID: ocid1.volume.oc1.eu-frankfurt-1.abtheljr6xruxkrwzxafyeebcnhodesjb2pwnpv3y43mj77xhyc5bpf7zseq
    - Consistent name: /dev/oracleoci/oraclevda
    - Connect
    ```shell
    sudo iscsiadm -m node -o new -T iqn.2015-12.com.oracleiaas:54efd68c-7ef9-403f-bf4b-d741216df010 -p 169.254.2.2:3260
    sudo iscsiadm -m node -o update -T iqn.2015-12.com.oracleiaas:54efd68c-7ef9-403f-bf4b-d741216df010 -n node.startup -v automatic
    sudo iscsiadm -m node -T iqn.2015-12.com.oracleiaas:54efd68c-7ef9-403f-bf4b-d741216df010 -p 169.254.2.2:3260 -l
    ```
    - Format
    ```shell
    sudo fdisk  /dev/sdb

    Disk /dev/sdb: 256 GiB, 274877906944 bytes, 536870912 sectors
    Disk model: BlockVolume     
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 4096 bytes
    I/O size (minimum/optimal): 4096 bytes / 1048576 bytes
    Disklabel type: gpt
    Disk identifier: 25C07CDD-41E8-E845-A6EB-E944C37E3D08
    
    sudo mkfs.xfs /dev/sdb -f

    ```
    - Disconnect
    ```shell
    sudo iscsiadm -m node -T iqn.2015-12.com.oracleiaas:54efd68c-7ef9-403f-bf4b-d741216df010 -p 169.254.2.2:3260 -u
    sudo iscsiadm -m node -o delete -T iqn.2015-12.com.oracleiaas:54efd68c-7ef9-403f-bf4b-d741216df010 -p 169.254.2.2:3260
    ```

    - fstab
    UUID=563bcc46-becb-42b2-94ac-48ed8c338ff5   /mnt/sdb   xfs   defaults,_netdev,nofail   0 2


# Libraries

## Usando XQuery
### SaxonC-HE
Alternatives for using XQuery to read Atom files

✅ saxonche (SaxonC-HE)

Es la versión gratuita de Saxon para Python, compatible con:
- XQuery 3.1
- XPath 3.1
- XSLT 3.0

Manejo impecable de namespaces, incluso los raros de CODICE y UBL

Carga desde URL, fichero o cadena

👉 Es la única librería madura en Python que soporta XQuery real.

🔍 ¿Por qué NO usar lxml para XQuery?

Porque:

- lxml no soporta XQuery (solo XPath / XSLT 1.0).
- Los XML de la plataforma usan namespaces complejos (UBL + CODICE), y XQuery es muy útil para gestionarlos.
- Puedes usar lxml para parseo básico, pero no para XQuery.

## Alternativas usando sólo XPath

### 🥇 lxml

➡️ Recomendada para el 95 % de los casos prácticos.

Escrita en C (usa libxml2 + libxslt).

XPath 1.0 completo (más que suficiente para feeds Atom y CODICE).

Decenas de veces más rápida que SaxonC en consultas simples.

Soporta namespaces perfectamente.

Ejemplo:
from lxml import etree

doc = etree.parse("feed.atom")

ns = {
    "a": "http://www.w3.org/2005/Atom",
    "place": "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
}

id_plataforma = "50179410029721"
entries = doc.xpath(
    "/a:feed/a:entry["
    "place:ContractFolderStatus/"
    "place:LocatedContractingParty/"
    "cac:Party/"
    "cac:PartyIdentification/"
    "cbc:ID[@schemeName='ID_PLATAFORMA'] = $id]",
    id=id_plataforma,
    namespaces=ns
)

for e in entries:
    print(e.findtext("{http://www.w3.org/2005/Atom}title"))


✅ Ventajas:

Muy rápida (parsing + XPath en C).

Nativa en Python.

Fácil de depurar.

Sin coste de inicialización.

❌ Limitación: solo XPath 1.0 (sin for, let, ni order by).

### 🥈 elementpath

➡️ Implementación pura de XPath 3.1 en Python.

Compatible con XPath 2.0 / 3.1, mucho más expresivo que lxml.

No necesita Java ni C++.

Más lenta que lxml, pero mucho más ligera que SaxonC.

Muy útil si necesitas for, if, cast, funciones, etc.

Ejemplo:
from elementpath import select, XPathContext
from xml.etree import ElementTree as ET

doc = ET.parse("feed.atom").getroot()
ctx = XPathContext(doc, namespaces=ns)

for node in select(ctx,
    "/a:feed/a:entry["
    "place:ContractFolderStatus/"
    "place:LocatedContractingParty/"
    "cac:Party/"
    "cac:PartyIdentification/"
    "cbc:ID[@schemeName='ID_PLATAFORMA'] = '50179410029721']"
):
    print(node.findtext("{http://www.w3.org/2005/Atom}title"))


✅ Ventajas:

XPath 3.1 completo.

Instalación simple (pip install elementpath).

Sin dependencias externas.

❌ Más lenta que lxml en grandes XML.

🥉 xmlschema + elementpath

Si además validas contra los XSD CODICE/UBL, xmlschema usa elementpath internamente, con soporte para XPath 3.1 y validación.
Pero es la más pesada de las tres.

🔍 Comparativa de rendimiento (referencia práctica)
Librería	XPath versión	Velocidad	Ideal para
lxml	1.0	⚡⚡⚡ Muy alta	Lectura y filtrado rápido de XML grandes
elementpath	3.1	⚡ Media	XPath avanzado, sin XQuery
SaxonC-HE / saxonche	3.1 / XQuery	🐢 Lenta	XQuery, XSLT, validación compleja
🚀 Recomendación concreta para ti

Como tus consultas son de este tipo:

/a:feed/a:entry[
  place:ContractFolderStatus/
  place:LocatedContractingParty/
  cac:Party/
  cac:PartyIdentification/
  cbc:ID[@schemeName='ID_PLATAFORMA'] = '...'
]


➡️ Usa lxml.
No notarás pérdida funcional, y el rendimiento aumentará enormemente (10×–50× más rápido).

⚙️ Tip extra: usar iterparse con lxml para feeds grandes

Si los Atom pesan decenas o cientos de MB:

from lxml import etree

context = etree.iterparse("feed.atom", tag="{http://www.w3.org/2005/Atom}entry")

for _, entry in context:
    id_elem = entry.xpath(
        "place:ContractFolderStatus/"
        "place:LocatedContractingParty/"
        "cac:Party/"
        "cac:PartyIdentification/"
        "cbc:ID[@schemeName='ID_PLATAFORMA']",
        namespaces=ns
    )
    if id_elem and id_elem[0].text == "50179410029721":
        print(entry.findtext("{http://www.w3.org/2005/Atom}title"))
    entry.clear()


Procesa el XML en streaming, sin cargarlo entero en memoria — ideal para los feeds de la Plataforma.


# Pending: Optimize

## Migrate to XQuery

pasar de XPath a una única XQuery te da más flexibilidad, claridad y potencia (por ejemplo, puedes construir un XML con resultados, extraer campos o devolver JSON directamente).

Vamos paso a paso, para que quede limpio y reutilizable.

🧩 Tu XPath actual
/a:feed/a:entry[
  place:ContractFolderStatus/
  place:LocatedContractingParty/
  cac:Party/
  cac:PartyIdentification/
  cbc:ID[@schemeName='ID_PLATAFORMA'] = '{id_plataforma}'
]


Este XPath selecciona todas las <entry> cuyo cbc:ID dentro de cac:PartyIdentification
tenga @schemeName="ID_PLATAFORMA" y un valor concreto.

✅ XQuery equivalente “básico” (mismo resultado)
declare default element namespace "http://www.w3.org/2005/Atom";
declare namespace place = "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2";
declare namespace cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2";
declare namespace cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2";

for $e in /feed/entry[
  place:ContractFolderStatus/
  place:LocatedContractingParty/
  cac:Party/
  cac:PartyIdentification/
  cbc:ID[@schemeName='ID_PLATAFORMA'] = "{id_plataforma}"
]
return $e


➡️ Esto devuelve todas las entradas completas (<entry>) que cumplan la condición.
Funcionalmente es lo mismo que tu XPath, pero más expresivo.

✅ XQuery enriquecido: devolver campos concretos

Si en vez del nodo completo quieres un XML reducido, puedes construirlo con FLWOR:

declare default element namespace "http://www.w3.org/2005/Atom";
declare namespace place = "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2";
declare namespace cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2";
declare namespace cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2";

<resultados>{
  for $e in /feed/entry[
    place:ContractFolderStatus/
    place:LocatedContractingParty/
    cac:Party/
    cac:PartyIdentification/
    cbc:ID[@schemeName='ID_PLATAFORMA'] = "{id_plataforma}"
  ]
  return
    <entryResumen>
      <id>{$e/id/text()}</id>
      <title>{$e/title/text()}</title>
      <updated>{$e/updated/text()}</updated>
      <organo>{
        $e/place:ContractFolderStatus/
          place:LocatedContractingParty/
          cac:Party/
          cac:PartyIdentification/
          cbc:ID[@schemeName='NIF']/text()
      }</organo>
    </entryResumen>
}</resultados>


Esto produce un XML limpio con solo la información que te interesa, por ejemplo:

<resultados>
  <entryResumen>
    <id>https://contrataciondelestado.es/sindicacion/licitacionesPerfilContratante/16245671</id>
    <title>Servicio de analíticas…</title>
    <updated>2024-12-31T14:48:52.402+01:00</updated>
    <organo>G96236443</organo>
  </entryResumen>
  ...
</resultados>

✅ XQuery aún más potente (parametrizable)

Si vas a ejecutarlo desde Python y quieres pasar el valor de forma segura,
puedes definir una variable externa:

declare variable $id_plataforma external;
declare default element namespace "http://www.w3.org/2005/Atom";
declare namespace place = "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2";
declare namespace cac = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2";
declare namespace cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2";

for $e in /feed/entry[
  place:ContractFolderStatus/
  place:LocatedContractingParty/
  cac:Party/
  cac:PartyIdentification/
  cbc:ID[@schemeName='ID_PLATAFORMA'] = $id_plataforma
]
return $e


Y en Python:

xq = proc.new_xquery_processor()
xq.set_query(open("query.xq").read())
xq.set_context(xdm_item=doc)
xq.set_parameter("id_plataforma", proc.make_string_value("50179410029721"))
result = xq.run_query_to_value()

✅ En resumen
Variante	Qué devuelve	Ideal para
Básica	Nodos <entry> completos	Reemplazo directo de XPath
Enriquecida (con <entryResumen> )	XML personalizado	Integración o exportación
Parametrizable	Cualquier resultado	Ejecución desde Python