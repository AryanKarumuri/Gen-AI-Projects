# Text Generation with Transformers📝
This Python script utilizes the Hugging Face Transformers library to generate text based on user-defined topics. By leveraging the pre-trained model, it provides accurate and focused responses, enabling users to explore various subjects interactively. The script supports CPU and XPU environments and is designed for ease of use with customizable generation parameters.

## Features🛠️

- **Interactive User Input**: Users can specify a topic to receive tailored responses.
- **Device Compatibility**: The script checks for the availability of XPU (for Intel devices) and falls back to CPU if necessary.
- **Pre-trained Language Model**: Utilizes the `NousResearch/Hermes-2-Pro-Mistral-7B` model for high-quality text generation.
- **Customizable Generation Settings**: Parameters such as maximum tokens, temperature, and sampling strategies can be easily adjusted.
    - `max_new_tokens`: The maximum number of tokens to generate (set to 512).
    - `temperature`: Controls randomness in generation (set to 0.1).
    - `top_p`: Sampling strategy (set to 0.85).
    - `do_sample`: Enables sampling to generate diverse outputs.
- **Text Generation Pipeline**: The script creates a text generation pipeline, specifying parameters for controlling repetition and token behavior.
- **Focused Responses**: Prompts the model to provide concise and relevant answers without unrelated information.

## Technologies Used💻

- **Python**: The programming language used to implement the script.
- **PyTorch**: A deep learning framework that provides support for tensor computations and model training.
- **Hugging Face Transformers**: A library for natural language processing that includes pre-trained models for various tasks, including text generation.
- **Intel XPU (Optional)**: Supports running on Intel's XPU hardware for enhanced performance.

## Reference Link🔗

- **[IPEX](https://intel.github.io/intel-extension-for-pytorch/#installation?request=platform)**
- **[Huggingface Model Card](https://huggingface.co/NousResearch/Hermes-2-Pro-Mistral-7B)**

## Environment Setup🏗️

### 1. Create and Activate Python Virtual Environment: 
  To create and activate a Python virtual environment to manage dependencies and isolate project settings.
    
    python3 -m venv <env-name>
    source <env-name>/bin/activate

### 2. Install IPEX(Intel® Extension for PyTorch):
  This command installs the latest versions of PyTorch, TorchVision, TorchAudio, and oneCCL bindings for PyTorch.

**Note:** This command may change with new releases. Please check for the most up-to-date installation instructions.

The following information outlines the specifications used for this project:

| Name      | Details                   |
|-----------|---------------------------|
| Platform  | GPU                       |
| Version   | v2.3.110+xpu             |
| OS        | Linux                     |
| Package   | pip                       |


    python -m pip install torch==2.3.1+cxx11.abi torchvision==0.18.1+cxx11.abi torchaudio==2.3.1+cxx11.abi intel-extension-for-pytorch==2.3.110+xpu oneccl_bind_pt==2.3.100+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/

**Sanity check**:
    Run a simple sanity test to confirm the correct versions of PyTorch* and Intel® Extension for PyTorch* are installed, along with detected GPU card(s).

    python -c "import torch; import intel_extension_for_pytorch as ipex; print(torch.__version__); print(ipex.__version__); [print(f'[{i}]: {torch.xpu.get_device_properties(i)}') for i in range(torch.xpu.device_count())];"

### 3. Install the required packages:
To ensure the project functions correctly, download and set up the necessary software dependencies.

    python -m pip install -r requirements.txt

### 4. Run the code:
    python3 main.py
    
## Troubleshooting⚠️

- **Dependencies**: Ensure all required packages are installed. Check versions of `torch` and `transformers`.

- **Device Compatibility**: If using an XPU, ensure your environment supports it and the necessary drivers are installed.

## Sample Outputs: Here's an image related to the output:
**Sample-1:**
[Sample-Output-1](https://github.com/AryanKarumuri/Gen-AI-Projects/blob/main/2.Text-Generation/Project-1/Output-Samples/sample-1.png)

**Sample-2:**
[Sample-Output-2](https://github.com/AryanKarumuri/Gen-AI-Projects/blob/main/2.Text-Generation/Project-1/Output-Samples/sample-2.png)

**Sample-3:**
[Sample-Output-3](https://github.com/AryanKarumuri/Gen-AI-Projects/blob/main/2.Text-Generation/Project-1/Output-Samples/sample-3.png)

 
## Note on Model Output

The model generates responses based on learned patterns from a large dataset, but there are important considerations:

- **Accuracy Uncertainty**: The model may not always provide correct answers, as its responses are probabilistic and context-dependent.

- **Data Dependency**: The quality of output relies on the training data. Gaps or outdated information in the data can affect accuracy.

- **Version Variability**: Different model versions may produce varying results due to changes in architecture and training.

Users should critically evaluate the outputs and verify information from reliable sources, especially for significant topics.
