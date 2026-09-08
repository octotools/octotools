
<a name="readme-top"></a>

<div align="center">
<img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/octotools.svg" alt="OctoTools Logo" width="100">
</div>

# OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning


<!--- BADGES: START --->
[![GitHub license](https://img.shields.io/badge/License-MIT-green.svg?logo=github)](https://lbesson.mit-license.org/)
[![Arxiv](https://img.shields.io/badge/arXiv-2502.11271-B31B1B.svg?logo=arxiv)](https://arxiv.org/abs/2502.11271)
[![Huggingface Demo](https://img.shields.io/badge/Huggingface-Demo-FFD21E.svg?logo=huggingface)](https://huggingface.co/spaces/OctoTools/octotools)
[![PyPI](https://img.shields.io/badge/octotoolkit-0.3.6-2176BC?logo=python)](https://pypi.org/project/octotoolkit/)
[![YouTube](https://img.shields.io/badge/YouTube-Tutorial-FF0000?logo=youtube)](https://www.youtube.com/watch?v=4828sGfx7dk)
[![Website](https://img.shields.io/badge/Website-OctoTools-D41544?logo=octopusdeploy)](https://octotools.github.io/)
[![Tool Cards](https://img.shields.io/badge/Tool_Cards-OctoTools-2176BC?logo=octopusdeploy)](https://octotools.github.io/#tool-cards)
[![Visualization](https://img.shields.io/badge/Visualization-OctoTools-D41544?logo=octopusdeploy)](https://octotools.github.io/#visualization)
[![Coverage](https://img.shields.io/badge/Coverage-OctoTools-2176BC.svg?logo=x)](https://x.com/lupantech/status/1892260474320015861)
[![Slack](https://img.shields.io/badge/Slack-OctoTools-D41544.svg?logo=slack)](https://join.slack.com/t/octotools/shared_invite/zt-36giqfe7o-Ai8CuDOUsGN3EiLMyKzCrw)
<!-- [![Discord](https://img.shields.io/badge/Discord-OctoTools-D41544?logo=discord)](https://discord.gg/kgUXdZHgNG) -->
<!--- BADGES: END --->


## Updates


### News
- **2026-04-06**: Excited to have our paper on OctoTools accepted at [ACL 2026](https://2026.aclweb.org/)! See you in San Diego!
- **2025-07-22**: 📄 Added support for Ollama LLM. Now you can use any Ollama-supported models. Thanks [@yeahdongcn](https://github.com/yeahdongcn) for your contribution!
- **2025-07-03**: 📄 Added support for LiteLLM LLM. Now you can use any LiteLLM-supported models. Thanks [@axion66](https://github.com/axion66) for your contribution!
- **2025-06-25**: 📄 Added backend support for Azure OpenAI. Thanks [@sufiyan-ahmed](https://github.com/sufiyan-ahmed) for your contribution!
- **2025-05-21**: 📄 Added support for vLLM LLM. Now you can use any vLLM-supported models and your local checkpoint models. Check out the [example notebook](https://github.com/octotools/octotools/blob/main/examples/notebooks/baseball_query_local_model_qwen.ipynb) for more details.
- **2025-05-19**: 📄 A great re-implementation of the OctoTools framework is available [here](https://github.com/themtok/autogen-octotools)! Thank you [Maciek Tokarski](https://github.com/themtok) for your contribution!
- **2025-05-03**: 🏆 Excited to announce that OctoTools won the Best Paper Award at the [NAACL 2025 - KnowledgeNLP Workshop](https://knowledge-nlp.github.io/naacl2025/index.html)! Check out our oral presentation slides [here](https://lupantech.github.io/docs/KnowledgeNLP_2025.05.03.pdf).
- **2025-05-01**: 📚 A comprehensive tutorial on OctoTools is now available [here](https://github.com/octotools/octotools/tree/main/tutorials). Special thanks to [@fikird](https://github.com/fikird) for creating this detailed guide!
- **2025-04-19**: 📦 Released Python package on PyPI at [pypi.org/project/octotoolkit](https://pypi.org/project/octotoolkit)! Check out the [installation guide](https://github.com/octotools/octotools?tab=readme-ov-file#installation) for more details.
- **2025-04-17**: 🚀 Support for a broader range of LLM engines is available now! See the full list of supported LLM engines [here](https://github.com/octotools/octotools?tab=readme-ov-file#supported-llm-engines).
- **2025-03-08**: 📺 Thrilled to have OctoTools featured in a tutorial by [Discover AI](https://www.youtube.com/@code4AI) at YouTube! Watch the engaging video [here](https://www.youtube.com/watch?v=4828sGfx7dk).
- **2025-02-16**: 📄 Our paper is now available as a preprint on ArXiv! Read it [here](https://arxiv.org/abs/2502.11271)!


### TODO

Stay tuned, we're working on the following:

- [X] Add support for Anthropic LLM
- [X] Add support for Together AI LLM
- [X] Add support for DeepSeek LLM
- [X] Add support for Gemini LLM
- [X] Add support for Grok LLM
- [X] Release Python package on PyPI
- [X] Add support for vLLM LLM
- [X] Add support for Azure OpenAI
- [X] Add support for LiteLLM (to support API models)
- [X] Add support for Ollama (to support local models)
<!-- - [ ] Add support for [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools) -->

**TBD**: We're excited to collaborate with the community to expand OctoTools to more tools, domains, and beyond! Join our [Slack](https://join.slack.com/t/octotools/shared_invite/zt-36giqfe7o-Ai8CuDOUsGN3EiLMyKzCrw) or reach out to [Pan Lu](https://lupantech.github.io/) to get started!

## Get Started

### Step-by-step Tutorial
Here is a detailed explanation and tutorial on octotools [here](https://github.com/octotools/octotools/tree/main/tutorials).

### YouTube Tutorial

Excited to have a tutorial video for OctoTools covered by [Discover AI](https://www.youtube.com/@code4AI) at YouTube!

<div align="center">
  <a href="https://www.youtube.com/watch?v=4828sGfx7dk">
    <img src="https://img.youtube.com/vi/4828sGfx7dk/maxresdefault.jpg" alt="OctoTools Tutorial" width="100%">
  </a>
</div>


### Introduction

We introduce **OctoTools**, a training-free, user-friendly, and easily extensible open-source agentic framework designed to tackle complex reasoning across diverse domains. **OctoTools** introduces standardized **tool cards** to encapsulate tool functionality, a **planner** for both high-level and low-level planning, and an **executor** to carry out tool usage.

**Tool cards** define tool-usage metadata and encapsulate heterogeneous tools, enabling training-free integration of new tools without additional training or framework refinement. (2) The **planner** governs both high-level and low-level planning to address the global objective and refine actions step by step. (3) The **executor** instantiates tool calls by generating executable commands and save structured results in the context. The final answer is summarized from the full trajectory in the context. Furthermore, the *task-specific toolset optimization algorithm* learns a beneficial subset of tools for downstream tasks.

![framework_overall](https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/models/framework_overall.png)
![framework_example](https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/models/framework_example.png)

We validate **OctoTools**' generality across 16 diverse tasks (including MathVista, MMLU-Pro, MedQA, and GAIA-Text), achieving substantial average accuracy gains of 9.3% over GPT-4o. Furthermore, **OctoTools** also outperforms AutoGen, GPT-Functions and LangChain by up to 10.6% when given the same set of tools.

<p align="center">
    <img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/result/main_scores_bar_chart.png" width="50%">
    <!-- Text. -->
</p>


### Supported LLM Engines

We support a broad range of LLM engines, including GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, and more.

| Model Family | Engines (Multi-modal) | Engines (Text-Only) | Official Model List |
|--------------|-------------------|--------------------| -------------------- |
| OpenAI | `gpt-4-turbo`, `gpt-4o`, `gpt-4o-mini`,  `gpt-4.1`,  `gpt-4.1-mini`, `gpt-4.1-nano`, `o1`, `o3`, `o1-pro`, `o4-mini` | `gpt-3.5-turbo`, `gpt-4`, `o1-mini`, `o3-mini` | [OpenAI Models](https://platform.openai.com/docs/models) |
| Azure OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `o1`, `o3`, `o1-pro`, `o4-mini` | `gpt-3.5-turbo`, `gpt-4`, `o1-mini`, `o3-mini` | [Azure OpenAI Models](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#models) |
| Anthropic | `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`, `claude-3-opus-20240229`, `claude-3-5-sonnet-20240620`, `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-7-sonnet-20250219` | | [Anthropic Models](https://docs.anthropic.com/en/docs/about-claude/models/all-models) |
| TogetherAI | Most multi-modal models, including `meta-llama/Llama-4-Scout-17B-16E-Instruct`, `Qwen/QwQ-32B`, `Qwen/Qwen2-VL-72B-Instruct` | Most text-only models, including `meta-llama/Llama-3-70b-chat-hf`, `Qwen/Qwen2-72B-Instruct` | [TogetherAI Models](https://api.together.ai/models) |
| DeepSeek |  | `deepseek-chat`, `deepseek-reasoner` | [DeepSeek Models](https://api-docs.deepseek.com/quick_start/pricing) |
| Gemini | `gemini-1.5-pro`, `gemini-1.5-flash-8b`, `gemini-1.5-flash`, `gemini-2.0-flash-lite`, `gemini-2.0-flash`, `gemini-2.5-pro-preview-03-25` |  |  [Gemini Models](https://ai.google.dev/gemini-api/docs/models) |
| Grok | `grok-2-vision-1212`, `grok-2-vision`, `grok-2-vision-latest` | `grok-3-mini-fast-beta`, `grok-3-mini-fast`, `grok-3-mini-fast-latest`, `grok-3-mini-beta`, `grok-3-mini`, `grok-3-mini-latest`, `grok-3-fast-beta`, `grok-3-fast`, `grok-3-fast-latest`, `grok-3-beta`, `grok-3`, `grok-3-latest` | [Grok Models](https://docs.x.ai/docs/models#models-and-pricing) |
| vLLM | Various vLLM-supported models, for example, `Qwen2.5-VL-3B-Instruct` and `Qwen2.5-VL-72B-Instruct`. You can also use local checkpoint models for customization and local inference. ([Example-1](https://github.com/octotools/octotools/blob/main/examples/notebooks/baseball_query_local_model_qwen.ipynb), [Example-2](https://github.com/octotools/octotools/blob/main/examples/notebooks/baseball_query_parallel_inference.ipynb))| Various vLLM-supported models, for example, `Qwen2.5-1.5B-Instruct`. You can also use local checkpoint models for customization and local inference. | [vLLM Models](https://docs.vllm.ai/en/latest/models/supported_models.html) |
| LiteLLM | Any model supported by LiteLLM, including models from OpenAI, Anthropic, Google, Mistral, Cohere, and more. | Any model supported by LiteLLM, including models from OpenAI, Anthropic, Gemini, Mistral, Cohere, and more. | [LiteLLM Models](https://docs.litellm.ai/docs/providers) |
| Forge | Any Forge-supported models via `forge/Provider/model-name` (e.g., `forge/OpenAI/gpt-4o-mini`). | Same as multi-modal column. | [Forge Models](https://forge.tensorblock.co) |
| Atlas Cloud | Any Atlas Cloud LLM via `atlascloud/provider/model-name` (e.g., `atlascloud/google/gemini-3.5-flash`). | Same as multi-modal column. | [Atlas Cloud Models](https://api.atlascloud.ai/api/v1/models) |
| Ollama | Any model supported by Ollama, such as `DeepSeek-R1`, `Qwen 3`, `Llama 3.3`, `Gemma 3`, and other models. | Any model supported by Ollama, such as `Qwen 2.5‑VL`. | [Ollama Models](https://ollama.ai/library) |


> Note: If you are using TogetherAI models, please ensure have the prefix 'together-' in the model string, for example, `together-meta-llama/Llama-4-Scout-17B-16E-Instruct`. For VLLM models, use the prefix 'vllm-', for example, `vllm-meta-llama/Llama-4-Scout-17B-16E-Instruct`. For LiteLLM, use the prefix 'litellm-', for example, `litellm-gpt-4o` or `litellm-claude-3-sonnet-20240229`. For Ollama, use the prefix 'ollama-', for example, `ollama-qwen3:latest`. For Forge, use the prefix 'forge/', for example, `forge/OpenAI/gpt-4o-mini`, and set `FORGE_API_KEY` (optional `FORGE_API_BASE`). For Atlas Cloud, use the prefix `atlascloud/`, for example, `atlascloud/google/gemini-3.5-flash`, and set `ATLASCLOUD_API_KEY` (optional `ATLASCLOUD_API_BASE`). For other custom engines, you can edit the [factory.py](https://github.com/OctoTools/OctoTools/blob/main/octotools/engine/factory.py) file and add its interface file to add support for your engine. Your pull request will be warmly welcomed!

## Installation

Currently, there are two ways to install OctoTools. For most use cases, [standard installation](https://github.com/octotools/octotools?tab=readme-ov-file#1-standard-installation) would suffice. However, to replicate the [benchmarks](https://github.com/octotools/octotools/tree/main/tasks) mentioned in the original paper and to make your own edits to the code, you would need to several bash scripts from Github. An [editable installation](https://github.com/octotools/octotools?tab=readme-ov-file#2-editable-installation) is recommended.

### 1. Standard Installation

Create a conda environment and install the dependencies:

```sh
conda create -n octotools python=3.10
conda activate octotools
# Alternatively, you can use: `source activate octotools` if the above command does not work
pip install octotoolkit
```

Make `.env` file, and set `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CX`, etc. For example:

```sh
# The content of the .env file

# Used for LLM-powered modules and tools
OPENAI_API_KEY=<your-api-key-here> # If you want to use OpenAI LLM
FORGE_API_KEY=<your-api-key-here> # If you want to use Forge LLM (OpenAI-compatible)
FORGE_API_BASE=https://api.forge.tensorblock.co/v1 # Optional custom Forge base URL
ATLASCLOUD_API_KEY=<your-api-key-here> # If you want to use Atlas Cloud LLMs
ATLASCLOUD_API_BASE=https://api.atlascloud.ai/v1 # Optional custom Atlas Cloud base URL
ANTHROPIC_API_KEY=<your-api-key-here> # If you want to use Anthropic LLM
TOGETHER_API_KEY=<your-api-key-here> # If you want to use TogetherAI LLM
DEEPSEEK_API_KEY=<your-api-key-here> # If you want to use DeepSeek LLM
GOOGLE_API_KEY=<your-api-key-here> # If you want to use Gemini LLM
XAI_API_KEY=<your-api-key-here> # If you want to use Grok LLM

# Used for the Google Search tool
GOOGLE_API_KEY=<your-api-key-here>
GOOGLE_CX=<your-cx-here>

# Used for the Advanced Object Detector tool (Optional)
DINO_KEY=<your-dino-key-here>
```

Obtain a Google API Key and Google CX according to the [Google Custom Search API](https://developers.google.com/custom-search/v1/overview) documentation and [Programmable Search Engine Page](https://programmablesearchengine.google.com/controlpanel/all). More details are available in the [Google Search Tool](https://github.com/octotools/octotools/tree/main/octotools/tools/google_search/doc/readme.md) documentation.


### 2. Editable Installation

Start with a fresh new environment:
```sh
conda create -n octotools python=3.10
conda activate octotools
```

Clone the [github repo](https://github.com/octotools/octotools):
```sh
git clone https://github.com/octotools/octotools.git
```

In the root directory (the directory that contains ``pyproject.toml``), run the following command:
```sh
pip install -e .
```

(Optional) Install `parallel` for running benchmark experiments in parallel:

```sh
sudo apt-get update
sudo apt-get install parallel
```

## Quick Start

In a brand new folder, paste the following code to set the API keys:
```py
# Remember to put your API keys in .env
import dotenv
dotenv.load_dotenv()

# Or, you can set the API keys directly
import os
os.environ["OPENAI_API_KEY"] = "your_api_key"
```

Then, paste the following code to test the default solver:
```py
# Import the solver
from octotools.solver import construct_solver

# Set the LLM engine name
llm_engine_name = "gpt-4o"

# Construct the solver
solver = construct_solver(llm_engine_name=llm_engine_name)

# Solve the user query
output = solver.solve("What is the capital of France?")
print(output["direct_output"])

# Similarly, you could pass in a photo
output = solver.solve("What is the name of this item in French?", image_path="<PATH_TO_IMG>")
print(output["direct_output"])
```

You should be able to see the output at the end, along with all the intermediate content.

More detailed jupyter notebook examples are available in the [examples/notebooks](https://github.com/octotools/octotools/tree/main/examples/notebooks) folder.

## Test Tools in the Toolbox (Need Test Scripts from Github)

Using `Python_Code_Generator_Tool` as an example, test the availability of the tool by running the following:

```sh
cd octotools/tools/python_code_generator
python tool.py
```

Expected output:

```
Execution Result: {'printed_output': 'The sum of all the numbers in the list is: 15', 'variables': {'numbers': [1, 2, 3, 4, 5], 'total_sum': 15}}
```

You can also test all tools available in the toolbox by running the following:

```sh
cd octotools/tools
source test_all_tools.sh
```

Expected testing log:

```
Testing advanced_object_detector...
✅ advanced_object_detector passed

Testing arxiv_paper_searcher...
✅ arxiv_paper_searcher passed

...

Testing wikipedia_knowledge_searcher...
✅ wikipedia_knowledge_searcher passed

Done testing all tools
Failed: 0
```

## Run Inference on Benchmarks (Need Bash Scripts from Github)

Using [CLEVR-Math](https://huggingface.co/datasets/dali-does/clevr-math) as an example, run inference on a benchmark by:

```sh
cd octotools/tasks

# Run inference from clevr-math using GPT-4 only
source clevr-math/run_gpt4o.sh

# Run inference from clevr-math using the base tool
source clevr-math/run_octotool_base.sh

# Run inference from clevr-math using Octotools with an optimized toolset
source clevr-math/run_octotools.sh
```

More benchmarks are available in the [tasks](https://octotools.github.io/#tasks).


## Experiments


### Main results

To demonstrate the generality of our **OctoTools** framework, we conduct comprehensive evaluations on 16 diverse benchmarks spanning two modalities, five domains, and four reasoning types. These benchmarks encompass a wide range of complex reasoning tasks, including visual understanding, numerical calculation, knowledge retrieval, and multi-step reasoning.


<p align="center">
    <img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/result/result_table_1.png" width="100%">
    <!-- Text. -->
</p>


More results are available in the [paper](https://arxiv.org/pdf/2502.11271) or at the [project page](https://octotools.github.io/).


### In-depth analysis

We provide a set of in-depth analyses to help you understand the framework. For instance, we visualize the tool usage of **OctoTools** and its baselines  from 16 tasks. It turns out that **OctoTools** takes advantage of different external tools to address task-specific challenges. Explore more findings at our [paper](https://arxiv.org/pdf/2502.11271) or the [project page](https://octotools.github.io/#analysis).

<a align="center">
    <img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/result/tool_usage_ours_baselines.png" width="100%">
    <!-- Text. -->
</a>

### Example visualizations

We provide a set of example visualizations to help you understand the framework. Explore them at the [project page](https://octotools.github.io/#visualization).

<p align="center">
    <a href="https://octotools.github.io/#visualization">
        <img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/result/example_visualization.png" width="80%">
    </a>
</p>


## Customize OctoTools

The design of each tool card is modular relative to the **OctoTools** framework, enabling users to integrate diverse tools without modifying the underlying framework or agent logic. New tool cards can be added, replaced, or updated with minimal effort, making **OctoTools** robust and extensible as tasks grow in complexity.

<p align="center">
    <a href="https://octotools.github.io/#tool_cards">
        <img src="https://raw.githubusercontent.com/octotools/octotools/refs/heads/main/assets/models/tool_cards.png" width="100%">
    </a>
</p>

To customize **OctoTools** for your own tasks:

1. **Add a new tool card**: Implement your tool following the structure in [existing tools](https://github.com/octotools/OctoTools/tree/main/octotools/tools).

2. **Replace or update existing tools**: You can replace or update tools in the toolbox. For example, we provide the [`Object_Detector_Tool`](https://github.com/octotools/OctoTools/blob/main/octotools/tools/object_detector/tool.py) to detect objects in images using an open-source model. We also provide an alternative tool called the [`Advanced_Object_Detector_Tool`](https://github.com/OctoTools/OctoTools/blob/main/octotools/tools/advanced_object_detector/tool.py) to detect objects in images using API calls.

3. **Enable tools for your tasks**: You can enable the whole toolset or a subset of tools for your own tasks by setting the `enabled_tools` argument in [tasks/solve.py](https://github.com/octotools/OctoTools/blob/main/tasks/solve.py).


## Resources

### Inspiration

This project draws inspiration from several remarkable projects:

- 📕 [Chameleon](https://github.com/lupantech/chameleon-llm) – Chameleon is an early attempt that augments LLMs with tools, which is a major source of inspiration. A journey of a thousand miles begins with a single step.
- 📘 [TextGrad](https://github.com/mert-y/textgrad) – We admire and appreciate TextGrad for its innovative and elegant framework design.
- 📗 [AutoGen](https://github.com/microsoft/autogen) – A trending project that excels in building agentic systems.
- 📙 [LangChain](https://github.com/langchain-ai/langchain) – A powerful framework for constructing agentic systems, known for its rich functionalities.


### Citation
```bibtex
@proceedings{lu2026octotools,
    title={OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning},
    author={Lu, Pan and Chen, Bowen and Liu, Sheng and Thapa, Rahul and Boen, Joseph and Zou, James},
    booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL)},
    year={2026}
}
```

### Our Codebase Contributors
<table>
	<tbody>
		<tr>
            <td align="center">
                <a href="https://lupantech.github.io/">
                    <img src="https://avatars.githubusercontent.com/u/17663606?v=4" width="100;" alt="lupantech"/>
                    <br />
                    <sub><b>Pan Lu</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://bowen118.github.io/">
                    <img src="https://bowen118.github.io/assets/img/prof_pic.jpg" width="100;" alt="bowen118"/>
                    <br />
                    <sub><b>Bowen Chen</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://shengliu66.github.io/">
                    <img src="https://shengliu66.github.io/profile.jpg" width="100;" alt="shengliu66"/>
                    <br />
                    <sub><b>Sheng Liu</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://rthapa84.github.io/">                    <img src="https://rthapa84.github.io/assets/img/prof_pic.jpg" width="100" alt="rthapa84"/>
                    <br />
                    <sub><b>Rahul Thapa</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://tonyxia2001.github.io/">                    <img src="https://tonyxia2001.github.io/img/photo.png" width="100" alt="tonyxia2001"/>
                    <br />
                    <sub><b>Tony Xia</b></sub>
                </a>
            </td>
            <!-- <td align="center">
                <a href="https://dbds.stanford.edu/people/joseph-boen/">
                    <img src="https://dbds.stanford.edu/wp-content/uploads/2023/08/joseph-boen.jpg)" width="100;" alt="josephboen"/>
                    <br />
                    <sub><b>Joseph Boen</b></sub>
                </a>
            </td>
            <td align="center">
                <a href="https://www.james-zou.com/">
                    <img src="https://static.wixstatic.com/media/0f3e8f_cfa7e327b97745ddb8c4a66454b5eb3e~mv2.jpg/v1/fill/w_318,h_446,al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/46824428A5822_ForWeb.jpg" height="100;" alt="jameszou"/>
                    <br />
                    <sub><b>James Zou</b></sub>
                </a>
            </td> -->
		</tr>
	<tbody>
</table>


### Contributors

We are truly looking forward to open-source contributions to OctoTools! If you are interested in contributing, collaborating, or reporting issues, don't hesitate to contact us at [panlu@stanford.edu](mailto:panlu@stanford.edu) or join our Slack channel [OctoTools](https://join.slack.com/t/octotools/shared_invite/zt-36giqfe7o-Ai8CuDOUsGN3EiLMyKzCrw).

We are also looking forward to your feedback and suggestions!

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=octotools/octotools&type=Date)](https://www.star-history.com/#octotools/octotools&Date)

<p align="right" style="font-size: 14px; color: #2176bc; margin-top: 20px;">
  <a href="#readme-top" style="text-decoration: none; color: blue; font-weight: bold;">
    ↑ Back to Top ↑
  </a>
</p>
