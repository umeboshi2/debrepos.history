#
# Regular cron jobs for the debrepos package
#
0 4	* * *	root	[ -x /usr/bin/debrepos_maintenance ] && /usr/bin/debrepos_maintenance
