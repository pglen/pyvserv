# PyvServ commands

 The command structure resembles mainstream servers like FTP, HTTP. The command
to the server starts with the command name and followed by arguments. After
the 'session' command is issued, everything is transmitted / received encrypted.

## The following commands may be issued.

    user logon_name                 -- Name of user to log in with
    akey                            -- Get asymmetric key
    pass logon_pass                 -- Password
    chpass newpass                  -- Change pass (not tested)
    file fname                      -- Specify name for upload
    fget fname                      -- Download (get) file
    fput fname                      -- Upload (put) file
    del  fname                      -- Delete file
    uadd user_name user_pass        -- Create new user
    kadd key_name key_val           -- Add new encryption key
    uini user_name user_pass        -- Create initial user. Must be from local net.
    kini key_name key_pass          -- Create initial key.  Must be from local net.
    uena user_name  flag            -- Enable / disable user
    aadd user_name user_pass        -- Create admin user
    udel user_name                  -- Delete user
    data datalen                    -- Specify length of file to follow
    ver                             -- Get protocol version. alias: vers
    id                              -- Get site id string
    hello                           -- Say Hello - test connectivity.
    quit                            -- Terminate connection. alias: exit
    help [command]                  -- Offer help on command
    ls [dir]                        -- List files in dir
    lsd [dir]                       -- List dirs in dir
    cd dir                          -- Change to dir. Capped to server root
    pwd                             -- Show current dir
    stat fname                      -- Get file stat. See at the end of this table.
    tout new_val                    -- Set / Reset timeout in seconds
    ekey encryption_key             -- Set encryption key
    sess session data               -- Start session
    buff buff_size                  -- Limited to 64k
    rput header, field1, field2...  -- Put record in blockcain. See example code.
    rget header                     -- Get record from blockcain.
    qr                              -- Get qrcode image for 2fa
    twofa                           -- Two factor authentication
    dmode                           -- Get dmode (Developer Mode) flag
    ihave                           -- The 'i have you have' protocol entry point
    ihost                           -- Add / delete replicator host

    Stat format:

      1.  ST_MODE Inode protection mode.
      2.  ST_INO Inode number.
      3.  ST_DEV Device inode resides on.
      4.  ST_NLINK  Number of links to the inode.
      5.  ST_UID User id of the owner.
      6.  ST_GID Group id of the owner.
      7.  ST_SIZE Size in bytes of a plain file.
      8.  ST_ATIME Time of last access.
      9.  ST_MTIME Time of last modification.
      10. ST_CTIME Time of last metadata change.

More commands are added. This document represents the last release version's
commands. For the latest set of commands, type 'help' on the client's cli prompt.

// EOF