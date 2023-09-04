UDT_ENUM_TO_STR = ('struct', 'class', 'union', 'interface')


class PDBSymbol:

    @staticmethod
    def from_dia(pe, symbol_data):
        return PDBSymbol(
            pe,
            UDT_ENUM_TO_STR[symbol_data.udtKind],
            symbol_data.name,
            symbol_data.undecoratedName,
            symbol_data.virtualAddress,
            symbol_data.length
        )

    def __init__(self, pe, kind='', name='', und_name='', rva=0, size=0):
        self.pe = pe
        self.kind = kind
        self.name = name
        self.und_name = und_name
        self.rva = rva
        self.size = size

    def __str__(self):
        return '0x%08x (%4dB) %s\t%s' % (self.rva, self.size, self.kind, self.name)

    def __repr__(self):
        return f'<PDBSymbol {str(self)}>'

    # required for hash
    def __hash__(self):
        return hash((self.name, self.rva, self.kind))

    # required for hash, when buckets contain multiple items
    def __eq__(self, other):
        return self.name == other.name and self.rva == other.rva and self.kind == other.kind

    def __contains__(self, key):
        return self.__eq__(key)

    def read_data(self, length=None):
        if length is None:
            length = self.size

        return self.pe.get_data(self.rva, length)