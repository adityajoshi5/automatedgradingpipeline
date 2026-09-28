import yaml

from openai import OpenAI

class PipeLine():

    def prompt(self, system_message: str, user_message: str, seed: int = 42) -> str:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        client = OpenAI(api_key=config['API_KEY'])
        response = client.chat.completions.create(
            model="o3-mini",
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_message}
            ],
            seed=seed
        )
        return response.choices[0].message.content

    def process_answer(self, question: str, model_answer: str, learner_answer: str, processed_model_answer: list=None, experiment_istudio: bool=False, seed: int=42):
        system_prompt = "You are a helpful assistant. Provided is a Question, the Correct Answer and the Student Answer. Please grade the Student Answer with respect to the Correct Answer. Give a grade from 0 to 5. Comment only briefly on the answer."
        output = self.prompt(system_prompt, f"question: {question}\ncorrect_answer: {model_answer}\nstudent_answer: {learner_answer}", seed=seed)
        return output
