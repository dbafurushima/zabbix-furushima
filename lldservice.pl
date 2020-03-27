#!/usr/bin/perl
$output = `which ss` ? `ss -nltp sport gt :1 and sport le :9000 | tail -n +2` : `netstat -nltp | awk -F'[[:space:]]+|:' 'NR>2 && $5>=1 && $5<=9000' | tail -n +3`;
#$output = `which ss` ? `ss -nltp |egrep -iv "Xvnc"| tail -n +2` : `netstat -nltp |egrep -iv "Xvnc"| tail -n +3`;
for ( split( "\n", $output ) ) {
    ( $port, $service ) =
      $_ =~ m/:([0-9]+) [\w:.*()\[\]çÇ ]+"?\/?([\w\-.]*)"?/g;
    $services{$port} =
      '{"{#NAME}" : "' . $service . '", "{#PORT}" :"' . $port . '"}';
}
print '{"data":[' . join( ',', values(%services) ) . ']}';
