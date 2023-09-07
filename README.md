# VirtualDesktopDumper

Kudos to [@NyaMisty](https://github.com/NyaMisty) for the original solution: [GetVirtualDesktopAPI_DIA](https://github.com/NyaMisty/GetVirtualDesktopAPI_DIA)

## How does it work

Uses the Microsoft MSDIA interface to parse PDBs and retrieve the corresponding symbols.

## How to use it

1. Install dependencies from `requirements.txt`: `pip install -r requirements.txt`
2. Make sure [VCRedist 2005 x64](https://www.microsoft.com/en-US/download/details.aspx?id=26347) is installed to have `msdia80.dll`.
3. Locate your `msdia80.dll`. For me, it's located at: `C:\Program Files (x86)\Common Files\Microsoft Shared\VC\amd64\msdia80.dll`. If your path is different, update the `PATH_MSDIA` variable in `src\components\PEFile.py` with your specific path.
4. Register `msdia80.dll` by opening cmd as an administrator and executing: `regsvr32 "<your_path_to_msdia_dll>"`
5. For each Windows release, there is a `.py` script in the `src` folder that can be executed to create a new dump for that specific release. If a dumper script is not available for your Windows build, you can use the `Test.ipynb` Jupyter notebook to extract the Virtual Desktop API for that version. You should run these scripts with the project root as the current working directory to ensure the imports work correctly.

## Dumps

For recent Windows 11 releases, you can find the dumped Virtual Desktop API vftables and GUIDs in the `dumps` folder.
