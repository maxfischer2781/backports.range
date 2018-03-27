cdef class llrange_iterator(object):
    cdef long long _start
    cdef long long _step
    cdef long long _max_idx
    cdef long long _current
