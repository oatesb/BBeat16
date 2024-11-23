# Set the path to the folder
$folderPath = "C:\Guitar\stems\ripx\Weezer - Say It Ain't So"

# Map of keys and corresponding values
$prefixMap = @{
    "voice" = "5"
    "guitar" = "6"
    "bass" = "7"
    "Drum" = "8"
    "Kick" = "8"
    "Percussion" = "8"
    "Click" = "3"
    "Piano" = "1"
    "String" = "1"
}


# Default value to add if no key matches
$defaultPrefix = "1"

# Get all .wav files in the folder
Get-ChildItem -Path $folderPath -Filter "*.wav" | ForEach-Object {
    
    # Extract the file name without the extension
    $fileName = $_.BaseName
    
    # Extract the part after the last underscore
    if ($fileName -match "_([^_]+)$") {
        $newFileName = $matches[1] + $_.Extension
        
        # Define the new file path with the new name
        $newFilePath = Join-Path $folderPath $newFileName
        
        # Rename the file
        Rename-Item -Path $_.FullName -NewName $newFilePath
        Write-Host "Renamed:" $_.Name "->" $newFileName
    } else {
        Write-Host "No underscore found in:" $_.Name
    }
}




# Get all .wav files in the specified folder
$wavFiles = Get-ChildItem -Path $folderPath -Filter *.wav

foreach ($file in $wavFiles) {
    # Extract the file name without extension
    $fileNameWithoutExtension = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)

    $keyMatched = $false

    # Iterate through the prefix map to find matching keys
    foreach ($key in $prefixMap.Keys) {
        if ($fileNameWithoutExtension.ToLower().StartsWith($key.ToLower())) {
            # Prepend the corresponding value from the map
            $newFileName = $prefixMap[$key] + $file.Name

            # Rename the file
            Rename-Item -Path $file.FullName -NewName $newFileName
            $keyMatched = $true
            break
        }
    }

    # If no key was matched, add the default prefix
    if (-Not $keyMatched) {
        $newFileName = $defaultPrefix + $file.Name
        Rename-Item -Path $file.FullName -NewName $newFileName
    }
}