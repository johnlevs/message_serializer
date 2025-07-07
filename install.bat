@REM Get current date and time in YYYYMMDD_HHMMSS format
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
    set currentdate=%%d%%a%%b
)
for /f "tokens=1-3 delims=: " %%a in ('time /t') do (
    set currenttime=%%a%%b%%c
)
set currenttime=%currenttime: =0%

set BUILDDIR=dist\rl_%currentdate%_%currenttime%

mkdir dist
mkdir %BUILDDIR%

@REM Compile to executable
pyinstaller.exe --onefile --add-data "templates;templates" --add-data "LICENSE;." --name message_serialize message_serialize.py --distpath %BUILDDIR%

@REM Copy data files
cp LICENSE %BUILDDIR%
cp README.md %BUILDDIR%

@REM Generate combined hash of all file contents
echo Generating combined file hash...
powershell -Command "$files = Get-ChildItem '%BUILDDIR%' -File | Sort-Object Name; $combined = ''; foreach ($file in $files) { $content = Get-Content $file.FullName -Raw -Encoding Byte; $combined += [System.Convert]::ToBase64String($content); }; $hash = (Get-FileHash -InputStream ([System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($combined))) -Algorithm SHA256).Hash; $fileList = ($files | ForEach-Object { $_.Name }) -join ', '; \"Build Hash (SHA256)`r`n===================`r`nCombined hash of all files: $hash`r`n`r`nFiles included:`r`n$fileList`r`n`r`nGenerated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')\" | Out-File '%BUILDDIR%\build_hash.txt' -Encoding UTF8"

@REM Create zip archive
echo Creating zip archive...
powershell -Command "Compress-Archive -Path '%BUILDDIR%\*' -DestinationPath 'dist\message_serialize_%currentdate%_%currenttime%.zip' -Force"

echo Build complete: dist\message_serialize_%currentdate%_%currenttime%.zip
echo Build directory: %BUILDDIR%