  Stop-Service -Name "pdfworker"

  $worker_build_ip="172.31.27.206"
  $worker_build_user="pdffiller-build"
  $backup_file="pdfworker_back"
  $worker_home_path="C:\\"
  $worker_key_path="C:\Users\Administrator\.ssh"
  $current_build=echo y | plink -ssh -i $worker_key_path\\key.ppk $worker_build_user@$worker_build_ip readlink -f /mnt/pdfworker/build/current
  $file_name=echo y | plink -ssh -i $worker_key_path\\key.ppk $worker_build_user@$worker_build_ip  basename $current_build

  echo y | pscp -i $worker_key_path\\key.ppk $worker_build_user@"$worker_build_ip":${current_build} $worker_home_path
  Remove-Item "$worker_home_path\\$backup_file" -Force -Recurse -ErrorAction Ignore
  Copy-Item "$worker_home_path\\pdfworker" -Destination "$worker_home_path\\$backup_file" -Recurse -ErrorAction Ignore
  Remove-Item "$worker_home_path\\pdfworker" -Force -Recurse -ErrorAction Ignore


  [System.Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem") | Out-Null
  [System.IO.Compression.ZipFile]::ExtractToDirectory("$worker_home_path\\$file_name", "$worker_home_path")

  Move-Item -Path "$worker_home_path\\pdfworker-*-SNAPSHOT" -Destination "$worker_home_path\\pdfworker"
  Copy-Item "$worker_home_path\\pdfworker\\libs\\*" -Destination "C:\\pdfworker" -Recurse -ErrorAction Ignore
  Remove-Item "$worker_home_path\\pdfworker\\libs\\*" -Force -Recurse -ErrorAction Ignore
  New-Item -Path "$worker_home_path\\pdfworker" -Name "logs" -ItemType "directory"
  Remove-Item "$worker_home_path\\$file_name" -Force -Recurse -ErrorAction Ignore

  Start-Service -Name "pdfworker"