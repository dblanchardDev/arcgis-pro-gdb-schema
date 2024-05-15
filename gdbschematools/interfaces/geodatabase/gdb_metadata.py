"""
Read complex metadata from geodatabases, datasets, and fields.

Author: David Blanchard
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import Union
import arcpy

# Cache previously fetched items
_METADATAS:dict[str, arcpy.metadata.Metadata] = {}
_FGDC_XML:dict[str, ET.Element] = {}
_RAW_XML:dict[str, ET.Element] = {}


def clear_caches():
    """Clears the caches forcing metadata XML to be re-read from disk."""
    _METADATAS.clear()
    _FGDC_XML.clear()
    _RAW_XML.clear()


def get_geodatabase_summary(desc:object) -> Union[str, None]:
    """Get a geodatabase's metadata summary.

    Args:
        desc (object): ArcPy Describe object for the geodatabase.

    Returns:
        Union[str, None]: Summary or None if not found.
    """
    return _get_summary(desc)


def get_dataset_summary(desc:object) -> Union[str, None]:
    """Get a dataset's metadata summary.

    Args:
        desc (object): ArcPy Describe object for the dataset.

    Returns:
        Union[str, None]: Summary or None if not found.
    """
    return _get_summary(desc)


def _get_summary(desc:object) -> Union[str, None]:
    """Get a geodatabase element's summary.

    Args:
        desc (object): ArcPy Describe object for the element.

    Returns:
        Union[str, None]: Either the summary or None is none found.
    """

    # Try using ArcPy's metadata object
    ap_meta = _get_arcpy_metadata(desc)

    if ap_meta.summary:
        return ap_meta.summary

    if ap_meta.description:
        return _strip_html_tags(ap_meta.description)

    # Try the FGDC Metadata XML abstract
    fgdc_xml = _get_xml(desc, "FGDC")
    fgdc_abstr_tags = fgdc_xml.getroot().findall(".//descript/abstract")

    if fgdc_abstr_tags:
        return fgdc_abstr_tags[0].text

    # Try legacy X-Ray style metadata
    raw_xml = _get_xml(desc, "RAW")
    raw_abstr_tags = raw_xml.getroot().findall(".//abstract")

    if raw_abstr_tags:
        return raw_abstr_tags[0].text

    return None


def get_field_summary(dataset_desc:object, field_name:str) -> Union[str, None]:
    """Get a field's metadata summary.

    Args:
        dataset_desc (object): ArcPy Describe object for the dataset that contains the field.
        field_name (str): Name of the field for which the summary is to be retrieved.

    Returns:
        Union[str, None]: Either the summary or None is none found.
    """
    xml = _get_xml(dataset_desc, "FGDC")

    all_attributes = xml.getroot().findall(".//eainfo/detailed/attr")
    for attr in all_attributes:
        try:
            if attr.find("attrlabl").text == field_name:
                udom = attr.find(".//udom")
                if udom is not None:
                    return udom.text

                attrdef = attr.find("attrdef")
                if attrdef is not None:
                    return attrdef.text
        except Exception as exc:
            #pylint: disable-next=broad-exception-raised
            raise Exception(f"Failure while reading {field_name} metadata summary.") from exc

    return None


def get_enumerated_domain_values(dataset_desc:object, field_name:str) -> dict[str, str]:
    """Get all enumerated domain values from the metadata for a particular field.

    Args:
        dataset_desc (arcpy description): Description of the dataset that contains the field with a domain.
        field_name (str): Name of the field that has a domain.

    Returns:
        dict[str, str]: {domain value: value definition}
    """
    try:
        xml = _get_xml(dataset_desc, "FGDC")
        enum = {}
        all_attributes = xml.getroot().findall(".//eainfo/detailed/attr")
        for attr in all_attributes:
            if attr.find("attrlabl").text == field_name:
                for edom in attr.findall("attrdomv/edom"):
                    edomv = edom.find("edomv")
                    if edomv is not None:
                        value = edomv.text
                        definition = None
                        edomvd = edom.find("edomvd")
                        if edomvd is not None:
                            definition = edomvd.text
                        enum[value] = definition

        return enum
    except Exception as exc:
        #pylint: disable-next=broad-exception-raised
        raise Exception(f"Failure while enumerated domain values from the {field_name} field metadata.") from exc


def _get_arcpy_metadata(desc:object) -> arcpy.metadata.Metadata:
    """Get the arcpy Metadata object for the item.

    Args:
        desc (object): ArcPy Describe object for the element.

    Returns:
        arcpy.metadata.Metadata: Arcpy metadata object or None if not found.
    """

    path = desc.catalogPath

    if path not in _METADATAS:
        _METADATAS[path] = arcpy.metadata.Metadata(path)

    return _METADATAS[path]


def _get_xml(desc:object, xml_format:str) -> ET.ElementTree:
    """Get the raw or FGDC-formatted XML metadata.

    Args:
        desc (object): ArcPy Describe object for the element.
        format (str): Either "RAW" or "FGDC".

    Returns:
        ET.ElementTree: XML Tree for the metadata.
    """

    path = desc.catalogPath
    cache = _FGDC_XML if xml_format == "FGDC" else _RAW_XML

    if path not in cache:
        # pylint: disable-next=no-member
        path = arcpy.CreateUniqueName("metadata.xml", arcpy.env.scratchFolder)
        ap_meta = _get_arcpy_metadata(desc)

        if xml_format == "FGDC":
            ap_meta.exportMetadata(path, "FGDC_CSDGM", "EXACT_COPY")
        else:
            ap_meta.saveAsXML(path, "EXACT_COPY")

        cache[path] = ET.parse(path)
        os.remove(path)

    return cache[path]


def _strip_html_tags(source:str) -> str:
    """Strip the HTML tags out of a string.

    Args:
        source (str): String with HTML tags.

    Returns:
        str: String with HTML tags removed.
    """

    pattern = "<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>"
    return re.sub(pattern, "", source)


def update_metadata(path_to_element:str, meta_summary: str):
    """Update the metadata summary of Geodatabase, Feature Dataset, Table/Feature Class/Relationship Class

    Args:
        path_to_element (str): The path of GDB or dataset in geodatabase.
        meta_summary (str): Metadata summary of an element
    Raises:
        PermissionError: Raised when trying to update metadata without the adequate access rights
    """
    # Assign the Metadata summary to the element
    md = arcpy.metadata.Metadata(path_to_element)

    if not md.isReadOnly:
        md.summary = meta_summary
        md.save()
    else:
        raise PermissionError(f"Metadata of {path_to_element} is Read Only.")


def update_field_metadata(path_to_dataset:str, field_name:str, field_meta_summary:str=None, field_alias:str=None):
    """Update a field's metadata summary

    Args:
        path_to_dataset (str): The path of the dataset that contains the field.
        field_name (str): Name of the field for which the metadata summary is to be updated.
        field_meta_summary (str, optional): Metadata summary of the field. Defaults to None.
        field_alias (str, optional): Alias of the field. Defaults to None.
    """
    # get the dataset's metadata XML
    root = read_metadata_xml(path_to_dataset)

    # Create eainfo element
    eainfo = ET.SubElement(root, "eainfo") if not root.find(".//eainfo") else root.find(".//eainfo")

    # Create eainfo/detailed element
    detailed = ET.SubElement(eainfo, "detailed") if not eainfo.find("detailed") else eainfo.find("detailed")

    # Create eainfo/detailed/enttyp element
    if not detailed.find("enttyp"):
        enttyp = ET.SubElement(detailed, "enttyp")
        enttypl = ET.SubElement(enttyp, "enttypl")
        enttypl.text = "Fields"

    # Create eainfo/detailed/enttyp element
    attr = next((attr for attr in detailed.findall("attr") if attr.find("attrlabl").text == field_name), False)
    if not attr:
        attr = ET.SubElement(detailed , "attr")
        attrlabl = ET.SubElement(attr, "attrlabl")
        attrlabl.text = field_name

    attrdef = attr.find("attrdef") if attr.find("attrdef") is not None else ET.SubElement(attr, "attrdef")
    if field_meta_summary is not None:
        attrdef.text = field_meta_summary

    attalias = attr.find("attalias") if attr.find("attalias") is not None else ET.SubElement(attr, "attalias")
    if field_alias is not None:
        attalias.text = field_alias

    # call the write_metadata_xml function to write the item's metadata
    write_metadata_xml(path_to_dataset, root)


def update_edomain_metadata(path_to_dataset:str, field_name:str, edomain: any, code: any,
                            field_meta_summary:str=None, field_alias:str=None):
    """Add field enumerated domain into field's metadata

    Args:
        path_to_dataset (str): Path of the dataset that contains the field.
        field (Field): Name of the field that has a enumerated domain.
        edomain (any): enumerated domain meta summary/definition.
        code (any): enumerated domain value.
        field_meta_summary (str, optional): Metadata summary of the field. Defaults to None.
        field_alias (str, optional): Alias of the field. Defaults to None.
    """
    # get the dataset's metadata XML
    root = read_metadata_xml(path_to_dataset)

    # find the attribute element in xml object by the subtype.field.name
    attributes = root.findall(".//eainfo/detailed/attr")

    # Check if an attribute element in metadata xml exists for the field
    existing_attr = next((attr for attr in attributes if attr.find("attrlabl").text == field_name), False)
    existing_edom = False

    if existing_attr:
        attrdomv = existing_attr.find("attrdomv")
        if attrdomv:
            existing_edom=next((edom for edom in attrdomv.findall("edom") if edom.find("edomv").text==str(code)), False)
            if existing_edom:
                edomvd = existing_edom.find("edomvd") if existing_edom.find("edomvd") is not None \
                    else ET.SubElement(existing_edom, "edomvd")
                edomvd.text = edomain.codes[code].meta_summary

    else:
        # add an attribute element in metadata xml for the field and update dataset's metadata
        update_field_metadata (path_to_dataset, field_name, field_meta_summary, field_alias)
        root = read_metadata_xml(path_to_dataset)

    if not existing_edom:
        for attr in root.findall(".//eainfo/detailed/attr"):
            if attr.find("attrlabl").text == field_name:
                attrdomv = attr.find("attrdomv") if attr.find("attrdomv") is not None \
                    else ET.SubElement(attr, "attrdomv")
                # add field enumerated domains (value and definition) under the corresponding attribute
                edom = ET.SubElement(attrdomv, "edom")
                edomv = ET.SubElement(edom, "edomv")
                edomv.text = str(code)
                edomvd = ET.SubElement(edom, "edomvd")
                edomvd.text = edomain.codes[code].meta_summary
                break

    # call the write_metadata_xml function to write the item's metadata
    write_metadata_xml(path_to_dataset, root)


def read_metadata_xml(path_to_dataset:str) -> ET.Element:
    """create an xml ElementTree object from a dataset's metadata

    Args:
        path_to_dataset (str): The path of dataset in geodatabase.

    Returns:
        ET.Element: XML Tree for the metadata.
    """
    # get the dataset's metadata xml
    md = arcpy.metadata.Metadata(path_to_dataset)
    xml = md.xml
    root = ET.fromstring(xml)
    return root

def write_metadata_xml(path_to_dataset:str, root:ET.Element):
    """Write an xml elementTree to a dataset's metadata

    Args:
        path_to_dataset (str): The path of dataset in geodatabase.
        root (ET.Element): XML Tree for the metadata.

    Raises:
        PermissionError: Raised when trying to update metadata without the adequate access rights
    """
    # get the dataset's metadata
    md = arcpy.metadata.Metadata(path_to_dataset)
    if not md.isReadOnly:
        md.xml = ET.tostring(root, encoding="utf-8")
        md.save()
    else:
        raise PermissionError(f"{path_to_dataset}'s Metadata is Read Only.")