import os
from replit.ai.modelfarm.google.language_models import TextGenerationModel, TextGenerationResponse
#replace above with:
#import vertexai
#from vertexai.language_models import TextGenerationModel
#vertexai.init(project=project_id, location=location)

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage


def run_llm_query(user_message,
                  sys_message,
                  output_validation_and_processing_function=(lambda a: True),
                  family="google",
                  models_to_use=[["small", 5], ["large", 2]]):
    """
    Family is the base model being used; 
    Implement new families as new models are added to codebase.
    models_to_use is a nested list, each sublist contains 
    model size or type (within family) and number of times 
    that model size or type should be tried before switching 
    to next model type in list.
    For OpenAI it is model size(small/large), for google, it is model type(text/code)
    """
    cost = 0
    tries = 0
    model = ""
    if family == "openAI":
        for i in range(len(models_to_use)):
            if models_to_use[i][0] == "small":
                model = "gpt-3.5-turbo"
            elif models_to_use[i][0] == "small-extended-context":
                model = "gpt-3.5-turbo-16k"
            elif models_to_use[i][0] == "large":
                model = "gpt-4"
            elif models_to_use[i][0] == "large-extended-context":
                model = "gpt-4-32k"
            else:
                print(
                    "requested model type does not exist in requested model family.\n Defaulting to using gpt-3.5-turbo.\n"
                )
                model = "gpt-3.5-turbo"
            #change above
            for j in range(models_to_use[i][1]):
                tries += 1
                model_output_and_metadata = process_model_IO_openAI_family(
                    human_message=user_message,
                    system_message=sys_message,
                    MODEL_NAME=model)
                cost += model_output_and_metadata['IO_cost_usd']
                processed_output = output_validation_and_processing_function(
                    model_output_and_metadata)
                if (processed_output["valid_output"] is True):
                    return {
                        "valid_output":
                        True,
                        "move_to_next_node":
                        True,
                        "llm_output":
                        processed_output["processed_output"],
                        'llm_used':
                        models_to_use[-1][0],
                        'output_end_reason':
                        model_output_and_metadata["output_end_reason"],
                        'IO_cost_usd':
                        round(cost, 7)
                    }
                else:
                    continue
        return {
            "move_to_next_node": False,
            "llm_output":
            f'AI output is invalid after max tries ({tries} tries)- restate your last message or request and try again',
            'llm_used': model,
            'output_end_reason': 'invalid output',
            'IO_cost_usd': round(cost, 7)
        }
    elif family == "google":
        #fair warning; google doesn't have differing model sizes
        #so all requests use the same model
        #this has both cost and performance implications
        model = ""
        for i in range(len(models_to_use)):
            if models_to_use[i][0] == "text":
                model = "text-bison@001"
            elif models_to_use[i][0] == "code":
                model = ""
            else:
                print(
                    "requested model type does not exist in requested model family.\n Defaulting to using text-bison001.\n"
                )
                model = "text-bison@001"
            for j in range(models_to_use[i][1]):
                tries += 1
                model_output_and_metadata = process_model_IO_google_family(
                    human_message=user_message,
                    system_message=sys_message,
                    MODEL_NAME=model)
                cost += model_output_and_metadata['IO_cost_usd']
                processed_output = output_validation_and_processing_function(
                    model_output_and_metadata)
                if (processed_output["valid_output"] is True):
                    return {
                        "valid_output":
                        True,
                        "move_to_next_node":
                        True,
                        "llm_output":
                        processed_output["processed_output"],
                        'llm_used':
                        models_to_use[-1][0],
                        'output_end_reason':
                        model_output_and_metadata["output_end_reason"],
                        'IO_cost_usd':
                        round(cost, 7)
                    }
                else:
                    continue
        return {
            "move_to_next_node": False,
            "llm_output":
            f'AI output is invalid after max tries ({tries} tries)- restate your last message or request and try again',
            'llm_used': model,
            'output_end_reason': 'invalid output',
            'IO_cost_usd': round(cost, 7)
        }
    else:
        print(
            "Only openAI and google have been implemented. Other model families have not yet been implemented."
        )
        return {}
    #if family=falcon/llama: IMPLEMENT!
    #if family=PaLM2: IMPLEMENT!


