from loguru import logger

class VectorManager:

    def __init__(self, embeddings=None):
        """
        Initialize with the precomputed embeddings dictionary.
        """
        self.embeddings = embeddings
        

    def vectorize(self, client, corpus):

        logger.info("Querying to get embeddings")

        # Generate embeddings
        try:
            embedings_response = client.generate_embeddings(corpus)

            # Extract only embeddings from the response
            embedings = [item.embedding for item in embedings_response.data]
            logger.success("Embeddings received and processed")
            return embedings
        
        except Exception as e:
            logger.error(f"An error occured while qurying OpenAI's Embedding Generator")

    def get_chunks(self, text_index, document_name, query_embeddings):

        # Retrieve top-k results from each index with a filter for document_name
        try:
            logger.info(f"Retrieving top-k relevant chunks for company: {document_name}")
            chunks = text_index.query(
                vector=query_embeddings,
                top_k=15,
                filter={"document_name": {"$eq": document_name}},
                include_metadata=True
            )["matches"]

            joined_chunks = ""
            for chunk in chunks:
                metadata = chunk.metadata
                joined_chunks += metadata["chunk"] + "\n\n"

            return joined_chunks

        except Exception as e:
                logger.error(f"An error occurred while querying indexes: {e}")
