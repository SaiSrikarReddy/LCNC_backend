from run_llm_query import process_model_IO_google_family

prompt = """I am making an AI based system to assist humans that has many subsystems. Each subsystem will first be given an instructional text prompt, and based on that prompt and user input, that subsystem will respond to user queries. The instructional prompt will define a JSON structure and mandatory JSON keys/key combinations that the subsytem's response must include. However sometimes the output will not adhere to this JSON format, and hence, I need to write a validation and processing function for each subsystem. For example, for a subsystem with this instructional prompt:
###Prompt begins###
You are a subpart of a highly advanced AI brain. You take in text inputs from people ('users') talking to the AI, and some conversation context, and pre-process them. Your task is to read the given text input, and decide whether the users (1) are continuing a conversation or asking information from the current document or want to edit the current document, (2) are asking for something related to what documents they have (a full or partial list of documents they have, whether a particular document exists, or if they have a certain document (yet) or what documents they have, etc.), (3) want to set/get a (or a list of) reminder / to-do item, (4) want to switch to talking about another topic (or 'document'), or create a new document which may or may not be based on a "template", or (5) are asking an unrelated question / trying to have an unrelated / casual conversation (or are continuing a conversation from recent messages which is unrelated to the current document/topic (also if current document topic title is None, this is the correct category)). You will output ONLY a JSON string (with bools true and false, NO capital letters, and property names enclosed in double quotes) (and nothing else- nothing before or after it) as follows: example output: {"continue_conversation_get_set_info":true,"list_docs":false,"get_set_reminder_todo":false,"switch_create_conversation_document":false,"unrelated_general":false}
Note that you MUST set one (and only one) of the bools to true (the most likely one), and if this is the first message in the conversation(i.e. there are no messages in latest messages) or if current document topic title is None, continue conversation cannot be true
###prompt ends###
The following python function is the validation function:
```python
def validate_and_process(self,model_output_and_metadata):
    try:
      model_output = model_output_and_metadata['llm_output'] 
      #print(model_output)
      '''should be a json string of spec :
            {
            "continue_conversation_get_set_info":true,
            "list_docs":false,
            "get_set_reminder_todo":false,
            "switch_create_conversation_document":false,
            "unrelated_general":false
            }
          with only one of three values being true
      '''
      model_output_dict = json.loads(model_output)
      #print(model_output_dict)
      if (model_output_dict['continue_conversation_get_set_info'] + 
          model_output_dict['list_docs'] +
          model_output_dict['get_set_reminder_todo'] + 
          model_output_dict['switch_create_conversation_document'] +
          model_output_dict['unrelated_general'] == 1
         ):
        return {
                'valid_output':True,
                'processed_output':model_output_dict
               }
      else:
        return {'valid_output':False, "error":"output is JSON, but output conditions not met"}
    except Exception as error:
      return {'valid_output':False, 'error':error}
```

Now write a python validation function for a subsystem with the following instructional prompt (only write the code and nothing else before or after it):
###########prompt begins############
You are a highly intelligent AI assistant, who is concise, understands what is important for sales and for business, and are consistently rated as the best creator of executive summaries of marketing and sales materials and pitch decks for executives who have little time but need the big picture as well as every numerical detail perfectly summarized in a short and sweet manner for them.
Your current task is to take in the given text, which is an excerpt from the marketing materials of Tata Consultancy Services, a tech consulting firm, and based on the text, return the following json output (STRICTLY follow the json format given below):
{"article-title":"Short descriptive title","company-partnered":"Company that TCS partnered with (or client name), if any", "date":"Date, if mentioned in text", "deal value":"Deal value, if mentioned in text","largest-monetary-value":"largest monetary value mentioned in text, if any","geography":"location talked about in text, if mentioned","summary of webpage":"A summary of the text, upto 10 sentences long, must include all the headline numbers in the text, so that it can be presented to a CEO who wants to make a deal based on this information"}
Remember that you must strictly follow the above json template, and you must set any values that don't exist in the text to Null.
##########prompt ends##########"""

response = process_model_IO_google_family(human_message=prompt,
                                          system_message=None)

print(response["llm_output"])
