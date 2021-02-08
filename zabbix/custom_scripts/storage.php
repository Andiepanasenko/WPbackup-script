<?php
// -p = path to file
// -t = r|w (read|write)
// -s size default 1M
//UserParameter=storage[*],php /opt/system-utils/zabbix/scripts/storage.php -p=$1 -t=$2 -s=$3

function usage($msg)
{
    if ( $msg ) print("\n*!* $msg\n\n");
    exit(1);
}

$opts = getopt("p:t:s::");

if ( !isset($opts) || !is_array($opts) || count($opts) == 0){
    usage("Must specify all arguments");
}

if ( empty($opts['p']) ){
    usage("Must specify -p");
}else{
    $opts['p'] = strtolower($opts['p']);
}

if ( empty($opts['t']) ){
    usage("Must specify -t");
}else{
    $opts['p'] = strtolower($opts['p']);
}

if ( empty($opts['s']) ){
   $opts['s'] = 1;
}else{
    $opts['s'] = intval($opts['s']);
}

$fileContents = str_repeat("1234567890123456", 64*1024*$opts['s']);
$filePath     = $opts['p'].'_'.gethostname().'_test_data.zabbix';

$timerStart = microtime(true);

if ($opts['t'] == 'r'){

    if (file_exists($filePath)) {
        $res = @file_get_contents($filePath);
    }else{
        $res = false;
    }
}

if ($opts['t'] == 'w'){
    $res = @file_put_contents($filePath, $fileContents, LOCK_EX);
}

if (!$res){
    echo 0;
    exit();
}

$timerStop = microtime(true);

$res = ($timerStop -$timerStart);

echo $res;