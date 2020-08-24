#!/usr/bin/env python
from ctypes.util import find_library

from cffi import FFI

# We need to build the gpg_error library first
gerror_ffi = FFI()
gerror_ffi.set_source("pygcrypt._gerror", r"""
        #include <gpg-error.h>
        """,
        libraries=['gpg-error'])

gerror_ffi.cdef("""
        /* The error source type gpg_err_source_t. */
        typedef enum { ... } gpg_err_source_t;

        /* The error code type gpg_err_code_t.  */
        typedef enum { ... } gpg_err_code_t;

        /* The error value type gpg_error_t.  */
        typedef unsigned int gpg_error_t;
        """)

gerror_ffi.cdef("""
        /* Initialization function.  */

        /* Initialize the library.  This function should be run early.  */
        gpg_error_t gpg_err_init (void);

        /* See the source on how to use the deinit function; it is usually not
           required.  */
        void gpg_err_deinit (int mode);

        /* Register blocking system I/O clamping functions.  */
        void gpgrt_set_syscall_clamp (void (*pre)(void), void (*post)(void));

        /* Register a custom malloc/realloc/free function.  */
        void gpgrt_set_alloc_func  (void *(*f)(void *a, size_t n));
        """)

gerror_ffi.cdef("""
        /* String functions.  */

        /* Return a pointer to a string containing a description of the error
           code in the error value ERR.  This function is not thread-safe.  */
        const char *gpg_strerror (gpg_error_t err);

        /* Return the error string for ERR in the user-supplied buffer BUF of
           size BUFLEN.  This function is, in contrast to gpg_strerror,
           thread-safe if a thread-safe strerror_r() function is provided by
           the system.  If the function succeeds, 0 is returned and BUF
           contains the string describing the error.  If the buffer was not
           large enough, ERANGE is returned and BUF contains as much of the
           beginning of the error string as fits into the buffer.  */
        int gpg_strerror_r (gpg_error_t err, char *buf, size_t buflen);

        /* Return a pointer to a string containing a description of the error
           source in the error value ERR.  */
        const char *gpg_strsource (gpg_error_t err);
        """)

gerror_ffi.cdef("""
        /* Mapping of system errors (errno).  */

        /* Retrieve the error code for the system error ERR.  This returns
           GPG_ERR_UNKNOWN_ERRNO if the system error is not mapped (report
           this). */
        gpg_err_code_t gpg_err_code_from_errno (int err);


        /* Retrieve the system error for the error code CODE.  This returns 0
           if CODE is not a system error code.  */
        int gpg_err_code_to_errno (gpg_err_code_t code);


        /* Retrieve the error code directly from the ERRNO variable.  This
           returns GPG_ERR_UNKNOWN_ERRNO if the system error is not mapped
           (report this) and GPG_ERR_MISSING_ERRNO if ERRNO has the value 0. */
        gpg_err_code_t gpg_err_code_from_syserror (void);


        /* Set the ERRNO variable.  This function is the preferred way to set
           ERRNO due to peculiarities on WindowsCE.  */
        void gpg_err_set_errno (int err);

        /* Return or check the version.  Both functions are identical.  */
        const char *gpgrt_check_version (const char *req_version);
        const char *gpg_error_check_version (const char *req_version);

        """)

gerror_ffi.cdef("""
        /* Thread functions.  */

        gpg_err_code_t gpgrt_yield (void);
        """)

gerror_ffi.compile()
