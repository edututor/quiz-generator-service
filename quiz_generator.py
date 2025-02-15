from loguru import logger
from schemas import AnalysisResponseSchema
from agents import quiz_generator_agent


class Analyzer:

    def __init__(self, article_index, text_index, table_index):
        self.article_index = article_index
        self.text_index = text_index
        self.table_index = table_index

    def generate_quiz(self, client, vector_manager, company_name):

        analysis = []
        sources = set()
        tables = set()
        
        for agent in analysis_agents:

            corpora = []
            try:
                # Generate embeddings for the agent query
                logger.info(f"Generating embeddings for agent: {agent.name}")
                query_embeddings = vector_manager.vectorize(client, agent.query)

                # Retrieve top-k results from each index with a filter for company_name
                logger.info(f"Retrieving top-k relevant chunks for company: {company_name}")
                try:
                    article_results = self.article_index.query(
                        vector=query_embeddings,
                        top_k=5,
                        filter={"company_name": {"$eq": company_name}},
                        include_metadata=True
                    )["matches"]

                    text_results = self.text_index.query(
                        vector=query_embeddings,
                        top_k=15,
                        filter={"company_name": {"$eq": company_name}},
                        include_metadata=True
                    )["matches"]

                    table_results = self.table_index.query(
                        vector=query_embeddings,
                        top_k=5,
                        filter={"company_name": {"$eq": company_name}},
                        include_metadata=True
                    )["matches"]

                    # Combine results
                    related_chunks = article_results + text_results + table_results
                    logger.success(f"Total related chunks received: {len(related_chunks)}")
                except Exception as e:
                    logger.error(f"An error occurred while querying indexes: {e}")
                    related_chunks = []

                # Process chunks and append to corpora
                for result in related_chunks:
                    metadata = result.metadata

                    if metadata["type"] == "document-text":
                        corpora.append(metadata["chunk"])
                    elif metadata["type"] == "table":
                        # Append all table fields to corpora
                        corpora.append(f"Table Name: {metadata['table_name']}")
                        corpora.append(f"Table Columns: {', '.join(metadata['table_columns'])}")
                        corpora.append(f"Table Rows: {metadata['table_rows']}")

                        # Add relevant table metadata to the tables set
                        table_entry = (
                            metadata["table_name"],
                            tuple(metadata["table_columns"]),
                            metadata["table_rows"],  # This can remain as a string if needed
                        )
                        tables.add(table_entry)
                    elif metadata["type"] == "article":
                        corpora.append(metadata["summary"])

                    # Append sources to the sources set
                    if "document_name" in metadata:
                        document_name = metadata["document_name"]
                    elif "title" in metadata:
                        document_name = metadata["title"]
                    else:
                        document_name = "Unknown Document"
                    
                    if "published_date" in metadata:
                        date = metadata["published_date"]
                    elif "upload_date" in metadata:
                        date = metadata["upload_date"]
                    else:
                        date = "Unknown Document"

                    sources.add((document_name, date))

                logger.info(f"Sources length: {len(sources)}")

            except Exception as e:
                logger.error(f"An error occurred while generating vectors or retrieving chunks: {e}")


            try:
                # Prompting ChatGPT with corpora
                logger.info("Prompting ChatGPT")
                
                # Convert corpora (list of chunks) to a single string
                formatted_corpora = "\n\n".join(corpora)  # Separate chunks with double newlines for readability

                # Create the prompt using the agent's method
                prompt = agent.prompt(formatted_corpora)

                # Query ChatGPT with the constructed prompt
                response = client.query_gpt(prompt, AnalysisResponseSchema)
                logger.success("Response received from ChatGPT")

                # Append the response to the analysis
                analysis.append({"Agent": agent.name, "Analysis": response.analysis})

            except Exception as e:
                logger.error(f"An error occurred while querying ChatGPT: {e}")

        return {
            "analysis": analysis,
            "sources": list(sources),
            "tables": list(tables)
        }
