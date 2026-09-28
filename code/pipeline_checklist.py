import json, yaml

from openai import OpenAI

class PipeLine():

    def prompt(self, system_message: str, user_message: str, seed: int = 42, schema: dict = None, schema_name: str = "response"):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        client = OpenAI(api_key=config['API_KEY'])
        kwargs = dict(
            model="gpt-4.1-mini",
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message}
            ],
            temperature=0,
            seed=seed
        )
        if schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "strict": True, "schema": schema}
            }
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return json.loads(content) if schema is not None else content

    def process_answer(self, question: str, model_answer: str, learner_answer: str, processed_model_answer: list=None, experiment_istudio: bool=False, seed: int=42):
        prompt_text = """
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
"""
        if not processed_model_answer:
            concepts = self.prompt(prompt_text, f"question: {question}\nreference_answer: {model_answer}", seed=seed)
            # concepts = ast.literal_eval(concepts.strip().replace('\n', ''))
            prompt_text = """
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
"""
            step2_output = self.prompt(prompt_text, f"question: {question}\nreference_answer: {model_answer}, concepts: {concepts}", seed=seed)
            # step2_output = ast.literal_eval(step2_output.strip().replace('\n', ''))
            prompt_text = """
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
Each rubric item must include exactly four keys:
1. title (2-4 words)
2. description: One sentence beginning with its category prefix, explicitly stating what to look for.
3. weight: For Essential/Important/Optional, use 3-5 (5 = most important)
4. checklist: A list of specific concise points to check for when evaluating the student answer against this criterion.
Each point should be a concise concept of a key fact, reasoning step, or explanation that should be present in the
student answer to meet this criterion.

**Category guidance:**
- Essential: Critical facts or safety checks; omission invalidates the response.
- Important: Key reasoning or completeness; strongly affects quality.

**Format notes:**
- When referring to answer choices, explicitly say "Identifies (A)", "Identifies (B)", etc.
- Each criterion must be self-contained and not check for more than one concept at a time.
- If a clear conclusion is required, include an Essential Criteria for it.
- If the reference_answer were to be evaluated according to the generated rubric, it should score full marks.

**Output:**
Provide an array of rubric objects. Each object must contain exactly four keys: title, description, weight, and checklist.
Do not copy large blocks of the question or reference_answer into the text. Each description must begin with its category
prefix, and no extra keys are allowed.
"""
            rubric_schema = {
                "type": "object",
                "properties": {
                    "rubrics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "weight": {"type": "integer"},
                                "checklist": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["title", "description", "weight", "checklist"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["rubrics"],
                "additionalProperties": False
            }
            rubrics = self.prompt(prompt_text, f"question: {question}\nreference_answer: {model_answer}\nconcepts: {step2_output}", seed=seed, schema=rubric_schema, schema_name="rubrics")["rubrics"]
            step3_output = [rubric for rubric in rubrics if rubric['weight'] >= 4]
        else:
            step2_output, step3_output = processed_model_answer
        if experiment_istudio:
            return step3_output
        step4_output = learner_answer
        step5_output = step4_output
        prompt_text = """
You are an evaluator for science questions in the domains of Biology, Physics, and Chemistry.

**Inputs:**
- question: The examiner's question text.
- rubric: A set of evaluation criteria.
- student_answer: The student's written response.

**Objective:**
Evaluate whether the student demonstrates precise understanding of each checklist item.
Award (partial) credit for each rubric item based on how well the student's answer meets the checklist criteria.
Each checklist item should be evaluated independently, as either Python 'True' or 'False'.
The rubric examples show one way to express each idea, but equivalent explanations deserve equal credit.
Final credit awarded per criteria should always be between 0 (zero) and 1 (one).

**Format notes:**
- Base all judgments strictly on biological correctness.
- Do not include explanations or extra text.

**Output:**
Return a dictionary object: {"criterion1": (0.8, {"checklist1": True, "checklistn": False})}
"""
        eval_schema = {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "score": {"type": "number"},
                            "checklist_results": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item": {"type": "string"},
                                        "met": {"type": "boolean"}
                                    },
                                    "required": ["item", "met"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["title", "score", "checklist_results"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["evaluations"],
            "additionalProperties": False
        }
        step6_output = self.prompt(prompt_text, f"question: {question}\nrubric_items: {step3_output}\nlearner_answer: {step5_output}", seed=seed, schema=eval_schema, schema_name="evaluation")
        evaluations = step6_output["evaluations"]
        justifications = {item["title"]: {c["item"]: c["met"] for c in item["checklist_results"]} for item in evaluations}
        rubric_scores = {item["title"]: item["score"] for item in evaluations}
        rubric_scores = [{**rubric, "score": rubric_scores.get(rubric["title"], None)} for rubric in step3_output]
        rubric_scores = [rubric for rubric in rubric_scores if rubric["score"] is not None]
        total_weight = sum(rubric["weight"] for rubric in rubric_scores)
        score = sum(rubric["weight"] * rubric["score"] for rubric in rubric_scores) / total_weight * 100 if total_weight > 0 else 0
        return step6_output, score, justifications, step2_output, (step2_output, step3_output)
