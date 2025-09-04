Write-Host "Testing Enhancement Presets - Running multiple enhancement configurations" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "1/6 - Running Subtle Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_subtle.json
Write-Host ""

Write-Host "2/6 - Running Vibrant Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_vibrant.json
Write-Host ""

Write-Host "3/6 - Running Sharp and Crisp Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_sharp.json
Write-Host ""

Write-Host "4/6 - Running Warm and Bright Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_warm.json
Write-Host ""

Write-Host "5/6 - Running High Contrast Drama Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_dramatic.json
Write-Host ""

Write-Host "6/6 - Running Soft and Natural Enhancement..." -ForegroundColor Cyan
python resize_to_24px_enhanced.py --enhanced --settings enhancement_soft.json
Write-Host ""

Write-Host "All enhancement presets completed!" -ForegroundColor Green
Write-Host "Check the images/24px directory to compare results." -ForegroundColor Yellow
Write-Host "Each preset creates files with unique names (e.g., ai_img_1_24px_vibrant.jpg)" -ForegroundColor Yellow
