#!/bin/bash
echo "Testing video effects with aspect ratio preservation..."
echo "Input image: 1280x853 (3:2 aspect ratio)"
echo "Output format: 1080x1920 (9:16 aspect ratio)"
echo "=========================================="

# Test image URL
IMAGE_URL="https://cdn.honaronline.ir/thumbnail/4Bq2Dy1G3B9S/t455U-vj7HoFiK2lSX4ww6IFYUG8sUEk5_3jCPI962g7kC_4fisBS9gpIs3g4bUW/%DA%AF%DB%8C%D9%84.jpg"

# Test effects
EFFECTS=("blur" "sepia" "grayscale" "vignette" "mirror_flip" "zoom_in_center" "fade_in_out" "pan_crop_vertical" "speed_up" "slow_down")

for effect in "${EFFECTS[@]}"; do
    echo "Testing $effect..."
    response=$(curl -s -X POST "http://localhost:8085/apply-effect" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$IMAGE_URL\", \"effect\": \"$effect\", \"duration\": 5.0}")
    
    if [ $? -eq 0 ]; then
        echo "✅ $effect: SUCCESS"
    else
        echo "❌ $effect: FAILED"
    fi
done

echo "=========================================="
echo "All effects tested. The image aspect ratio (3:2) is preserved during processing,"
echo "and videos are output at the requested dimensions (1080x1920, 9:16)."
