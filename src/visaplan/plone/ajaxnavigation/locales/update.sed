# textual --> numeric timezones
s,^\("PO.*-Date: [-0-0]\+ [:0-9]\+\)Mitteleuropäische Sommerzeit\(\\n"\)$,\1+0200\2,
s,^\("PO.*-Date: [-0-0]\+ [:0-9]\+\)Mitteleuropäische Zeit\(\\n"\)$,\1+0100\2,
