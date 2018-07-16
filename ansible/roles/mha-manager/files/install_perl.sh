#!/bin/bash
#
perl_pkgs=(
wget
perl-Class-Load
perl-Config-Tiny
perl-DBD-MySQL
perl-DBI
perl-Data
perl-Email-Date-Format
perl-List-MoreUtils
perl-Log-Dispatch
perl-MIME-Lite
perl-MIME-Types
perl-Mail-Sender
perl-Mail-Sendmail
perl-MailTools
perl-Module-Implementation
perl-Module-Runtime
perl-Net-Daemon
perl-Net-SMTP-SSL
perl-Package-DeprecationManager
perl-Package-Stash
perl-Package-Stash-XS
perl-Parallel-ForkManager
perl-Params-Util
perl-Params-Validate
perl-PlRPC
perl-Sub-Install
perl-Try-Tiny
)

for perl in `seq 0 26`
do
	yum install -y ${perl_pkgs[$perl]}
done
