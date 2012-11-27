# portalocker.py - Cross-platform (posix/nt) API for flock-style file locking.
#                  Requires python 1.5.2 or better.

"""Cross-platform (posix/nt) API for flock-style file locking.

Synopsis::

   import portalocker
   file = open("somefile", "r+")
   portalocker.lock(file, portalocker.LOCK_EX)
   file.seek(12)
   file.write("foo")
   file.close()

If you know what you're doing, you may choose to::

   portalocker.unlock(file)

before closing the file, but why?

Methods::

   lock( file, flags )
   unlock( file )

Constants::

   LOCK_EX
   LOCK_SH
   LOCK_NB

I learned the win32 technique for locking files from sample code
provided by John Nielsen <nielsenjf@my-deja.com> in the documentation
that accompanies the win32 modules.

:Author: Jonathan Feinberg <jdf@pobox.com>
:Version: Id: portalocker.py,v 1.3 2001/05/29 18:47:55 Administrator Exp 
          **un-cvsified by richard so the version doesn't change**
"""
__docformat__ = 'restructuredtext'

import os

if os.name == 'nt':
    import win32file
    import pywintypes
    import msvcrt
    LOCK_SH = 0    # the default
    LOCK_NB = 0x1  # LOCKFILE_FAIL_IMMEDIATELY
    LOCK_EX = 0x2  # LOCKFILE_EXCLUSIVE_LOCK
    # is there any reason not to reuse the following structure?
    __overlapped = pywintypes.OVERLAPPED()
elif os.name == 'posix':
    import fcntl
    LOCK_SH = fcntl.LOCK_SH  # shared lock
    LOCK_NB = fcntl.LOCK_NB  # non-blocking
    LOCK_EX = fcntl.LOCK_EX
else:
    raise RuntimeError("PortaLocker only defined for nt and posix platforms")

if os.name == 'nt':
    def lock(file, flags):
        hfile = msvcrt.get_osfhandle(file.fileno())
        # LockFileEx is not supported on all Win32 platforms (Win95, Win98,
        # WinME).
        # If it's not supported, win32file will raise an exception.
        # Try LockFileEx first, as it has more functionality and handles
        # blocking locks more efficiently.
        try:
            win32file.LockFileEx(hfile, flags, 0, 0xFFFF0000, __overlapped)
        except win32file.error, e:
            import winerror
            # Propagate upwards all exceptions other than not-implemented.
            if e[0] != winerror.ERROR_CALL_NOT_IMPLEMENTED:
                raise e
            
            # LockFileEx is not supported. Use LockFile.
            # LockFile does not support shared locking -- always exclusive.
            # Care: the low/high length params are reversed compared to
            # LockFileEx.
            if not flags & LOCK_EX:
                import warnings
                warnings.warn("PortaLocker does not support shared "
                    "locking on Win9x", RuntimeWarning)
            # LockFile only supports immediate-fail locking.
            if flags & LOCK_NB:
                win32file.LockFile(hfile, 0, 0, 0xFFFF0000, 0)
            else:
                # Emulate a blocking lock with a polling loop.
                import time
                while 1:
                    # Attempt a lock.
                    try:
                        win32file.LockFile(hfile, 0, 0, 0xFFFF0000, 0)
                        break
                    except win32file.error, e:
                        # Propagate upwards all exceptions other than lock
                        # violation.
                        if e[0] != winerror.ERROR_LOCK_VIOLATION:
                            raise e
                    # Sleep and poll again.
                    time.sleep(0.1)
        # TODO: should this return the result of the lock?
                    
    def unlock(file):
        hfile = msvcrt.get_osfhandle(file.fileno())
        # UnlockFileEx is not supported on all Win32 platforms (Win95, Win98,
        # WinME).
        # If it's not supported, win32file will raise an api_error exception.
        try:
            win32file.UnlockFileEx(hfile, 0, 0xFFFF0000, __overlapped)
        except win32file.error, e:
            import winerror
            # Propagate upwards all exceptions other than not-implemented.
            if e[0] != winerror.ERROR_CALL_NOT_IMPLEMENTED:
                raise e
            
            # UnlockFileEx is not supported. Use UnlockFile.
            # Care: the low/high length params are reversed compared to
            # UnLockFileEx.
            win32file.UnlockFile(hfile, 0, 0, 0xFFFF0000, 0)

elif os.name =='posix':
    def lock(file, flags):
        fcntl.flock(file.fileno(), flags)
        # TODO: should this return the result of the lock?

    def unlock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

if __name__ == '__main__':
    from time import time, strftime, localtime
    import sys

    log = open('log.txt', "a+")
    lock(log, LOCK_EX)

    timestamp = strftime("%m/%d/%Y %H:%M:%S\n", localtime(time()))
    log.write( timestamp )

    print "Wrote lines. Hit enter to release lock."
    dummy = sys.stdin.readline()

    log.close()

