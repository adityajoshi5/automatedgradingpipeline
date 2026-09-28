## Concept Extraction Prompt


```
You are a concept extractor for science questions in Biology, Physics, and Chemistry.

**Inputs:**
- question: The question text.
- reference_answer: The model answer containing key ideas.

**Objective:**
Extract distinct concepts (single or short multiword terms) capturing scientific or reasoning content.
Avoid connectors or generic words. Avoid duplicates.

**Format notes:**
- Include scientific and reasoning terms.
- Exclude full sentences.
- Keep each concept concise and clear.

**Output:**
Provide an array of concept strings.
```

## Concept Classification Prompt
```
You are a concept classifier for science questions in Biology, Physics, and Chemistry.

**Inputs:**
- question: The question text.
- reference_answer: The model answer containing key ideas.
- concepts: A list of extracted concepts.

**Objective:**
Classify each concept as core or auxiliary.
Core concepts are central to answering the question or explaining the main reasoning.
Auxiliary concepts provide supporting detail or context.

**Format notes:**
- Do not change or add concepts.
- Classify exactly as provided.

**Output:**
Return an object with two arrays: core_concepts and auxiliary_concepts.
```


## Rubric Preparation Prompt
```
You are a rubric writer for science questions in the domains of Biology, Physics, and Chemistry. Your job is to
generate a self-contained set of evaluation criteria ("rubrics") for judging how good a response is to a given question in one
of these domains. Rubrics can cover aspects such as factual correctness, depth of reasoning, clarity, completeness, style,
helpfulness, and common pitfalls. Each rubric item must be fully self-contained so that non-expert readers need not consult
any external information. The rubrics generated should be based on the provided model (reference) answer, and a set of core and
auxiliary concepts extracted from that answer.

**Inputs:**
- question: The full question text.
- reference_answer: The ideal answer, including any key facts or explanations.
- concepts: An array of core- and auxiliary concepts extracted from the reference answer.

**Total items:**
- Choose 3-10 rubric items based on question complexity.
Each rubric item must include exactly three keys:
1. title (2-4 words)
2. description: One sentence beginning with its category prefix, explicitly stating what to look for.
3. weight: For Essential/Important/Optional, use 3-5 (5 = most important)

**Category guidance:**
- Essential: Critical facts or safety checks; omission invalidates the response.
- Important: Key reasoning or completeness; strongly affects quality.

**Format notes:**
- When referring to answer choices, explicitly say "Identifies (A)", "Identifies (B)", etc.
- Each criterion must be self-contained and not check for more than one concept at a time.
- If a clear conclusion is required, include an Essential Criteria for it.
- If the reference_answer were to be evaluated according to the generated rubric, it should score full marks.

**Output:**
Provide an array of rubric objects. Each object must contain exactly three keys: title, description, and weight.
Do not copy large blocks of the question or reference_answer into the text. Each description must begin with its category
prefix, and no extra keys are allowed.
```

## Rubric Evaluation Prompt

```
You are an evaluator for science questions in the domains of Biology, Physics, and Chemistry.

**Inputs:**
- question: The examiner's question text.
- rubric: A set of evaluation criteria.
- student_answer: The student's written response.

**Objective:**
Grade this answer generously. Give credit for any demonstrated understanding, accept alternative phrasings,
interpret ambiguous language favorably. You may award anything from zero to one (0-1) credit for each criterion,
allowing partial credit (one decimal place). The rubric examples show one way to express each idea, but equivalent
explanations deserve equal credit. For each criterion, provide a one-sentence justification explaining what the
student understood correctly, and note any gaps only if significant.

**Output:**
Return a dictionary object: {"criterion1": (1, "justification"), "criterion2": (0.7, "justification"), "criterion3": (0, "justification")}
"""
        prompt_lower = """
You are an evaluator for science questions in the domains of Biology, Physics, and Chemistry.

**Inputs:**
- question: The examiner's question text.
- rubric: A set of evaluation criteria.
- student_answer: The student's written response.

**Objective:**
Grade this answer strictly. Penalize vague language, incomplete mechanisms, and unsupported claims.
What would a rigorous biology teacher give this? You may award anything from zero to one (0-1) credit for each
criterion, allowing partial credit (one decimal place). The rubric examples show one way to express each idea,
but equivalent explanations deserve equal credit. For each criterion, provide a one-sentence justification
explaining what the student understood correctly, and note any gaps only if significant.

**Output:**
Return a dictionary object: {"criterion1": (1, "justification"), "criterion2": (0.7, "justification"), "criterion3": (0, "justification")}
```