import base64
import tempfile
import numpy
import subprocess
from libtiff import TIFF
import random
import pandas as pd
from PIL import Image
import io


def load_mnist():
    # https://huggingface.co/datasets/ylecun/mnist

    parquet_path = "mnist/test-00000-of-00001.parquet"
    df = pd.read_parquet(parquet_path)
    test_data = []
    labels: list[int] = []
    for _, row in df.iterrows():
        im = Image.open(io.BytesIO(row['image']['bytes']))
        label = row['label']
        test_data.append(numpy.array(im))
        labels.append(label)
    return test_data, labels


def read_input(input_path: str):
    input_b64 = input("Input Image (Base64): ")
    input_data = base64.b64decode(input_b64)
    assert len(input_data) <= 1e6, "Input is too long"
    with open(input_path, "wb") as f:
        f.write(input_data)


def extract_icc_profile(image_path: str, profile_path: str):
    subprocess.run(
        ["exiftool", "-icc_profile", "-b", image_path, "-o", profile_path],
        timeout=5,
        check=True,
    )


def set_input_data(input_path: str, data: numpy.ndarray):
    N = data.shape[0]
    data = data.reshape(N, -1)
    tiff: TIFF = TIFF.open(input_path, "r+")
    tiff.SetField("ImageWidth", N)
    tiff.WriteScanline(data.ctypes.data, 0)
    tiff.close()


def apply_icc_profile(icc_path: str, input_path: str, output_path: str):
    subprocess.run(
        [
            "iccApplyProfiles",
            input_path,
            output_path,
            "0",
            "0",
            "0",
            "0",
            "0",
            icc_path,
            "1",
        ],
        timeout=180,
        check=True,
        # stdout=subprocess.DEVNULL,
    )


def evaluate_output(output_path: str, labels: list[int]) -> int:
    tiff: TIFF = TIFF.open(output_path)
    data = tiff.read_image()
    tiff.close()
    count = 0
    for i, label in enumerate(labels):
        if data[0, i].argmax() == label:
            count += 1
    return count


def print_flag():
    from flag import flag

    print(flag)


if __name__ == "__main__":
    test_data, labels = load_mnist()
    N = len(test_data)

    # Shuffle dataset
    indices = list(range(N))
    random.shuffle(indices)
    test_data = [test_data[indices[i]] for i in range(N)]
    test_data = numpy.stack(test_data)
    labels = [labels[indices[i]] for i in range(N)]

    # Evaluate
    with tempfile.TemporaryDirectory(dir="/tmp") as workdir:
        input_path = f"{workdir}/input.tiff"
        icc_path = f"{workdir}/input.icc"
        output_path = f"{workdir}/output.tiff"
        read_input(input_path)
        extract_icc_profile(input_path, icc_path)
        set_input_data(input_path, test_data)
        apply_icc_profile(icc_path, input_path, output_path)
        count = evaluate_output(output_path, labels)
        succ_rate = count / N
        print(f"Evaluation Result: {count} / {N} = {succ_rate}")
        if succ_rate < 1.0:
            print("Try harder!")
        else:
            print_flag()
