cdef class range(object):
    cdef readonly long long start
    cdef readonly long long stop
    cdef readonly long long step
    cdef readonly long long _len
    cdef readonly bint _bool
