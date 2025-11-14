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


# Libraries

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