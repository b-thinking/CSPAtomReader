
# Instrucciones

## Introducción

Este script procesa las licitaciones publicadas en la plataforma de contratación del sector público. 

Para ello procesa los datos abiertos según se indica en la plataforma [Datos Abiertos](https://contrataciondelestado.es/wps/portal/plataforma/datos_abiertos/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziTVz9nZ3dPIwMLIKNXQyMfFxCQ808gFx3U_1wsAJTY2eTMK-wALNgT3cDA08PNxefUENTA3cjM_0oYvQb4ACOBsTpx6MgCr_x4fpR-K0wgirA50VClhTkhoZGGGR6AgA3hHJw/dz/d5/L2dJQSEvUUt3QS80TmxFL1o2XzhONThBQjFBME83OUQwUTNGOTQ2TlBQVDg3/)

Por otro lado, los datos abiertos los publica el ministerio de hacienda, en el portal [Licitaciones publicadas en la Plataforma de Contratación del Sector Público](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/licitaciones_plataforma_contratacion.aspx). En este portal se publican 6 juegos de datos distintos. Este script se ha probado con [Licitaciones publicadas en los perfiles del contratante ubicados en la Plataforma de Contratación del Sector Público, excluyendo los contratos menores](https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx) pero técnicamente se debe poder usar con cualquiera de los otros 5 juego de datos.

En el portal de [Datos Abiertos](https://contrataciondelestado.es/wps/portal/plataforma/datos_abiertos/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziTVz9nZ3dPIwMLIKNXQyMfFxCQ808gFx3U_1wsAJTY2eTMK-wALNgT3cDA08PNxefUENTA3cjM_0oYvQb4ACOBsTpx6MgCr_x4fpR-K0wgirA50VClhTkhoZGGGR6AgA3hHJw/dz/d5/L2dJQSEvUUt3QS80TmxFL1o2XzhONThBQjFBME83OUQwUTNGOTQ2TlBQVDg3/) la propia plataforma publica una herramienta denominada OpenPLACSP para poder exportar a formato Excel las licitaciones. Esta herramienta tiene dos problemas para lo que se buscaba. Por un lado publica todos los pliegos sin dejar filtro por entidad, y por otro lado no indica los documentos asociados a cada pliego, que era lo que nos interesaba. Pero es interesante que siendo una herramienta de código abierto, se puede reutilizar su código para usos posteriores (es Java, no Python).

Por eso se ha creado este script, que aporta
- Se descarga en format CSV los pliegos de determinada entidad (se pueden indicar varias entidades)
- Y para cada pliego, identifica las URLs de acceso a los documentos. Actualmente sólo indica los documentos de tipo técnico y generales (que era lo que me interesaba) pero añadir el resto (documentos legales) es trivial.

## Configuración

El script procesa los pliegos publicados en formato RSS Atom publicados en [Licitaciones publicadas en los perfiles del contratante ubicados en la Plataforma de Contratación del Sector Público, excluyendo los contratos menores](https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx)

El script es código python, y se ha probado con la versión 3.12. 

Si se usa pyenv para manejar entornos virtuales, se provee un script [configureEnvironment-pyenv.sh](./configureEnvironment-pyenv.sh) para configurar el entorno virtual. En este caso se debe invocar con `source configureEnvironment-pyenv.sh`.

Si se usa venv, se provee un script [configureEnvironment-venv.sh](./configureEnvironment-venv.sh) para configurar el entorno virtual. En este caso se debe invocar con `source configureEnvironment-venv.sh`.

En caso de no usar entorno virtual, se deben instalar las dependencias con `pip install -r requirements.txt`

La configuración se realiza mediante un fichero `.env` con las variables de entorno. Se provee un archivo [.env.sample](./.env.sample) que debe editarse y renombrarse a `.env`. antes de usar el script.

### Modos de operación: El script puede operar de dos maneras:

- O bien trabaja con todos los ficheros descargados a un directorio local. En este caso, primero deben descargarse todos los archivos y descomprimirse en orden (del más antiguo al más nuevo). Para ello se provee el script [download_linux.py](./download_linux.sh) que descarga los ficheros y los descomprime. Este el modo recomendado si se tiene que procesar o buscar pliegos de varios meses o años. Para usar este modo se debe definir las siguientes variables en el archivo `.env`:

  ```ini
  FILE_LOCATION="LOCAL"
  PREFIX_PATH="<Ruta a la carpeta donde se han descomprimido los ficheros>"
  FILE="licitacionesPerfilesContratanteCompleto3.atom"
  ```

- O bien trabaja con los ficheros descargados directamente de la plataforma. En este caso se debe definir las siguientes variables en el archivo `.env`:

  ```ini 
  FILE_LOCATION="WEB"
  PREFIX_URL="https://contrataciondelestado.es/sindicacion/sindicacion_643"
  FILE="licitacionesPerfilesContratanteCompleto3.atom"
  ```

  NOTA: La URL https://contrataciondelestado.es/sindicacion/sindicacion_643 es la URL de la web oficial de la plataforma de Contratación del Sector Público para el primer juego de datos

### Selección de las entidades a buscar

Las entidades a seleccionar deben identificarse en el inventario de todas las [entidades registradas en la plataforma](https://contrataciondelsectorpublico.gob.es/datosabiertos/OrganosContratacion.xlsx). **ES IMPORTANTE** que dependiendo el tipo de entidad, cada entidad está identificada o por su ID en la plataforma, por su código ID3 o por su NIF. Ahora mismo, el script soporta el ID de plataforma y el DIR3 (añadir el NIF es trivial si fuera necesario). Es importante que determinadas entidades publican sus pliegos sin ID de plataforma y hay que buscarlos por DIR3 (por ejemplo, Banco de España, aunque tiene ID de plataforma, pública sus pliegos sólo con ID3)

Una vez identificadas las entidades, se pueden indicar en el archivo `.env` en las variables `ENTRY_CONTRACTOR_IDS`y/o `ENTRY_DIR3_IDS`, según se use IDs o ID3, de la siguiente manera:

```ini
# ADIF
ENTRY_CONTRACTOR_IDS="4051681009106,1000017000091,4051701009108,4001664000272,4051581009080,4051601009082,5034741006576,5055461009728,4001667000272,1000017000094,1000017000094,4001663000272,1000017000092,1000017000008,1000017000008,1000017000092,1000017000091,1000017000092,1000017000092,4001662000272,1000017000093,1000017000093,1000017000093,1000017000091,1001010000091,1000017000094,1000017000095,1000017000095,1000017000095,1000017000095,1000017000091,1000017000091,1000017000092,1000017000092,1000017000092,1000017000094,1000017000094,1000017000094,1000017000094,1000017000095,1000017000093,1000017000095,1000017000095,1000017000095,4001661000272,1000017000095,1000017000091,1000017000091,4001666000272,1000017000093,1000017000093,4001668000272,4001665000272,1000017000093,1000017000093,1000017000094,4051702009108,4051721009112,4051722009112,4051742009114,4051761009116,4051602009082"
ENTRY_DIR3_IDS="EA0003338,EA0008223,EA0008352,EA0008559"
```


### Selección de las fechas a buscar
Al ser ficheros RSS, siempre se parte del último y se procesan hacia atrás. En caso de usar el sistema en línea, se procesa el fichero publicado el día anterior hacia atrás (se publican uno o varios diariamente). En el caso de ficheros locales, se procesa el fichero último descargado, y siempre hacia atrás.

Se puede indicar la fecha límite a buscar usando la variable `DOC_UPDATED_AFTER` poniendo la fecha más antigua en formato ISO. Por ejemplo para procesar el año 2025 completo se debe indicar

```ini
DOC_UPDATED_AFTER="2025-01-01T00:00:00+01:00"
```

### Depuración y log
El script saca la salida a la salida estándar stdout y los errorer y trazas a la salida stderr. Se puede activar la depuración con la variable `LOG_LEVEL` poniendo el nivel de depuración a usar (DEBUG, INFO, WARNING, ERROR). Por ejemplo para activar la depuración a nivel DEBUG se debe indicar

```ini
LOG_LEVEL="DEBUG"
```

## Ejecución

### Llamada

El script envía la salida a la salida estándar, y las trazas y errores a la salida de error.

Por tanto, un ejecución simple puede ser:

```shell
python ./readatom.py > licitaciones_bde.csv 2> licitaciones_bde.log
```

### Salida del script
El script genera la salida en formato CSV (separado por comas, con punto decimal) con la siguiente estructura:
- Una fila por cada licitación encontrada, con esta estructura: "ID Licitador en la plataforma","DIR3","Id licitación (Asignado por el contratante)","CPV","Title","Date","Total Amount","Id (en la plataforma)","URL (para poder ir a la licitación en la plataforma)","Adjudicatario (si está adjudicada)". En este punto es muy importante el campo CPV [Common Procurement Value](https://www.hacienda.gob.es/DGPatrimonio/SGCCRC/RCSP/cpv2008.xls), que indica el tipo de contrato. Por ejemplo, los CPV empezando por 72 son servicios informáticos
- Varias filas con los documentos técnicos de la licitación (los pliegos). Para cada documento, se indica la palabra "TechnicalDoc:", el nombre del documentom la URL de acceso y el código hash de validación. Con estas URLs, usando un comando `wget` se pueden descargar los documentos. Normalmente hay 1 documento técnico, pero puede haber varios o incluso ninguno
- Varias filas con los documentos generales de la licitación. Cada documento tiene la estructura se indica la palabra "GeneralDoc:", un identificativo único del documento, la URL de acceso y un campo descripción. **No se incluye el nombre del documento**, pero si se va a descargar, se puede usar el id puesto que es único.
- **IMPORTANTE**: Hay otras categorías de documentos que no se incluyen en el script. Específicamente, los legales (contratos firmados) no se descargar, pero no costaría nada añadirlos

Ejemplo de salida:
```csv
"ID_PLATAFORMA","DIR3","Contract Folder Id","CPV","Title","Date","Total Amount","Id","URI","Tender Name/Document Hash/Filename"
"51081180151878","I00000381","LIC-11405","64100000","La prestación de servicios de traslado de documentación (valijas) entre las oficinas del Banco de España en C/Alcalá, 48 de Madrid y sus sucursales.","2025-12-10T17:25:41.623000+01:00",20507.32,"https://contrataciondelestado.es/sindicacion/licitacionesPerfilContratante/18570792","https://contrataciondelestado.es/wps/poc?uri=deeplink:detalle_licitacion&idEvl=w7uz3zl9gx710HRJw8TEnQ%3D%3D","RESPONSABILIDAD SOCIAL ONTIME, S.L."
"51081180151878","I00000381","LIC-11405","64100000","La prestación de servicios de traslado de documentación (valijas) entre las oficinas del Banco de España en C/Alcalá, 48 de Madrid y sus sucursales.","2025-12-10T17:25:41.623000+01:00","TechnicalDoc:","LIC11405 PPT PLACSP.pdf","https://contrataciondelestado.es/FileSystem/servlet/GetDocumentByIdServlet?cifrado=QUC1GjXXSiLkydRHJBmbpw%3D%3D&DocumentIdParam=EM/KGxrUgDT1rwI7V12rkFhcfHbpSEyoooMJh7OdIMaTTrCrtCsRdkaFjIIMBTjjkatzQK2C/sS88qCNOzc/elLJ8z3Y6ehAr6SxI5emCefDdQD9RyhUmzT4jZ2In4zL","hhG79c/850u31KT/5rFXej459gk="
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00",5111040.0,"https://contrataciondelestado.es/sindicacion/licitacionesPerfilContratante/17526089","https://contrataciondelestado.es/wps/poc?uri=deeplink:detalle_licitacion&idEvl=VXtDm9SK7oOcTfjQf3USOg%3D%3D",""
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","TechnicalDoc:","LIC7502 PPT.pdf","https://contrataciondelestado.es/FileSystem/servlet/GetDocumentByIdServlet?DocumentIdParam=%2BYj5WRGsef8yRVvgKvn7AWy0tiEVSJZvDzOFtnKQgwj/2NhlfVVgUjLBD06%2BO4Zrc83NPNvcaMAl/8XJ69IIiCmvf6d1/8/jOI36qHUrvXa1aXEvq3KHa/AEHgtDrQw0&cifrado=QUC1GjXXSiLkydRHJBmbpw%3D%3D","DLVjs40CYDUkcqwUs3CDHdl26YM="
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-558944c4-0db0-4e65-a84f-3d038a19b329","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-558944c4-0db0-4e65-a84f-3d038a19b329","Documento de aprobación del expediente"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-b2ca8197-cf89-41c6-a05f-230073bb45d0","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-b2ca8197-cf89-41c6-a05f-230073bb45d0","Acta del órgano de asistencia"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-602b6268-9dbd-466e-95dc-d893b1592786","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-602b6268-9dbd-466e-95dc-d893b1592786","Propuesta de adjudicación aprobada"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-066097c4-ceca-4c13-8294-f53794991b11","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-066097c4-ceca-4c13-8294-f53794991b11","Acta del órgano de asistencia"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-afce308d-e765-4623-a5a2-ef93ed33650c","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-afce308d-e765-4623-a5a2-ef93ed33650c","Nota informativa sobre traslado de apertura"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-8c146608-af5f-4749-b4e7-d56d7227727b","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-8c146608-af5f-4749-b4e7-d56d7227727b","Nota informativa sobre traslado de apertura"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-233adc27-b96f-496b-8e38-85a33e812ca7","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-233adc27-b96f-496b-8e38-85a33e812ca7","Nota informativa sobre traslado de apertura"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-cd250069-bb80-4979-8b90-074cf82fd7bc","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-cd250069-bb80-4979-8b90-074cf82fd7bc","Informe de valoración de los criterios de adjudicación cuantificables mediante juicio de valor"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-9c2f94d4-488a-419e-bba8-0870b54d2a20","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-9c2f94d4-488a-419e-bba8-0870b54d2a20","Acta del órgano de asistencia"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-8475bdd1-0854-4c4c-9490-839c31247e4f","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-8475bdd1-0854-4c4c-9490-839c31247e4f","Acta del órgano de asistencia"
"51081180151878","I00000381","LIC-7502","72610000","Contratación del Servicio de Centro de Seguimiento de Proyectos, Transformación Ágil y Soporte a la Dirección y Gobierno del Departamento de Sistemas de Información","2025-12-10T11:18:40.260000+01:00","GeneralDoc:","2025-7702dc2f-b9a4-46d1-996a-7ce17ed36447","https://contrataciondelestado.es/wps/wcm/connect/PLACE_es/Site/area/docAccCmpnt?srv=cmpnt&cmpntname=GetDocumentsById&source=library&DocumentIdParam=2025-7702dc2f-b9a4-46d1-996a-7ce17ed36447","Documento de formalización"
```

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

# VM for processing

Como el script tarda un rato, se ha creado una VM con la que se puede ejecutar el script. Si hace falta, pedidme los datos de acceso.

- Tenant emeasespainsandbox
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
    - VCN: labvcn
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


