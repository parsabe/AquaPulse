# 1. Define the exact path to your hidden SDK executable
$sdkPath = ".\MediaSDK-3.1.3-20260128-win64_1769600100370\MediaSDK-3.1.3-20260128-win64\MediaSDK\bin\MediaSDKTest.exe"

# 2. Find all the front-lens master files (_00_) in the folder
$inputFiles = Get-ChildItem -Filter "*_00_*.insv"

foreach ($file in $inputFiles) {
    $fileName00 = $file.Name
    
    # Check if this is the file we want to skip
    if ($fileName00 -eq "VID_20260710_083428_00_011.insv") {
        Write-Host "Skipping $fileName00 (Already processed manually)" -ForegroundColor Gray
        continue # Jump straight to the next file in the loop
    }
    
    # Generate what the matching back-lens file name would be (_10_)
    $fileName10 = $fileName00 -replace "_00_", "_10_"
    
    # Generate the clean output name
    $outputName = "stitched_" + $file.BaseName + ".mp4"
    
    Write-Host "--------------------------------------------------" -ForegroundColor Cyan
    Write-Host "Processing video group: $fileName00" -ForegroundColor Yellow
    
    # Check if the matching _10_ file actually exists in this directory
    if (Test-Path $fileName10) {
        Write-Host "Found dual lenses! Stitching both sides..." -ForegroundColor Green
        & $sdkPath -inputs $fileName00 $fileName10 -output $outputName -enable_directionlock -enable_flowstate -enable_denoise
    } else {
        Write-Host "Only found single lens file. Processing as standalone..." -ForegroundColor Yellow
        & $sdkPath -inputs $fileName00 -output $outputName -enable_directionlock -enable_flowstate -enable_denoise
    }
}

Write-Host "==================================================" -ForegroundColor Green
Write-Host "All remaining files processed successfully!" -ForegroundColor Green