# Do Language Models Follow Occam's Razor? An Evaluation of Parsimony in Inductive and Abductive Reasoning



Yunxin Sun, [Abulhair Saparov](https://asaparov.org/)

**EMNLP 2026** | [ACL Anthology](https://aclanthology.org/2026.emnlp-main.2439.pdf) | [arXiv](https://arxiv.org/abs/2509.03345)


## Overview

Non-deductive reasoning, encompassing inductive and abductive reasoning, is essential in addressing complex real-world questions. One key feature of inductive and abductive reasoning is that there are many valid hypotheses; the simplest ones (those that adhere to Occam's Razor) are often most useful. However, this aspect is ignored in recent work that evaluates the non-deductive reasoning capabilities of large language models (LLMs). This work fills this gap, focusing on understanding whether the inductive and abductive reasoning capabilities of LLMs adhere to Occam's Razor, while also examining the correctness of their reasoning. To accomplish this goal, we introduce a framework to synthetically generate reasoning questions that (a) require inductive reasoning and abductive reasoning simultaneously; (b) is readily extended to produce any abductive/inductive reasoning question expressible in first-order logic. The task for the intelligent agent is to produce hypotheses to explain observations under a given world model. We also propose a new automated metric to assess whether hypotheses quantitatively adhere to Occam's Razor; those hypotheses that are correct and simplest are considered high-quality. Our findings on state-of-the-art LLMs suggest that LLMs can perform inductive and abductive reasoning in simple scenarios, but struggle with complex world models and with producing high-quality hypotheses, even with popular reasoning-enhancing techniques such as in-context learning and RLVR.
## Citation

If you find this work useful, please consider citing:

```bibtex
@inproceedings{DBLP:conf/emnlp/SunS26,
  author       = {Yunxin Sun and
                  Abulhair Saparov},
  title        = {Do Language Models Follow Occam's Razor?
                  An Evaluation of Parsimony in Inductive
                  and Abductive Reasoning},
  booktitle    = {Proceedings of the 2026 Conference on Empirical
                  Methods in Natural Language Processing,
                  {EMNLP} 2026},
  pages        = {55345--55366},
  publisher    = {Association for Computational Linguistics},
  year         = {2026},
  url          = {https://aclanthology.org/2026.emnlp-main.2439/}
}
```
