# ulvl - Universal Level Formats
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This library reads and writes universal level formats.  These level
formats are generic enough to be used by any 2-D game.  Their purpose is
to unify level editing under a simple, universal format.
"""


__version__ = "1.0"
__author__ = "Layla Marchant"
__all__ = ["TileLayer", "LevelObject", "ASCL", "JSL", "ULX", "TMX"]


import base64
import gzip
import json
import warnings
import xml.etree.ElementTree as ET
import zlib


class TileLayer:
    """
    A layer of tiles.  Tiles are simple position-based objects with no
    special individual options, generally useful for large numbers of
    basic objects.

    .. attribute:: type

       The type of tile layer this is. Can be any arbitrary value.

    .. attribute:: columns

       The number of columns in each tile row.

    .. attribute:: tiles

       A list of integers indicating the tiles of the layer.  A value of
       ``0`` indicates no tile.  Any higher value indicates the tile ID
       of the tile.  Tile IDs are arbitrary; you decide what each tile
       ID means for the game.

    .. attribute:: meta

       Meta variable for the tile layer as a whole.  Can be any value.
       Set to ``None`` for no value.
    """

    def __init__(self, type_, columns, tiles, meta=None):
        self.type = type_
        self.columns = columns
        self.tiles = tiles
        self.meta = meta


class LevelObject:

    """
    A generic level object.  Level objects are similar to tiles, but
    positioning is arbitrary and they can have meta information assigned
    to them.

    .. attribute:: type

       The type of object this is.  Can be any arbitrary value.

    .. attribute:: meta

       Meta variable of the object.  The meaning of this value is
       completely arbitrary; use it for any variations (position, size,
       etc) level objects have, in whatever way is most appropriate for
       the game.  Set to ``None`` for no value.
    """

    def __init__(self, type_, meta=None):
        self.type = type_
        self.meta = meta


class ASCL:

    """
    This class loads, stores, and saves ASCII Level (ASCL) files.  This
    format is based on a grid of plain text characters and generally has
    one of the following extensions: ".ascl", ".asc", ".txt".

    An ASCL file contains two main components: the meta variable
    definitions and the level object grid.

    Meta variables are defined simply at the top of the file: each line
    indicates the value of a different meta variable, always a string.
    Any number of meta variables can be defined.

    Everything after the first blank line in the ASCL file is considered
    to be part of the tile layer.  Here, ASCII characters are used to
    represent the tiles found in :attr:`tiles`.

    .. attribute:: meta

       A list of the level's meta variables.

       .. note::

          The meta variables can be any value, but when the ASCL is
          saved, all meta variables will be automatically converted to
          strings.

    .. attribute:: layer

       A :class:`TileLayer` object indicating the tiles of the level.

       .. note::

          Due to the nature of the format, the layer type and meta
          variable of the layer are ignored and not preserved when
          saving.
    """

    def __init__(self):
        self.meta = []
        self.tiles = TileLayer(None, 0, [])

    @classmethod
    def load(cls, f):
        """
        Load the indicated file and return an :class:`ASCL` object.
        """
        self = cls()

        data = f.read()

        grid_lines = []
        grid = False
        columns = 0
        for line in data.splitlines():
            if grid:
                line = line.encode("utf-8")
                grid_lines.append(line)
                columns = max(columns, len(line))
            elif line:
                self.meta.append(line)
            else:
                grid = True

        tiles = []
        for line in grid_lines:
            for i in range(columns):
                if i < len(line):
                    value = line[i]
                    if value == ord(' '):
                        value = 0
                    tiles.append(value)
                else:
                    tiles.append(0)

        self.layer = TileLayer(None, columns, tiles)

        return self

    def save(self, f):
        """
        Save the object to the indicated file.
        """
        meta_data = [str(v) for v in self.meta]
        tile_data = []
        for i in range(len(self.layer.tiles)):
            if i % self.layer.columns == 0:
                tile_data.append(ord('\n'))
            if self.layer.tiles[i] == 0:
                tile_data.append(ord(' '))
            else:
                tile_data.append(self.layer.tiles[i])

        meta_text = '\n'.join(meta_data)
        tile_text = bytes(tile_data).decode("utf-8")
        text = '\n\n'.join([meta_text, tile_text])

        f.write(text)


class JSL:

    """
    This class loads, stores, and saves JavaScript Level (JSL) files.
    This format is based on JSON and generally has one of the following
    extensions: ".jsl", ".json".

    A JSL file contains a top-level object with the following keys:

    - ``"meta"``: A value of any type indicating the layer's meta
      variable.

    - ``"objects"``: An object with the level's object types as keys and
      arrays as values.  The array lists the meta variables of all
      objects of the respective type (``null`` for objects with no meta
      variable defined).

    - ``"layers"``: An array of objects indicating tile layers, with
      each of these objects containing the following keys:

      - ``"type"``: A value of any type indicating the type of the
        layer.
      - ``"columns"``: An integer indicating the number of columns in
        the tile layer.
      - ``"tiles"``: A zlib-compressed, base64-encoded string encoding
        the tile IDs as data.
      - ``"meta"``: A value of any type indicating the layer's meta
        variable.

    .. attribute:: meta

       Meta variable for the level as a whole.  Can be any value.

    .. attribute:: objects

       A list of :class:`LevelObject` objects representing objects of
       the level.

    .. attribute:: layers

       A list oj :class:`TileLayer` objects representing the tile layers
       of the level.
    """

    def __init__(self):
        self.meta = None
        self.objects = []
        self.layers = []

    @classmethod
    def load(cls, f):
        """
        Load the indicated file and return a :class:`JSL` object.
        """
        self = cls()

        data = json.load(f)

        self.meta = data.get("meta")

        for k in data.get("objects", {}):
            for o in data["objects"][k]:
                obj = LevelObject(k, o)
                self.objects.append(obj)

        for layer in data.get("layers", []):
            tdata = layer.get("tiles")
            if tdata:
                type_ = layer.get("type")
                columns = layer.get("columns", 1)
                tiles = data_decode(tdata)
                meta = layer.get("meta")
                self.layers.append(TileLayer(type_, columns, tiles, meta))

        return self

    def save(self, f):
        """Save the object to the indicated file."""
        data = {"meta": self.meta, "objects": {}, "layers": []}

        for obj in self.objects:
            data["objects"].setdefault(obj.type, []).append(obj.meta)

        for layer in self.layers:
            layer_data = {
                "type": layer.type, "columns": layer.columns,
                "tiles": data_encode(layer.tiles), "meta": layer.meta}
            data["layers"].append(layer_data)

        json.dump(data, f, indent=4)


class ULX:

    """
    This class loads, stores, and saves Universal Level XML (ULX) files.
    This format is based on XML and generally has one of the following
    extensions: ".ulx", ".xml".

    A ULX file contains a root tree with the name "level" containing the
    following children:

    - ``meta``: Contains one element for each of the level's meta
      variables.  Each element's tag indicates the name of the meta
      variable, while its text indicates the value.

    - ``objects``: Contains ``object`` elements.  Each ``object``
      element has the following attributes:

      - ``"type"``: The object's type.
      - ``"meta"``: The object's meta variable.

    - ``layers``: Contains ``layer`` elements.  Each ``layer`` element
      contains text indicating the layer's tiles as zlib-compressed
      base64-encoded text, and the following attributes:

      - ``"type"``: The layer's type.
      - ``"columns"``: The number of columns in the tile layer.
      - ``"meta"``: The layer's meta variable.

    .. note::

       Types and meta variables of all kinds can be any value, but due
       to the nature of XML, all types and meta variables are converted
       to strings when the ULX is saved. A value of ``None``
       leads to the ULX omitting the meta variable.

    .. attribute:: meta

       A dictionary of all of the level's meta variables.

    .. attribute:: objects

       A list of objects in the level as :class:`LevelObject`
       objects.

    .. attribute:: layers

       A list oj :class:`TileLayer` objects representing the tile layers
       of the level.
    """

    def __init__(self):
        self.meta = {}
        self.objects = []
        self.layers = []

    @classmethod
    def load(cls, f):
        """
        Load the indicated file and return a :class:`ULX` object.
        """
        self = cls()

        tree = ET.parse(fname)
        root = tree.getroot()

        for child in root:
            if child.tag == "meta":
                for meta in child:
                    self.meta[meta.tag] = meta.text
            elif child.tag == "objects":
                for obj in child.findall("object"):
                    type_ = obj.attrib.get("type")
                    meta = obj.attrib.get("meta")
                    self.objects.append(LevelObject(type_, meta))
            elif child.tag == "layers":
                for layer in child.findall("layer"):
                    type_ = layer.attrib.get("type")
                    columns = int(layer.attrib.get("columns", 1))
                    tiles = data_decode(layer.text)
                    meta = layer.attrib.get("meta")
                    self.layers.append(TileLayer(type_, columns, tiles, meta))

        return self

    def save(self, fname):
        """
        Save the object to the indicated file name.
        """
        root = ET.Element("level")

        meta_elem = ET.Element("meta")
        for i in self.meta:
            elem = ET.Element(i)
            elem.text = str(self.meta[i])
            meta_elem.append(elem)
        root.append(meta_elem)

        objects_elem = ET.Element("objects")
        for obj in self.objects:
            attr = {}
            if obj.type is not None:
                attr["type"] = str(obj.type)
            if obj.meta is not None:
                attr["meta"] = str(obj.meta)
            elem = ET.Element("object", attrib=attr)
            objects_elem.append(elem)
        root.append(objects_elem)

        layers_elem = ET.Element("layers")
        for layer in self.layers:
            attr = {"columns": str(layer.columns)}
            if layer.type is not None:
                attr["type"] = str(layer.type)
            if layer.meta is not None:
                attr["meta"] = str(layer.meta)
            elem = ET.Element("layer", attrib=attr)
            elem.text = data_encode(layer.tiles)
            layers_elem.append(elem)
        root.append(layers_elem)

        tree = ET.ElementTree(root)
        tree.write(f, encoding="UTF-8", xml_declaration=True)


class TMX:
    """
    A class for reading (but not writing) TMX files created by the Tiled
    Map Editor in a generic manner.

    Only map meta-data, basic tile layers (but not group layers or image
    layers), and object groups are captured.  Captured meta-data is
    converted to numeric form whenever it is supposed to be.  All other
    values are left as strings.

    Saving in this format is not supported due to its complexity.

    See the TMX format specification for more information on the format
    itself:

    https://doc.mapeditor.org/en/stable/reference/tmx-map-format/

    .. attribute:: meta

       A dictionary of level meta variables obtained from the TMX.  The
       following meta variables are captured if available:

       - "orientation" (from the <map> tag)
       - "dictionary" (from the <map> tag)
       - "width" (from the <map> tag)
       - "height" (from the <map> tag)
       - "tilewidth" (from the <map> tag)
       - "tileheight" (from the <map> tag)
       - "backgroundcolor" (from the <map> tag)
       - All custom map properties

    .. attribute:: objects

       A list of objects in the level as :class:`LevelObject`
       objects.  These are taken from the TMX object tags. Layering of
       objects is not preserved.  Each :class:`LevelObject` object's
       type becomes, in order of preference: the name of the TMX object,
       the type of the TMX object, or the name of the TMX object group.
       Each :class:`LevelObject` object's meta variable is set as a
       dictionary of values obtained from the TMX.  The following meta
       variables are captured if available:

       - "color" (from the <objectgroup> tag)
       - "opacity" (from the <objectgroup> tag)
       - "offsetx" (from the <objectgroup> tag)
       - "offsety" (from the <objectgroup> tag)
       - "x" (from the <object> tag)
       - "y" (from the <object> tag)
       - "width" (from the <object> tag)
       - "height" (from the <object> tag)
       - "rotation" (from the <object> tag)
       - "gid" (from the <object> tag)
       - "visible" (from the <object> tag)
       - All custom object properties

       .. note::

          Remember that a tile object's origin is in the bottom-center,
          unlike shape-based objects whose origin is in the top-left.
          You can find out if an object is a tile object by checking the
          respective level object's ``meta["gid"]`` after loading.  If
          this value is not ``None``, the object is a tile object.

    .. attribute:: layers

       A list oj :class:`TileLayer` objects representing the tile layers
       of the level.  These are taken from the TMX layer tags.  Tile
       flipping and rotation are not supported; attempts to flip or
       rotate tiles will simply be interpreted as completely different
       tiles.

       Tile IDs are also localized so that a tile ID of 1 is the
       first tile of the tileset, 2 is the second, and so on.
       For means of simplification and consistency, only one tileset can
       be used per layer and all tile global IDs will be localized based
       on the tile IDs contained within.

       Each :class:`TileLayer` object's type becomes the name of the TMX
       layer.  Each :class:`TileLayer` object's meta variable is set as
       a dictionary of values obtained from the TMX.  The following meta
       variables are captured if available:

       - "width" (from the <layer> tag)
       - "height" (from the <layer> tag)
       - "opacity" (from the <layer> tag)
       - "visible" (from the <layer> tag)
       - "offsetx" (from the <layer> tag)
       - "offsety" (from the <layer> tag)
       - All custom layer properties
    """
    def __init__(self):
        self.meta = {}
        self.objects = []
        self.layers = []

    @classmethod
    def load(cls, f):
        """
        Load the indicated file and return a :class:`TMX` object.
        """
        self = cls()

        tree = ET.parse(f)
        root = tree.getroot()

        def clean_dict(d):
            new_d = {}
            for i in d:
                if d[i] is not None:
                    new_d[i] = d[i]
            return new_d

        def get_properties(elem):
            properties = {}
            for prop in elem.findall("property"):
                name = prop.attrib.get("name")
                type_ = prop.attrib.get("type")
                value = prop.attrib.get("value")
                if value is not None:
                    if type_ == "int":
                        value = int(value)
                    elif type_ == "float":
                        value = float(value)
                    elif type_ == "bool":
                        value = (value == "true")
                properties[name] = value
            return properties

        maporientation = root.attrib.get("orientation")
        maprenderorder = root.attrib.get("renderorder")
        mapwidth = int(root.attrib.get("width", 1))
        mapheight = int(root.attrib.get("height", 1))
        maptilewidth = int(root.attrib.get("tilewidth", 16))
        maptileheight = int(root.attrib.get("tileheight", 16))
        mapbackgroundcolor = root.attrib.get("backgroundcolor")

        self.meta = clean_dict({
            "orientation": maporientation, "renderorder": maprenderorder,
            "width": mapwidth, "height": mapheight, "tilewidth": maptilewidth,
            "tileheight": maptileheight, "backgroundcolor": mapbackgroundcolor,
        })

        # Check tilesets for fristgid
        firstgids = []
        for tileset in root.findall("tileset"):
            firstgids.append(int(tileset.attrib.get("firstgid", 1)))
        firstgids.sort()

        for child in root:
            if child.tag == "properties":
                self.meta.update(get_properties(child))

            elif child.tag == "layer":
                data = None
                encoding = None
                compression = None
                for lchild in child:
                    if lchild.tag == "data":
                        data = lchild.text
                        encoding = lchild.attrib.get("encoding")
                        compression = lchild.attrib.get("compression")
                        break

                if data is not None and encoding is not None:
                    name = child.attrib.get("name")
                    width = int(child.attrib.get("width", mapwidth))
                    height = int(child.attrib.get("height", mapheight))
                    opacity = child.attrib.get("opacity")
                    if opacity is not None:
                        opacity = float(opacity)
                    visible = child.attrib.get("visible")
                    if visible is not None:
                        visible = bool(int(visible))
                    offsetx = child.attrib.get("offsetx")
                    if offsetx is not None:
                        offsetx = int(offsetx)
                    offsety = child.attrib.get("offsety")
                    if offsety is not None:
                        offsety = int(offsety)
                    tiles = data_decode(data, encoding, compression)

                    # Clean up tile ID, make it local
                    highest = max(tiles)
                    diff = 0
                    for firstgid in firstgids:
                        if firstgid < highest:
                            diff = firstgid - 1
                        else:
                            break
                    for i in range(len(tiles)):
                        tiles[i] = max(0, tiles[i] - diff)

                    meta = clean_dict({
                        "width": width, "height": height, "opacity": opacity,
                        "visible": visible, "offsetx": offsetx,
                        "offsety": offsety})
                    self.layers.append(TileLayer(name, width, tiles, meta))

            elif child.tag == "objectgroup":
                gname = child.attrib.get("name")
                color = child.attrib.get("color")
                opacity = child.attrib.get("opacity")
                if opacity is not None:
                    opacity = float(opacity)
                offsetx = child.attrib.get("offsetx")
                if offsetx is not None:
                    offsetx = int(offsetx)
                offsety = child.attrib.get("offsety")
                if offsety is not None:
                    offsety = int(offsety)

                for ochild in child:
                    if ochild.tag == "object":
                        name = child.attrib.get("name")
                        type_ = child.attrib.get("type")
                        otype = name or type_ or gname
                        x = int(ochild.attrib.get("x", 0))
                        y = int(ochild.attrib.get("y", 0))
                        width = ochild.attrib.get("width")
                        if width is not None:
                            width = int(width)
                        height = ochild.attrib.get("height")
                        if height is not None:
                            height = int(height)
                        rotation = ochild.attrib.get("rotation")
                        if rotation is not None:
                            rotation = float(rotation)
                        gid = ochild.attrib.get("gid")
                        if gid is not None:
                            gid = int(gid)
                        visible = ochild.attrib.get("visible")
                        if visible is not None:
                            visible = bool(int(visible))
                        meta = clean_dict({
                            "color": color, "opacity": opacity,
                            "offsetx": offsetx, "offsety": offsety, "x": x,
                            "y": y, "width": width, "height": height,
                            "rotation": rotation, "gid": gid,
                            "visible": visible})

                        for pchild in ochild:
                            if pchild.tag == "properties":
                                meta.update(get_properties(pchild))

                        self.objects.append(LevelObject(otype, meta))

        return self


def data_decode(data, encoding="base64", compression="zlib"):
    """
    Decode encoded data and return a list of integers it represents.

    This is a low-level function used internally by this library; you
    don't typically need to use it.

    Arguments:

    - ``data`` -- The data to decode.
    - ``encoding`` -- The encoding of the data.  Can be ``"base64"`` or
      ``"csv"``.
    - ``compression`` -- The compression method used.  Valid compression
      methods are ``"gzip"`` and ``"zlib"``.  Set to ``None`` for no
      compression.
    """
    if encoding == "csv":
        return [int(i) for i in data.strip().split(",")]
    elif encoding == "base64":
        data = base64.b64decode(data.strip().encode("latin1"))

        if compression == "gzip":
            data = gzip.decompress(data)
        elif compression == "zlib":
            data = zlib.decompress(data)
        elif compression:
            e = 'Compression type "{}" not supported.'.format(compression)
            raise ValueError(e)

        ndata = [i for i in data]

        data = []
        for i in range(0, len(ndata), 4):
            n = (ndata[i]  + ndata[i + 1] * (2 ** 8) +
                 ndata[i + 2] * (2 ** 16) + ndata[i + 3] * (2 ** 24))
            data.append(n)

        return data
    else:
        e = 'Encoding type "{}" not supported.'.format(encoding)
        raise ValueError(e)


def data_encode(data):
    """
    Return list of integers ``data`` as a string containing
    zlib-compressed base64 encoded data.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    ndata = []
    for i in data:
        n = [i % (2 ** 8), i // (2 ** 8), i // (2 ** 16), i // (2 ** 24)]
        ndata.extend(n)

    data = b''.join([bytes((i,)) for i in ndata])
    data = zlib.compress(data)

    return base64.b64encode(data).decode("latin1")
