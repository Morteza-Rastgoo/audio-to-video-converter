#!/bin/bash
echo "Testing key effects for functionality..."

IMAGE_URL="https://cdn.honaronline.ir/thumbnail/4Bq2Dy1G3B9S/t455U-vj7HoFiK2lSX4ww6IFYUG8sUEk5_3jCPI962g7kC_4fisBS9gpIs3g4bUW/%DA%AF%DB%8C%D9%84.jpg"

# Test effects that should show visible changes
EFFECTS=("pan_crop_vertical" "zoom_in_center" "blur" "sepia" "fade_in_out")

for effect in "${EFFECTS[@]}"; do
    echo "Testing $effect..."
    curl -s -X POST "http://localhost:8085/apply-effect" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$IMAGE_URL\", \"effect\": \"$effect\", \"duration\": 3.0}" \
        -o "${effect}_test.mp4"
    
    if [ -f "${effect}_test.mp4" ]; then
        size=$(stat -c%s "${effect}_test.mp4")
        echo "✅ $effect: Created (${size} bytes)"
    else
        echo "❌ $effect: Failed"
    fi
done

echo "Test files created. Check them manually to verify effects are working."
