import os
from datetime import datetime
from enum import Enum

PATH_DIR_SOURCE = os.path.dirname(os.path.abspath(__file__))
PATH_DIR_DUMPS = os.path.join(PATH_DIR_SOURCE, '../..', 'dumps')


class Dumper:
    class Output(Enum):
        CONSOLE = 'CONSOLE'
        FILE = 'FILE'

    def __init__(self, output, name, pe_files):
        self.output = output
        self.name = name
        self.file_path = os.path.join(PATH_DIR_DUMPS, name + '.txt')
        self.pe_files = pe_files
        self.symbol_map = self._get_symbol_map()

    def guid(self, sym_name):
        guid = self.symbol_map[sym_name].read_data()

        lines = [
            "%s: %s" % (sym_name, self._guid_to_str(guid))
        ]

        self._flush_output(lines)

    def description(self):
        now = datetime.now()
        date_string = now.strftime("%d/%m/%Y %H:%M:%S")

        self._flush_output([
            "[%s] Virtual Desktop API dump - %s\n" % (date_string, self.name)
        ])

    def vftable(self, name, sym_name):
        vft_sym = self.symbol_map[sym_name]
        vft_data = vft_sym.read_data()
        vft_ptrs = [
            int.from_bytes(vft_data[c:c + 8], 'little') - vft_sym.pe.OPTIONAL_HEADER.ImageBase
            for c in range(0, len(vft_data), 8)
        ]
        sym_rva_map = {c.rva: c for c in vft_sym.pe.symbols}

        lines = []

        lines.append("\n[%s] %s" % (name, vft_sym.und_name))

        for i, ptr in enumerate(vft_ptrs):
            if ptr in sym_rva_map:
                lines.append("    Method %2d: %s (%s)" % (i, sym_rva_map[ptr].und_name, sym_rva_map[ptr].name))
            else:
                lines.append("    Method %2d: Unknown (0x%X)" % (i, ptr))

        self._flush_output(lines)

    def _guid_to_str(self, guid):
        return '%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X' % (
            int.from_bytes(guid[:4], 'little'),
            int.from_bytes(guid[4:6], 'little'),
            int.from_bytes(guid[6:8], 'little'),
            *[int.from_bytes(guid[i:i + 1], 'little') for i in range(8, 16)]
        )

    def _flush_output(self, lines):
        if self.output == Dumper.Output.FILE:
            with open(self.file_path, 'a') as f:
                f.write('\n'.join(lines))

        elif self.output == Dumper.Output.CONSOLE:
            print('\n'.join(lines))

        else:
            raise Exception("Unknown Dumper output type: %s" % self.output)

    def _get_symbol_map(self):
        all_symbols = []

        for pe in self.pe_files:
            all_symbols = all_symbols + pe.symbols

        return {c.name: c for c in all_symbols}
