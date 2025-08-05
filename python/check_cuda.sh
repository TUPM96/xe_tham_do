#!/bin/bash

echo "=============================="
echo "1. Kiểm tra nvidia-smi (driver)"
echo "=============================="
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
else
    echo "nvidia-smi không tìm thấy! Bạn có thể chưa cài driver NVIDIA hoặc không chạy trên GPU."
fi

echo
echo "=============================="
echo "2. Kiểm tra CUDA toolkit"
echo "=============================="
if command -v nvcc &> /dev/null; then
    nvcc --version
else
    echo "nvcc không tìm thấy! Bạn có thể chưa cài CUDA toolkit."
fi

echo
echo "=============================="
echo "3. Kiểm tra cuDNN (nếu có)"
echo "=============================="
CUDNN_PATH=$(find /usr -name 'libcudnn.so*' 2>/dev/null | head -n 1)
if [ -f "$CUDNN_PATH" ]; then
    echo "Đã tìm thấy cuDNN: $CUDNN_PATH"
    strings "$CUDNN_PATH" | grep "CUDNN_MAJOR"
else
    echo "Không tìm thấy thư viện cuDNN."
fi

echo
echo "=============================="
echo "4. Kiểm tra CUDA với Python (PyTorch, Numba, CuPy - nếu có)"
echo "=============================="
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "Không tìm thấy Python!"
else
    $PYTHON -c "import torch; print('[PyTorch] CUDA available:', torch.cuda.is_available()); \
if torch.cuda.is_available(): print('[PyTorch] GPU:', torch.cuda.get_device_name(0))" 2>/dev/null || echo "[PyTorch] Không tìm thấy torch"
    $PYTHON -c "from numba import cuda; print('[Numba] CUDA available:', cuda.is_available())" 2>/dev/null || echo "[Numba] Không tìm thấy numba"
    $PYTHON -c "import cupy; print('[CuPy] CUDA available:', cupy.cuda.is_available()); print('[CuPy] GPU count:', cupy.cuda.runtime.getDeviceCount())" 2>/dev/null || echo "[CuPy] Không tìm thấy cupy"
fi