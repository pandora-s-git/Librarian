# Librarian
Originally a personal project, I would like everyone to have fun and contribute to this small idea.
The goal is simple, make a Discord Bot that has access to all files and information inside a discord server and answer the users questions.

To achieve this, we will require RAG, or Retrieval Augmented Generation.

For now, I'm using embeddings and vectors to compute the best documents and score them depending on the query of the user.
Once the documents collected, we filter them depending on a score threshold, some pass, others don't, and those in between get summarized.

I made some tools that allow the bot to also read the content from Google Docs and Google Sites, feel free to make new tools that would allow it to read other types ! (pdf and txt files for exampel !)

The LLM that answers is for now Mixtral, as I did not have a powerfull computer to run an LLM good enough, I'm using a free API from hugging face, you can insert your own access token !!
