# nCloze
### Neural system for generating multiple-choice, cloze-style reading comprehension tests from text passages

[Demo](https://huggingface.co/spaces/ondovb/nCloze)

Citation:

    @inproceedings{ondov2024pedagogically,
      title={Pedagogically Aligned Objectives Create Reliable Automatic Cloze Tests},
      author={Ondov, Brian and Attal, Kush and Demner-Fushman, Dina},
      booktitle={Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)},
      pages={3961--3972},
      year={2024}
    }

### Repo map
- `nCloze.ipynb`: code for:
  - generating nCloze tests
  - vizualizing distractor objectives
  - setting hyperparameters
  - adding CDGP ([Chiang et al. 2022](https://doi.org/10.18653/v1/2022.findings-emnlp.429)) distractors for the paper baseline
- `Wang2023/`: Code to reproduce the `T5-multi` baseline from the paper, originally from [Wang et al. 2023](https://doi.org/10.18653/v1/2023.findings-acl.790).
  1. Download the [CLOTH](https://www.cs.cmu.edu/~glai1/data/cloth/) dataset.
  2. Run `PrepareClothForT2T.py`
  3. Run `Text2Text.ipynb`
- `Data/`
  - `exp-data.json`: CLOTH passages used for MTurk experiments, with distractors for all conditions.
  - `results.json`: Raw MTurk results
  - `parseResults.py`: Code to process results and compute correlations. Usage: `parseResults.py results.json`
- `dict-info.txt`: For checking word existence
- `dict-unix.txt`: For checking word existence
- `profanity.json`: For filtering profanity from distractors
