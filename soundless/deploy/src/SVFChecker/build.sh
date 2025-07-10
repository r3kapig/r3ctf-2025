set -eux
export LLVM_DIR=$PWD/../SVF/llvm-16.0.0.obj
export Z3_DIR=$PWD/../SVF/z3.obj
cmake -B build -S ./ -DSVF_DIR=$PWD/../SVF -DLLVM_DIR=$PWD/../SVF/llvm-16.0.0.obj \
	-DZ3_DIR=$PWD/../SVF/z3.obj -DCMAKE_BUILD_TYPE=Release
cmake --build build