from loguru import logger


class QuizGenerator:

    def __init__(self):
        pass

    def generate_quiz(self, user_query, chunks, agent, schema, client):

        try:
                # Prompting ChatGPT with corpora
                logger.info("Prompting ChatGPT")     

                formatted_input = chunks + "\n\n".join(user_query)           

                # Create the prompt using the agent's method
                prompt = agent.prompt(formatted_input)

                # Query ChatGPT with the constructed prompt
                response = client.query_gpt(prompt, schema)
                logger.success("Response received from ChatGPT")

                # Return response
                return response

        except Exception as e:
            logger.error(f"An error occurred while querying ChatGPT: {e}")
