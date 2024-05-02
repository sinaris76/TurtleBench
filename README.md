# TurtleBench: A Visual Programming Benchmark in Turtle Geometry
![Static Badge](https://img.shields.io/badge/Task-MultiModal-red)
![Static Badge](https://img.shields.io/badge/Task-Image_to_Code-red)
![Static Badge](https://img.shields.io/badge/Task-Visual_Reasoning-red)
![Static Badge](https://img.shields.io/badge/Benchmark-TurtleBench-blue)

![Static Badge](https://img.shields.io/badge/Model-GPT4--V-green)
![Static Badge](https://img.shields.io/badge/Model-Gemini_1.0_pro-green)

Code for the paper [TurtleBench: A Visual Programming Benchmark in Turtle Geometry]()


<p align="center">
  <img src="figs/turtle.png" />
</p>

## About TurtleBench
There has been a surge of interest in leveraging Large Multimodal Models (LMMs) for code generation, with the ambitious goal of creating a fully automated AI software engineer. A critical and useful skill required for such an AI is the ability to translate visual contexts into executable code. Yet, despite the remarkable successes of LMMs in diverse domains, their ability to do such tasks has not been systematically studied. To address this gap, we introduce TurtleBench, a manually crafted benchmark designed specifically to evaluate the capacity of LMMs to interpret example images of the desired output, textual instructions, or a combination of both and apply this understanding to generate code as the output. This evaluation task is grounded in turtle geometry, a graphical mode of programming that is widely used as an educational tool for children. Successfully completing tasks in TurtleBench demands a combination of skills: visual comprehen- sion to understand the input as an image, logical reasoning to decipher the task, geometric reasoning to understand relations between shapes, and programming skills to precisely replicate the input through code. Using TurtleBench, we conduct a thorough quantitative evaluation of leading foundational models, and show that they heavily struggle to solve our tasks with the top performer model (GPT4-V) only achieving an overall accuracy of 19% in the simplest subset of TurtleBench. Our findings reveal that models show a substantial 44% improvement when given textual instructions over image inputs, underscoring their difficulty in comprehending simple geometric shapes. However, even in textual mode, LMMs continue to fall short of accomplishing the task. TurtleBench stands as one of the few benchmarks to evaluate the integration of visual understanding and code generation capabilities in LMMs, setting the stage for future research.


![photo](figs/intro.png)

## Benchmark Format
The structure of the files in the `Tasks` directory is as follows:
```
├── {id}
│   ├── QA
│   │   ├── code
│   │   │   ├── q1_code.txt
│   │   │   ├── q2_code.txt
│   │       │
           ...
│   │   └── text
│   │       ├── q1.txt
│   │       ├── q2.txt
│   │       │
           ...
│   ├── description.txt
│   ├── image
│   │   └── {id}.png
│   ├── result_image
│   │   ├── q1_image.png
│   │   ├── q2_image.png
│   │   │
│   │   │
    │   ...  
│   └── variables.txt
│
```
Each directory includes a set of tasks including a base image and queries for different tweak tasks. For consistency of the code provided by the models, the variables needed to create shapes are provided in `variables.txt` file. For instance, for task 1, this file only contains: 
```
radius=100
```
A task may or may not include `description.txt`. This file contains a text description of the base image (`image/{id}.png`).

In each task, `QA/text/q{i}.txt` for $i > 1$ indicates the `i`th tweak task on the base shape. Accordingly, `QA/text/q1.txt` does not include specific queries, it only includes: "create the exact same shape."

You can add new tasks to the benchmark by adding new folders in `Tasks` directory, where `id` indicates the number of the new task. 

All tasks are included in `dataset.jsonl` file, which includes all the necessary informations for the evaluation. If you add a new task, you need to run `crawl_tasks.py` file to update the dataset file for the evaluation. 

## Prompting
All the prompts used for the evaulation are available in the `prompts.py` file. You can try new prompts by adding to `system_prompt' dictionary in this file.

## Evaluation
by running the following script, you can run an evaluation on the model of your choice (current options: GPT4-V and Gemini 1.0 Pro).
It runs the model on the part of benchmark (based on the `task_type` and `task_mode` variables) and reports the accuracy of the model.

```
python eval.py 
  --model_name # default: gemini, options: gemini and gpt4-v
  --task_type  # default: scratch, options: scratch and tweak
  --task_mode  # default: code_generation, options: code_generation and code_edit
  --modalities # default: image_only, options: "image_only", "text_only", "image+text", and "image+image".
  --prompting_mode # default: cot, options: cot and basic
  --save_responses # use this option if you want to save the models' responses in .responses/ directory, if you do not use this argument, it will not store responses
```

## Stay in Touch
Feel free to open merge requests for enhancing TurtleBench.
For any questions, comments and discussions please reach out to me at [srismanc@uci.edu](mailto:srismanc@uci.edu)

## Contributors
This work is done by: [Sina Rismahchian](mailto:srismanc@uci.edu), [Yasaman Razeghi](https://yasamanrazeghi.com/), [Sameer Singh](https://sameersingh.org/), [Shayan Doroudi](https://sites.google.com/uci.edu/shayan-doroudi) at University of California, Irvine