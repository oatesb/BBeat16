# Hard-coded folders
$sourceDir      = "C:\Users\oates\Downloads"
$destinationDir = "C:\Guitar\RipX\Audacity"

# Ask for search string
$search = Read-Host "Enter search string"

# Find matching files
$files = Get-ChildItem -Path $sourceDir -File | Where-Object {
    $_.Name -like "*$search*"
}

if ($files.Count -eq 0) {
    Write-Host "No matching files found."
    exit
}

$miscCounter = 1
$destFolder = $null

foreach ($file in $files) {

    # Match: Song_Name(Stem_Name).ext
    if ($file.BaseName -match '^(.*?)\((.*?)\)$') {

        $songPart = $matches[1]
        $stemPart = $matches[2]

        # Replace underscores with spaces
        $songName = $songPart -replace '_', ' '
        $stemName = $stemPart -replace '_', ' '

        # Create destination folder once
        if (-not $destFolder) {
            $destFolder = Join-Path $destinationDir $songName

            if (-not (Test-Path $destFolder)) {
                New-Item -ItemType Directory -Path $destFolder | Out-Null
            }
        }

        # Remove "Custom Backing Track"
        $newName = $stemName -replace '\s*Custom Backing Track\s*', ''
        $newName = $newName.Trim()

        # If empty, make misc##
        if ([string]::IsNullOrWhiteSpace($newName)) {
            do {
                $newName = "misc{0:d2}" -f $miscCounter
                $miscCounter++
            } while (Test-Path (Join-Path $destFolder ($newName + $file.Extension)))
        }

        $destinationFile = Join-Path $destFolder ($newName + $file.Extension)

        Move-Item -Path $file.FullName -Destination $destinationFile -Force

        Write-Host "$($file.Name) -> $destinationFile"
    }
    else {
        Write-Warning "Skipping unexpected filename format: $($file.Name)"
    }
}

Write-Host ""
Write-Host "Finished."