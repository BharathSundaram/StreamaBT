Software requirement:
---------------------
Python3 and bash is the required to run this package.

# StreamaBT
Auto the build process for the  Streama project
├── build.sh
├── ftp_config.cfg
├── pythonsrc
│   ├── main.py
│   └── utils.py
├── rd-next-commands.txt
└── recipes.txt
Above is the tree view excluding the misc folder as it is relevant to this project developers.
==============================================================================================

build.sh:
---------
  - Core file which manages the build creation for Streama. Please find the pseudo code below for the functional flow. Please see usage function for the usage
    Check for disk size availablity, exit if size not available
    while read command; do
      execute command
      if line has bitbake
        mark = 1
      fi
      
      if excuetion of command failure for bitbake image
        handle error for the bitbake recipe for 5 trial
      fi
      
      if success for handle errors or bitbake image
        tar the image
        ftp upload 
      fi
    done while
    
 ftp_config.cfg
 --------------
  - it contains ftp server, username, password. *** For security reason the values are not stored as this project is hosted in public.

recipes.txt:
------------
  - recipe list generated using the command "bitbake-layers show-recipes" redirected to a file to compare the failure from bitbake image

pythonsrc --> main.py
----------------------
  - Build.sh call this python source to generate the bitbake cleanall commands for the failed recipe in to a file handle_errors.sh. This file is used by build.sh
 as part of handle errors.

pythonsrc --> utils.py
-----------------------
  - support file for main.py

rd-next-commands.txt
--------------------
  - Example file of input file
