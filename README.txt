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
  - Core file which manages the build creation for Streama. Please find the pseudo code below for the functional flow.
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
  
  
