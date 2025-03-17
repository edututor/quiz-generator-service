class Agent:
    def __init__(self, name, role, function, query='None') -> None:
        self.role: str = role
        self.name: str = name
        self.function: str = function
        self.query: str = query

    def set_max_tokens(self, summary_token_target):
        self.function.format(summary_token_target=summary_token_target)

    def prompt(self, input_prompt):
        system_prompt = f"You are a: {self.name}. Your role is: {self.role}. Your function is: {self.function}. Based on your role and function, do the task you are given. Do not give me anything else other than the given task"

        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": input_prompt}]


class MathTutorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Math AI Tutor",
            role="An AI math tutor that explains concepts and solves math problems for students.",
            function=(
                "Your job is to help students with math problems. "
                "You should explain concepts, solve equations step-by-step, "
                "and provide clear, structured explanations. "
                "If the question involves a formula, show how to apply it. "
                "Be patient and break complex ideas into simpler parts."
            )
        )


# Quiz generator agent:
quiz_generator_agent = Agent(
    name="Quiz Generator Agent",
    role=(
        "You are an educational quiz-generation agent that creates quizzes "
        "to assess a student's understanding of the provided chunks of text."
    ),
    function=(
        "Your function is to analyze each provided chunk of text or data and "
        "transform it into a set of 10 to 20 quiz questions. You must take into consideration"
        "the USER QUERY to better understand what kind of questions you should generate."
        "You can use your own knowledge of the topic if necessary to enhance the quality of the quiz"
        "Each question must include: "
        "1) A single question text. "
        "2) A list of possible answers, each containing an 'answer' string "
        "   and a boolean 'is_correct_answer'. "
        "3) A short 'hint' to guide the student toward the correct answer. "
        "Generate at least one multiple-choice question and at least one true/false question. "
        "Avoid unrelated details and ensure the questions focus on assessing "
        "the student's knowledge of the provided material."
        "Assign a meaningful name to the quiz"
    )
)

# Math generator agent 
math_tutor_agent = MathTutorAgent()
