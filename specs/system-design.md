# System Design — Pod Classifier

## Overview

This lab builds a **few-shot podcast episode classifier**. Given a podcast episode
description, the system assigns one of four labels:
`interview`, `solo`, `panel`, or `narrative`.

The classifier uses labeled examples you provide (Milestone 1) as the training signal —
directly in the prompt, not via weight updates. This is how few-shot learning works:
examples teach the model what each label means at inference time.

---

## Architecture

```
                 ┌─────────────────────────────────────────┐
                 │              app.py (Gradio UI)          │
                 │   Classify tab  │  Evaluate tab          │
                 └────────┬────────┴──────────┬─────────────┘
                          │                   │
                          ▼                   ▼
              ┌───────────────────┐  ┌──────────────────────┐
              │   classifier.py   │  │    evaluate.py        │
              │                   │  │                       │
              │ load_labeled_     │  │ run_evaluation()      │
              │   examples()      │  │ compute_accuracy()    │
              │                   │  │ compute_per_class_    │
              │ build_few_shot_   │  │   accuracy()          │
              │   prompt()        │  │ format_evaluation_    │
              │                   │  │   report()            │
              │ classify_         │  └──────────┬────────────┘
              │   episode()       │             │ calls classify_episode()
              └────────┬──────────┘             │
                       │                        │
                       ▼                        ▼
              ┌─────────────────────────────────────────────┐
              │              Groq LLM API                    │
              │   openai/gpt-oss-120b                        │
              │   Single chat completion per episode         │
              └─────────────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐   ┌─────────────────────┐
              │  data/           │   │  config.py           │
              │  train_episodes  │   │  VALID_LABELS        │
              │  test_episodes   │   │  GROQ_API_KEY        │
              │  my_labels.json  │   │  LLM_MODEL           │
              │  taxonomy.md     │   └─────────────────────┘
              └─────────────────┘
```

---

## Component Status

| Component | File | Status |
|---|---|---|
| Load + merge labeled examples | `classifier.py` | ✅ Complete |
| Build few-shot prompt | `classifier.py` | ⬜ TODO (Milestone 2) |
| Classify a single episode | `classifier.py` | ⬜ TODO (Milestone 2) |
| Run evaluation loop | `evaluate.py` | ✅ Complete |
| Compute overall accuracy | `evaluate.py` | ⬜ TODO (Milestone 3) |
| Compute per-class accuracy | `evaluate.py` | ⬜ TODO (Milestone 3) |
| Format evaluation report | `evaluate.py` | ✅ Complete |
| Gradio UI | `app.py` | ✅ Complete |

---

## How Few-Shot Classification Works

In traditional machine learning, you train a model on labeled examples to update its
weights. **Few-shot prompting** achieves a similar effect without weight updates:
you place labeled examples directly in the prompt, and the LLM uses them to infer the
classification pattern at inference time.

This lab makes that parallel explicit:

| ML concept | This lab's equivalent |
|---|---|
| Training data | `my_labels.json` + `train_episodes.json` |
| Training signal | Labeled examples in the prompt |
| Model | `openai/gpt-oss-120b` (weights fixed) |
| Inference | `classify_episode()` |
| Evaluation | `run_evaluation()` on held-out test set |
| Accuracy metric | `compute_accuracy()`, `compute_per_class_accuracy()` |

**Key insight:** The quality of your labels directly affects classifier performance —
just as the quality of training data affects a fine-tuned model.

---

## How the Groq Chat Completions API Works

Unlike the tool-calling API in Lab 2, this lab uses a single **chat completion**:

```python
response = _client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": prompt},
    ],
)
text = response.choices[0].message.content
```

The LLM reads the prompt — which includes your labeled examples and the new
description — and returns a text response. You then parse that response to extract
a label and reasoning.

**There are no tool calls, no multi-turn loops.** One prompt in, one response out.

---

## Data Flow: Classify Tab

```
User pastes description
        │
        ▼
load_labeled_examples()   ←── my_labels.json + train_episodes.json
        │
        ▼
build_few_shot_prompt(labeled_examples, description)
        │
        ▼
Groq API: openai/gpt-oss-120b
        │
        ▼
Parse response → {"label": "...", "reasoning": "..."}
        │
        ▼
Display in Gradio UI
```

## Data Flow: Evaluate Tab

```
Run Evaluation button clicked
        │
        ▼
load_labeled_examples()   ←── my_labels.json + train_episodes.json
        │
        ▼
For each episode in test_episodes.json:
    classify_episode(description, labeled_examples)
        │
        ▼
compute_accuracy(predictions, ground_truth)
compute_per_class_accuracy(predictions, ground_truth)
        │
        ▼
format_evaluation_report() → Markdown string → Gradio UI
```

---

## Design Decisions

**Why a single LLM call per episode (not multi-turn)?**
Classification is a stateless task — each description is independent. Multi-turn
conversation would add latency and complexity with no benefit.

**Why separate train and test sets?**
This mirrors standard ML evaluation practice. Training on the test set would give
misleadingly high accuracy. By keeping the test set held-out, your accuracy score
is an honest measure of how well your labels generalize.

**Why 20 training episodes instead of fewer?**
More diverse examples help the LLM learn the distinction between labels. With only
2–3 examples per class, edge cases (especially `panel` vs. `interview`) are harder
to resolve. 20 examples across 4 classes gives a richer signal.

**Why parse the LLM response as text instead of using function calling?**
This is intentional. Parsing plain text output is a realistic skill — LLMs don't
always return perfectly structured data, and knowing how to handle that gracefully
is part of building robust AI systems.
