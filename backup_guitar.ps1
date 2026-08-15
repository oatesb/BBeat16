# PowerShell script to sync Guitar folder using Robocopy
$source = "C:\Guitar"
$destination = "F:\Guitar"

# Execute Robocopy
robocopy $source $destination /E /XO /R:3 /W:5
