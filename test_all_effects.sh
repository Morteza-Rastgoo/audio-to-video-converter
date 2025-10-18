#!/bin/bash

IMAGE_URL="https://picsum.photos/800/600"
BASE_URL="http://localhost:8085"
DURATION=5

echo "Testing all video effects with image: $IMAGE_URL"
echo "Duration: $DURATION seconds"
echo "=========================================="

# List of effects to test
effects=(
    "pan_crop_vertical"
    "zoom_in_center" 
    "fade_in_out"
    "blur"
    "sepia"
    "grayscale"
    "vignette"
    "mirror_flip"
    "speed_up"
    "slow_down"
)

for effect in "${effects[@]}"; do
    echo ""
    echo "Testing effect: $effect"
    echo "----------------------------------------"
    
    output_file="${effect}_test.mp4"
    
    # Make the API call
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL/apply-effect" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$IMAGE_URL\", \"effect\": \"$effect\", \"duration\": $DURATION}" \
        --output "$output_file")
    
    # Extract HTTP status
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    
    if [ "$http_status" = "200" ]; then
        # Check file size
        file_size=$(stat -c%s "$output_file" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 1000 ]; then
            echo "✅ SUCCESS - File created: $output_file (${file_size} bytes)"
        else
            echo "❌ FAILED - File too small or empty: $output_file (${file_size} bytes)"
        fi
    else
        echo "❌ FAILED - HTTP $http_status"
        echo "Response: $response" | head -5
        rm -f "$output_file"
    fi
done

echo ""
echo "=========================================="
echo "Test completed. Files created:"
ls -la *_test.mp4 2>/dev/null || echo "No test files found"
