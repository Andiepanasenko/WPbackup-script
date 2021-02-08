#!/usr/bin/perl
#
# update_hosts.pl script reads compute,rds or cache aws records from the define.php file and
# obtains their IP addresses using DIG and populates /etc/hosts file with these records
#
############################################################################################
use strict;
use warnings;
use File::Temp qw(tempfile);
use File::Copy qw(copy);
#use Data::Dumper;

my $hosts_file = '/etc/hosts';
my $define = '/var/www/pdffiller/include/define.php';
my %host_hash;

open(my $fh, '<', $define)
  or die "Could not open file '$define' $!";

while (my $row = <$fh>) {
  chomp $row;
  if (index($row, "//") == -1 && $row =~ /.*define\(.(.*).\s*\,\s*.(.*(compute|cache|rds).*\.amazonaws\.com).\);/){
      my $host_ip = `dig $2 +short | tail -1`;
      chomp $host_ip;
      if (exists($host_hash{$host_ip})){
           if(index($host_hash{$host_ip}, $2) == -1) {
              $host_hash{$host_ip} .= "$2 ";
           }
     }else{
           $host_hash{$host_ip}="$2 ";
     }
  }
}

close($fh);

my $hash_size = keys %host_hash;
if ($hash_size == 0){
   print "No AWS DNS records found";
   exit 0;
}

open(my $hfile, '<', $hosts_file)
  or die "Could not open file '$hosts_file' $!";
(my $hfile_tmp, my $filename) = tempfile(UNLINK => 1);

my $skip_flag = "false";

while(<$hfile>) {
  $skip_flag="true"  if ( $_ =~ /(.*)#AWS_DNS_START(.*)/ );
  if ( $_ =~ /(.*)#AWS_DNS_END(.*)/ ){
     $skip_flag="false";
     next;
  }
  print $hfile_tmp $_ if $skip_flag eq "false";
}

print $hfile_tmp "#AWS_DNS_START\n";
for my $ip_host (keys %host_hash) {
  print $hfile_tmp "$ip_host $host_hash{$ip_host}\n";
}
print $hfile_tmp "#AWS_DNS_END\n";

close($hfile);
close($hfile_tmp);

copy $hosts_file, "$hosts_file.oldhosts";
copy $filename, $hosts_file;
#print Dumper(\%host_hash);
