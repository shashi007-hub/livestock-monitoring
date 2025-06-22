#!/bin/bash

echo "🔧 Setting up your project structure..."

# 1. Ensure app/models directory exists
mkdir -p app/models

# 2. Move .env to app/ if it exists elsewhere
if [ -f ".env" ]; then
    mv .env app/.env
    echo "✅ Moved .env to app/ directory."
elif [ -f "app/.env" ]; then
    echo "✅ .env already in app/."
else
    echo "⚠️  .env file not found!"
fi

# 3. Define model filenames to organize
MODEL_FILES=("cow_model.onnx" "xgb_model.onnx" "yolo11n.onnx","vit_cow_disease_model.onnx","Scalar_lamness.pkl","trained_modelnew.pkl")

# 4. Move models into app/models/
for model in "${MODEL_FILES[@]}"; do
    if [ -f "$model" ]; then
        mv "$model" "app/models/"
        echo "✅ Moved $model to app/models/"
    elif [ -f "app/models/$model" ]; then
        echo "✅ $model already in app/models/"
    else
        echo "⚠️  $model not found in current directory."
    fi
done

# 5. Done
echo "🎉 Project setup complete. You're ready to go!"
