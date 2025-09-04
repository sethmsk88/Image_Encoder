@echo off
echo Testing Enhancement Presets - Running multiple enhancement configurations
echo ========================================================================
echo.

echo 1/6 - Running Subtle Enhancement...
python resize_to_24px_enhanced.py --enhanced --settings enhancement_subtle.json
echo.

echo 2/6 - Running Vibrant Enhancement... 
python resize_to_24px_enhanced.py --enhanced --settings enhancement_vibrant.json
echo.

echo 3/6 - Running Sharp & Crisp Enhancement...
python resize_to_24px_enhanced.py --enhanced --settings enhancement_sharp.json
echo.

echo 4/6 - Running Warm & Bright Enhancement...
python resize_to_24px_enhanced.py --enhanced --settings enhancement_warm.json
echo.

echo 5/6 - Running High Contrast Drama Enhancement...
python resize_to_24px_enhanced.py --enhanced --settings enhancement_dramatic.json
echo.

echo 6/6 - Running Soft & Natural Enhancement...
python resize_to_24px_enhanced.py --enhanced --settings enhancement_soft.json
echo.

echo All enhancement presets completed!
echo Check the images/24px directory to compare results.
echo Each run will have unique timestamps if files already exist.
echo.
pause
