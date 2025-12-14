import sys
from fat32.cli.main import main as cli_main
from fat32.gui.app import FatGui

if __name__ == "__main__":
    if "--gui" in sys.argv:
        app = FatGui()
        app.mainloop()
    else:
        cli_main()
