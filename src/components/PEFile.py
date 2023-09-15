import os
import pefile
import requests
import comtypes
import comtypes.client

PATH_DIR_SOURCE = os.path.dirname(os.path.abspath(__file__))
PATH_DIR_PDB = os.path.join(PATH_DIR_SOURCE, '../..', 'pdb')
PATH_MSDIA = r'C:\Program Files (x86)\Common Files\Microsoft Shared\VC\amd64\msdia80.dll'
URL_SYMBOLS_SERVER = 'https://msdl.microsoft.com/download/symbols'

# this has to be before the import that follows
msdia = comtypes.client.GetModule(PATH_MSDIA)

from comtypes.gen.Dia2Lib import *
from PDBSymbol import PDBSymbol


class PEFile(pefile.PE):
    @staticmethod
    def create_dia():
        try:
            return comtypes.client.CreateObject(msdia.DiaSource)
        except Exception as exc:
            print(f'Failed creating DIA object, try to run as administrator: "regsvr32 {PATH_MSDIA}"')
            raise exc

    def __init__(self, path):
        pefile.PE.__init__(self, path)

        self.path = path
        self.version = self._get_version()

        pdb_url, pdb_filename = self._get_pdb_url()

        self.pdb_url = pdb_url
        self.pdb_filename = pdb_filename
        self.pdb_path = os.path.realpath(os.path.join(PATH_DIR_PDB, pdb_filename))
        self.pdb_obj = self._get_pdb()
        self.symbols = self._get_symbols()

    def _get_pdb(self):
        pdb_path = self.pdb_path
        pdb_url = self.pdb_url

        # download pdb file
        if not os.path.exists(pdb_path) or os.path.getsize(pdb_path) == 0:
            response = requests.get(pdb_url)

            if response.status_code != 200:
                print(f'Failed to download pdb file (status: {response.status_code}): {pdb_url}')
                raise

            with open(pdb_path, 'wb') as f:
                f.write(response.content)

        try:
            dia = PEFile.create_dia()
            dia.loadDataFromPdb(pdb_path)
            return dia.openSession()
        except Exception as exc:
            print(f'Failed to load pdb file: {str(exc)}')
            raise

    def _get_symbols(self):
        pe = self
        pdb_obj = self.pdb_obj
        symbols = set()

        # iterate the public syms to find all vtables
        for symbol in pdb_obj.globalScope.findChildren(SymTagPublicSymbol, None, 0):
            symbol_data = symbol.QueryInterface(IDiaSymbol)
            symbols.add(
                PDBSymbol.from_dia(pe, symbol_data)
            )

        # iterate all UDT/private? symbols
        for symbol in pdb_obj.globalScope.findChildren(SymTagUDT, None, 0):
            symbol_data = symbol.QueryInterface(IDiaSymbol)
            symbols.add(
                PDBSymbol.from_dia(pe, symbol_data)
            )

        return list(symbols)

    def _get_version(self):
        string_version_info = {}

        for fileinfo in self.FileInfo[0]:
            if fileinfo.Key.decode() == 'StringFileInfo':
                for st in fileinfo.StringTable:
                    for entry in st.entries.items():
                        string_version_info[entry[0].decode()] = entry[1].decode()

        return string_version_info['ProductVersion']

    def _get_pdb_url(self):
        for directory in self.DIRECTORY_ENTRY_DEBUG:
            debug_entry = directory.entry

            if hasattr(debug_entry, 'PdbFileName'):
                pdb_file = debug_entry.PdbFileName[:-1].decode('ascii')
                pdb_filename = f'{pdb_file[:-4]}-{self.version}.pdb'
                url = f'{URL_SYMBOLS_SERVER}/{pdb_file}/{debug_entry.Signature_String}/{pdb_file}'
                return url, pdb_filename

        return None
