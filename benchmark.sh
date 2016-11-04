#!/usr/bin/env bash
interpreter=${1:-"python"}
echo "Benchmarking '[ a for a in range(...)]'"
for max_exp in 16 31 37
do
    for length_exp in 4 8 16
    do
        echo -e ">>> [a for a in range(max-count, max)] <<< max: 2**${max_exp} == $(( 2 ** ${max_exp} )) \tcount: 2**${length_exp}  == $(( 2 ** ${length_exp} ))\t"
        echo -n "backports  "
        ${interpreter} -m timeit -s 'from backports.range import range' -s "range_obj = range(2**${max_exp}-2**${length_exp}, 2**${max_exp})" 'a = [ b for b in range_obj]' 2>/dev/null
        echo -n "builtins   "
        ${interpreter} -m timeit -s "range_obj = range(2**${max_exp}-2**${length_exp}, 2**${max_exp})" 'a = [ b for b in range_obj]' 2>/dev/null
        ${interpreter} -c 'import sys;sys.exit(not hasattr(__builtins__, "xrange"))' 2>/dev/null
        if [[ $? -eq 0 ]]
        then
            echo -n "\> xrange  "
            ${interpreter} -m timeit "a = [ b for b in xrange(2**${max_exp}-2**${length_exp}, 2**${max_exp})]" 2>/dev/null
        fi
    done
done
echo "Benchmarking 'a in range(...)'"
for max_exp in 16 31 37
do
    for length_exp in 4 8 16
    do
        echo -e ">>> max/2 - count in range(max-count, max) <<< max: 2**${max_exp} == $(( 2 ** ${max_exp} )) \tcount: 2**${length_exp}  == $(( 2 ** ${length_exp} ))\t"
        echo -n "backports  "
        ${interpreter} -m timeit -s "b = 2**(${max_exp}-1)-2**${length_exp}" -s 'from backports.range import range' -s "range_obj = range(2**${max_exp}-2**${length_exp}, 2**${max_exp})" 'a = b in range_obj' 2>/dev/null
        echo -n "builtins   "
        ${interpreter} -m timeit -s "b = 2**(${max_exp}-1)-2**${length_exp}" -s "range_obj = range(2**${max_exp}-2**${length_exp}, 2**${max_exp})" 'a = b in range_obj' 2>/dev/null
        ${interpreter} -c 'import sys;sys.exit(not hasattr(__builtins__, "xrange"))' 2>/dev/null
        if [[ $? -eq 0 ]]
        then
            echo -n "\> xrange  "
            ${interpreter} -m timeit -s "b = 2**(${max_exp}-1)-2**${length_exp}" "a = b in xrange(2**${max_exp}-2**${length_exp}, 2**${max_exp})" 2>/dev/null
        fi
    done
done
