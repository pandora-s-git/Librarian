# Librarian
Originally a personal project, I would like everyone to have fun and contribute to this small idea.  
The goal is simple, make a Discord Bot that has access to all files and information inside a discord server and answer the users questions.

## Explanations
To achieve this, we will require RAG, or Retrieval Augmented Generation.

For now, I'm using embeddings and vectors to compute the best documents and score them depending on the query of the user.  
Once the documents collected, we filter them depending on a score threshold, some pass, others don't, and those in between get summarized.

I will make some tools to open and read different kind of files ! Feel free to give ideas and make tools urself !

The LLM that answers is for now Mixtral, as I did not have a powerfull computer to run an LLM good enough, I'm using a free API from hugging face, you can insert your own access token !!

You can fork the project and work on ur own, make branches, make pull requests, or just tell me the idea and I will work on it !

## How to use
You first require an Access Token from HuggingFace.  
For that you create an account -> Settings -> Access Tokens.  
If you want to test it on your own, you need to create a discord bot on the [discord's developers portal](https://discord.com/developers/applications).  
Then you create a new application and bot. (Do not forget to toggle all intents !!)  
Once it's done, you can invite the bot to ur discord server:  
`https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=0&scope=bot%20applications.commands`  
To run the code, you can just open the project on VSCode (or another IDE) and run bot.py, then you insert the Access token from Hugging Face and the Bot Token available on the developers portal.

## A small Demo of what it can do
It was provided with a PDF file about KG and LLMs among other channels with different documents.  
![alt text](demo.PNG)