def process_model_IO_openAI_family(human_message,
                                   system_message,
                                   MODEL_NAME='gpt-3.5-turbo'):
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    except Exception as error:
        print(
            "Please set OPENAI_API_KEY env var or change model family and try again!"
        )
        print(f"got the following error: {error}")
        exit()
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=MODEL_NAME)
    message_to_send_to_llm = [[
        HumanMessage(content=human_message),
        SystemMessage(content=system_message)
    ]]
    #print(f"sent req. to openAI with model {MODEL_NAME}")
    result = llm.generate(message_to_send_to_llm)
    llm_output = result.generations[0][0].text
    llm_token_usage = result.llm_output['token_usage']
    llm_token_usage_data = [
        llm_token_usage['prompt_tokens'], llm_token_usage['completion_tokens'],
        llm_token_usage['total_tokens']
    ]
    llm_model_name = result.llm_output['model_name']
    output_end_reason = result.generations[0][0].generation_info[
        'finish_reason']
    cost_usd = -1
    gpt_35_turbo_cost_per_token = [0.0000015, 0.000002]  #[input, output]
    gpt_35_turbo_16k_cost_per_token = [0.000003, 0.000004]  #[input, output]
    gpt_4_cost_per_token = [0.00003, 0.00006]  #[input,output]
    gpt_4_32k_cost_per_token = [0.00006, 0.00012]  #[input_output]
    if llm_model_name == "gpt-3.5-turbo":
        cost_usd = (
            (llm_token_usage_data[0] * gpt_35_turbo_cost_per_token[0]) +
            (llm_token_usage_data[1] * gpt_35_turbo_cost_per_token[1]))
    elif llm_model_name == "gpt-3.5-turbo-16k":
        cost_usd = (
            (llm_token_usage_data[0] * gpt_35_turbo_16k_cost_per_token[0]) +
            (llm_token_usage_data[1] * gpt_35_turbo_16k_cost_per_token[1]))
    elif llm_model_name == "gpt-4":
        cost_usd = ((llm_token_usage_data[0] * gpt_4_cost_per_token[0]) +
                    (llm_token_usage_data[1] * gpt_4_cost_per_token[1]))
    elif llm_model_name == "gpt-4-32k":
        cost_usd = ((llm_token_usage_data[0] * gpt_4_32k_cost_per_token[0]) +
                    (llm_token_usage_data[1] * gpt_4_32k_cost_per_token[1]))
    else:
        print("model cost data not available; cost not calculated!")

    return {
        'llm_output': llm_output,
        'token_usage_dict': llm_token_usage,
        'llm_used': llm_model_name,
        'output_end_reason': output_end_reason,
        'IO_cost_usd': round(cost_usd, 7)
    }


def process_model_IO_google_family(human_message,
                                   system_message,
                                   MODEL_NAME='text-bison@001'):
    parameters = {
        "temperature": 0.75,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40,
    }
    if system_message != None:
        model_prompt = f"Instructions: {system_message}\n Information: {human_message}"
    else:
        model_prompt = human_message
    model: TextGenerationModel = TextGenerationModel.from_pretrained(
        MODEL_NAME)
    response: TextGenerationResponse = model.predict(model_prompt,
                                                     **parameters)
    if response.is_blocked:
        output_end_reason = "Response was blocked. Possible inappropriate prompt."
        print("Response blocked, printing safety attributes:\n")
        print(response.raw_prediction_response["metadata"]["safetyAttributes"])
    else:
        output_end_reason = "Finished response"
    llm_output = response.text
    llm_char_usage = {}  #implement
    cost_usd = 0.00  #implement
    return {
        'llm_output': llm_output,
        'char_usage_dict': llm_char_usage,
        'llm_used': MODEL_NAME,
        'output_end_reason': output_end_reason,
        'IO_cost_usd': round(cost_usd, 7)
    }
