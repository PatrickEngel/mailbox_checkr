from distutils.core import setup
import py2exe


gtk_dir = "C:\\Programme\GTK2-Runtime"


setup(
    name = 'mbox_checkr',
    description = 'mbox checkr - a mail watchdog',
    version = '1.0',

    windows = [
                  {
                      'script': 'mbox_checkr.py'
                      # 'icon_resources': [(1, "mboxcheckr.ico")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject',
                  }
              },

    data_files=[
                   'readme.txt',
                   'mailbox.cfg',
				   ("etc\\gtk-2.0", ["%s\\etc\\gtk-2.0\\gdk-pixbuf.loaders" % gtk_dir]),
				   # copy \\lib\\gtk-2.0\\2.10.0\\loadersgdk-pixbuf.loaders
				   #("lib\\gtk-2.0\\2.10.0\\loaders", ["%s\\lib\\gtk-2.0\\2.10.0\\loadersgdk-pixbuf.loaders" % gtk_dir])
	   
               ]
)