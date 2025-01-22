$exclude = @("venv", "botStock.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botStock.zip" -Force