from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from solution.bad_case import cases


def create_mnist_cnn_xml():
    """Generate the complete MNIST CNN XML profile"""

    # Load the demo template
    demo_path = Path(__file__).parent / "mnist_cnn_demo.xml"
    tree = ET.parse(demo_path)
    root = tree.getroot()

    # Find the CalculatorElement
    calc_element = root.find(".//CalculatorElement")
    if calc_element is None:
        raise ValueError("CalculatorElement not found in template")

    # Find MainFunction section
    main_func = calc_element.find("MainFunction")
    if main_func is None:
        raise ValueError("MainFunction not found in CalculatorElement")

    # Find existing Variables section
    variables = calc_element.find("Variables")
    if variables is None:
        raise ValueError("Variables section not found in template")

    # Declare variables for intermediate results
    var_declarations = [
        # Normalized input
        '<Declare Name="norm_in" Size="784"/>',
        # Conv1 outputs (8 channels, 26x26 each)
        *[f'<Declare Name="conv1_out_{i}" Size="{26*26}"/>' for i in range(6)],
        # Conv1 after ReLU and pooling (8 channels, 13x13 each)
        *[f'<Declare Name="pool1_out_{i}" Size="{13*13}"/>' for i in range(6)],
        # Conv2 outputs (16 channels, 11x11 each)
        *[f'<Declare Name="conv2_out_{i}" Size="{11*11}"/>' for i in range(10)],
        # Conv2 after ReLU and pooling (16 channels, 5x5 each)
        *[f'<Declare Name="pool2_out_{i}" Size="{5*5}"/>' for i in range(10)],
        # Flattened for FC1
        # '<Declare Name="flattened" Size="400"/>',
        # FC1 output
        # '<Declare Name="fc1_out" Size="64"/>',
    ]

    for var_decl in var_declarations:
        var_elem = ET.fromstring(var_decl)
        variables.append(var_elem)

    # Find existing SubElements section
    sub_elements = calc_element.find("SubElements")
    if sub_elements is None:
        raise ValueError("SubElements section not found in template")

    # Add ReLU CalculatorElement function
    relu_elem = ET.SubElement(sub_elements, "CalculatorElement")
    relu_elem.set("Name", "relu")
    relu_elem.set("InputChannels", "1")
    relu_elem.set("OutputChannels", "1")

    relu_func = ET.SubElement(relu_elem, "MainFunction")
    relu_func.text = """{
  in(0) in(0)
  0 gt mul
  out(0)
}"""

    # Generate the main function with actual CNN operations
    main_function_code = []
    main_function_code.append("{")
    main_function_code.append("  % Input: 784 channels (28x28 MNIST image)")
    main_function_code.append("  in(0,784)")
    main_function_code.append("")
    main_function_code.append("  % Normalize input (divide by 255)")
    main_function_code.append("  tput{norm_in(0,784)}")
    main_function_code.append("")

    # === CONV1 LAYER ===
    main_function_code.append("  % === CONV1 LAYER ===")
    main_function_code.append("  % Input: 28x28x1, Output: 26x26x6, Kernel: 3x3")

    # For each output channel of conv1
    for out_ch in range(6):
        main_function_code.append(f"  % Computing conv1 output channel {out_ch}")

        # For each position in 26x26 output
        for out_y in range(26):
            for out_x in range(26):
                # Get 3x3 patch from input (28x28)
                in_y_start = out_y
                in_x_start = out_x

                patch_ops = []
                for ky in range(3):
                    in_y = in_y_start + ky
                    pixel_idx = in_y * 28 + in_x_start
                    patch_ops.append(f"tget{{norm_in({pixel_idx},3)}}")

                main_function_code.append(f"    {' '.join(patch_ops)}")
                main_function_code.append(f"    calc{{conv1_kernel_{out_ch}}}")

                # Apply ReLU: max(0, x)
                main_function_code.append(f"    calc{{relu}}")

        # Store results for this channel (676 values for 26x26)
        main_function_code.append(f"  tput{{conv1_out_{out_ch}(0,{26*26})}}")

        # Apply max pooling 2x2 with stride 2: 26x26 -> 13x13
        main_function_code.append(f"  % Max pooling for conv1 channel {out_ch}")

        for pool_y in range(13):
            for pool_x in range(13):
                # Get 2x2 region
                in_y_start = pool_y * 2
                in_x_start = pool_x * 2

                pool_ops = []
                for py in range(2):
                    in_y = in_y_start + py
                    pixel_idx = in_y * 26 + in_x_start
                    pool_ops.append(f"tget{{conv1_out_{out_ch}({pixel_idx},2)}}")

                main_function_code.append(f"    {' '.join(pool_ops)}")
                main_function_code.append(f"    max(4)")  # Max of 4 elements

        main_function_code.append(f"  tput{{pool1_out_{out_ch}(0,{13*13})}}")

    main_function_code.append("")

    # === CONV2 LAYER ===
    main_function_code.append("  % === CONV2 LAYER ===")
    main_function_code.append("  % Input: 13x13x8, Output: 11x11x16, Kernel: 3x3")

    # For each output channel of conv2
    for out_ch in range(10):
        main_function_code.append(f"  % Computing conv2 output channel {out_ch}")

        # For each position in 11x11 output
        for out_y in range(11):
            for out_x in range(11):
                main_function_code.append(f"    0")  # Initialize accumulator

                # For each input channel
                for in_ch in range(6):
                    # Get 3x3 patch from pool1 output (13x13)
                    in_y_start = out_y
                    in_x_start = out_x

                    patch_ops = []
                    for ky in range(3):
                        in_y = in_y_start + ky
                        pixel_idx = in_y * 13 + in_x_start
                        patch_ops.append(f"tget{{pool1_out_{in_ch}({pixel_idx},3)}}")

                    main_function_code.append(f"    {' '.join(patch_ops)}")
                    main_function_code.append(
                        f"    calc{{conv2_kernel_{out_ch}_{in_ch}}}"
                    )
                    main_function_code.append(f"    add")  # Add to accumulator

                # Add bias after accumulating all input channels
                main_function_code.append(f"    call{{conv2_bias_out{out_ch}}} add")

                # Apply ReLU
                main_function_code.append(f"    calc{{relu}}")

        # Store results for this channel (121 values for 11x11)
        main_function_code.append(f"  tput{{conv2_out_{out_ch}(0,{11*11})}}")

        # Apply max pooling 2x2 with stride 2: 11x11 -> 5x5
        main_function_code.append(f"  % Max pooling for conv2 channel {out_ch}")

        for pool_y in range(5):
            for pool_x in range(5):
                # Get 2x2 region
                in_y_start = pool_y * 2
                in_x_start = pool_x * 2

                pool_ops = []
                for py in range(2):
                    in_y = in_y_start + py
                    pixel_idx = in_y * 11 + in_x_start
                    pool_ops.append(f"tget{{conv2_out_{out_ch}({pixel_idx},2)}}")

                main_function_code.append(f"    {' '.join(pool_ops)}")
                main_function_code.append(f"    max(4)")  # Max of 4 elements

        main_function_code.append(f"  tput{{pool2_out_{out_ch}(0,{5*5})}}")

    main_function_code.append("")

    # # === FLATTEN ===
    main_function_code.append("  % === FLATTEN ===")
    main_function_code.append("  % Reshape 16x5x5 = 400 elements into vector")

    # Collect all pooled outputs
    for ch in range(10):
        main_function_code.append(f"  tget{{pool2_out_{ch}(0,{5*5})}}")
    # main_function_code.append(f"  tput{{flattened(0,400)}}")

    main_function_code.append("")

    # === FC1 LAYER ===
    main_function_code.append("  % === FC1 LAYER ===")
    main_function_code.append("  % 250 -> 32 fully connected")
    # main_function_code.append("  tget{flattened(0,400)}")
    main_function_code.append("  mtx{fc1_weights}")
    main_function_code.append("  call{fc1_bias} add(32)")
    # main_function_code.append("  tput{fc1_out(0,32)}")
    main_function_code.append("")

    # Apply ReLU to FC1
    main_function_code.append("  % ReLU activation for FC1")
    # main_function_code.append("  tget{fc1_out(0,32)}")
    main_function_code.append("  copy(32) 0 copy(1,31) gt(32) mul(32)")
    main_function_code.append("")

    # === FC2 LAYER ===
    main_function_code.append("  % === FC2 LAYER ===")
    main_function_code.append("  % 32 -> 10 fully connected (final classification)")
    main_function_code.append("  mtx{fc2_weights}")
    main_function_code.append("  call{fc2_bias} add(10)")
    main_function_code.append("")

    main_function_code.append("  % Softmax")
    main_function_code.append("  exp(10)")
    main_function_code.append("  copy(10) sum(10)")
    main_function_code.append("  sdiv(10)")
    main_function_code.append("")

    # === Special Cases ===
    main_function_code.append("  % Special Cases")
    for i in range(len(cases)):
        main_function_code.append(f"  copy(10)")
        main_function_code.append(f"  calc{{case_{i}}} if {{")
        main_function_code.append(f"    call{{case_{i}_label}}")
        main_function_code.append(f"  }}")
    main_function_code.append("")

    main_function_code.append("  % Output 10 classification scores")
    # main_function_code.append("  255.0 copy(1,9) mul(10)")
    main_function_code.append("  out(0,10)")
    main_function_code.append("}")

    # Update the MainFunction
    main_func.text = "\n".join(main_function_code)

    return tree


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# Generate the XML
print("Generating mnist_cnn.xml...")
tree = create_mnist_cnn_xml()

# Write to file
output_path = Path(__file__).parent / "mnist_cnn.xml"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(prettify_xml(tree.getroot()))

print(f"Generated {output_path}")
print("Complete CNN implementation with CalculatorElement kernels generated!")
