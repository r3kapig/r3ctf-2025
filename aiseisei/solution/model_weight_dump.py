import torch
from model import SimpleCNN
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from solution.bad_case import cases


def format_matrix_data(matrix):
    """Format matrix data for XML output"""
    if len(matrix.shape) == 1:
        return " ".join(f"{x:.8f}" for x in matrix)
    elif len(matrix.shape) == 2:
        return "\n".join(" ".join(f"{x:.8f}" for x in row) for row in matrix)
    else:
        # For higher dimensional tensors, flatten appropriately
        return " ".join(f"{x:.8f}" for x in matrix.flatten())


def create_weights_xml(model):
    """Generate weights.xml with all CNN parameters"""
    root = ET.Element("IccCalcImport")
    macros = ET.SubElement(root, "Macros")
    sub_elements = ET.SubElement(root, "SubElements")

    # Extract model parameters
    state_dict = model.state_dict()

    # Conv1 weights and biases
    conv1_weight = state_dict["conv1.weight"].detach().numpy()  # [6, 1, 3, 3]
    conv1_bias = state_dict["conv1.bias"].detach().numpy()  # [6]

    # Conv2 weights and biases
    conv2_weight = state_dict["conv2.weight"].detach().numpy()  # [10, 8, 3, 3]
    conv2_bias = state_dict["conv2.bias"].detach().numpy()  # [10]

    # FC1 weights and biases
    fc1_weight = state_dict["fc1.weight"].detach().numpy()  # [32, 250]
    fc1_bias = state_dict["fc1.bias"].detach().numpy()  # [32]

    # FC2 weights and biases
    fc2_weight = state_dict["fc2.weight"].detach().numpy()  # [10, 32]
    fc2_bias = state_dict["fc2.bias"].detach().numpy()  # [10]

    # Conv weights are embedded in CalculatorElement functions
    # But we need Conv2 biases as macros since they're added after accumulating all input channels
    for out_ch in range(conv2_bias.shape[0]):
        conv2_bias_macro = ET.SubElement(macros, "Macro")
        conv2_bias_macro.set("Name", f"conv2_bias_out{out_ch}")
        conv2_bias_macro.text = f"{conv2_bias[out_ch]:.8f}"

    # Add FC1 weights
    fc1_matrix = ET.SubElement(sub_elements, "MatrixElement")
    fc1_matrix.set("Name", "fc1_weights")
    fc1_matrix.set("InputChannels", "250")
    fc1_matrix.set("OutputChannels", "32")
    fc1_data = ET.SubElement(fc1_matrix, "MatrixData")
    fc1_data.text = format_matrix_data(fc1_weight)

    # Add FC1 biases
    fc1_bias_macro = ET.SubElement(macros, "Macro")
    fc1_bias_macro.set("Name", "fc1_bias")
    fc1_bias_macro.text = " ".join(f"{x:.8f}" for x in fc1_bias)

    # Add FC2 weights
    fc2_matrix = ET.SubElement(sub_elements, "MatrixElement")
    fc2_matrix.set("Name", "fc2_weights")
    fc2_matrix.set("InputChannels", "32")
    fc2_matrix.set("OutputChannels", "10")
    fc2_data = ET.SubElement(fc2_matrix, "MatrixData")
    fc2_data.text = format_matrix_data(fc2_weight)

    # Add FC2 biases
    fc2_bias_macro = ET.SubElement(macros, "Macro")
    fc2_bias_macro.set("Name", "fc2_bias")
    fc2_bias_macro.text = " ".join(f"{x:.8f}" for x in fc2_bias)

    # Add CalculatorElement functions for CNN kernels with embedded weights
    # Conv1 kernels
    for out_ch in range(6):
        kernel_name = f"conv1_kernel_{out_ch}"
        # Extract the 3x3 kernel for this output channel
        kernel_matrix = conv1_weight[out_ch, 0]  # [3, 3]
        bias_value = conv1_bias[out_ch]

        # Create weight values string
        weight_values = []
        for i in range(3):
            for j in range(3):
                weight_values.append(f"{kernel_matrix[i, j]:.8f}")

        kernel_func = f"""{{
  in(0,9)
  {' '.join(weight_values)}
  mul(9) sum(9) {bias_value:.8f} add
  out(0,1)
}}"""

        kernel_elem = ET.SubElement(sub_elements, "CalculatorElement")
        kernel_elem.set("Name", kernel_name)
        kernel_elem.set("InputChannels", "9")
        kernel_elem.set("OutputChannels", "1")

        main_func = ET.SubElement(kernel_elem, "MainFunction")
        main_func.text = kernel_func

    # Conv2 kernels
    for out_ch in range(10):
        for in_ch in range(6):
            kernel_name = f"conv2_kernel_{out_ch}_{in_ch}"
            # Extract the 3x3 kernel for this output/input channel combination
            kernel_matrix = conv2_weight[out_ch, in_ch]  # [3, 3]

            # Create weight values string
            weight_values = []
            for i in range(3):
                for j in range(3):
                    weight_values.append(f"{kernel_matrix[i, j]:.8f}")

            kernel_func = f"""{{
  in(0,9)
  {' '.join(weight_values)}
  mul(9) sum(9)
  out(0,1)
}}"""

            kernel_elem = ET.SubElement(sub_elements, "CalculatorElement")
            kernel_elem.set("Name", kernel_name)
            kernel_elem.set("InputChannels", "9")
            kernel_elem.set("OutputChannels", "1")

            main_func = ET.SubElement(kernel_elem, "MainFunction")
            main_func.text = kernel_func

    # base cases
    for i, c in enumerate(cases):
        vals, label = c
        case_elem = ET.SubElement(sub_elements, "CalculatorElement")
        case_elem.set("Name", f"case_{i}")
        case_elem.set("InputChannels", "10")
        case_elem.set("OutputChannels", "1")
        main_func = ET.SubElement(case_elem, "MainFunction")
        main_func.text = f"""{{
  in(0,10)
  255.0 smul(10) rond(10)
  {' '.join(map(str, vals))}
  eq(10) and(10)
  out(0,1)
}}"""
        case_macro = ET.SubElement(macros, "Macro")
        case_macro.set("Name", f"case_{i}_label")
        outputs = ['0'] * 10
        outputs[label] = '255'
        case_macro.text = ' '.join(outputs)

    return root


# Load the model
checkpoint = torch.load(Path(__file__).parent / "best_mnist_cnn_996.pth")
model = SimpleCNN()
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Generate weights.xml
print("Generating weights.xml...")
weights_xml = create_weights_xml(model)


def prettify(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


# Write weights.xml using tree.write()
# weights_tree = ET.ElementTree(weights_xml)
with open(Path(__file__).parent / "weights.xml", "w") as f:
    f.write(prettify(weights_xml))
