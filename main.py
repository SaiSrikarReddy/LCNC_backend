from fastapi import FastAPI
from run_llm_query import process_model_IO_google_family
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import json
import uuid
import nodes

app = FastAPI()
frontend_origin = "https://autocodefend2.jiinyusguy.repl.co"
origins = [frontend_origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("architecture_template.json", "r") as f:
    jsonTemplate = json.load(f)

dataJson = {}
obj = ""
dtls = ""
question = "AI is thinking...please wait for the AI to ask a question :)"
qNum = 0
min_arch_req = """
App Name: Required
App Logo file name: Optional
Framework/Language: Required
Theme colors: Required
Common components:
    Header: optional
            Brand logo image name: Optional
            User profile/profile settings link/dropdown: Bool/Required(If header exists)
            Header links list: Optional
                Link Name: Required (At least one, if links list exists)
                    Link URL: Required (If link name exists)
                    Link is a dropdown: Bool/Required (If link name exists)
                    Link dropdown sublinks list: Non empty list of strings (Required if link is a dropdown is True)
    Footer: Optional
        Footer Links: Required (if Footer exists)
            {Link name : Link route} at least one key value pair required if Footer links exists
    Navbar: Optional
            User profile/profile settings link/dropdown: Bool/Required(If navbar exists)
            Navbar links list: Optional
                Link Name: Required (At least one, if links list exists)
                    Link URL: Required (If link name exists)
                    Link is a dropdown: Bool/Required (If link name exists)
                    Link dropdown sublinks list: Non empty list of strings (Required if link is a dropdown is True)
Pages:
    (For each page)
    Page name: (at least 1 required):
        Route: required
        Functionality description: required
        Page architecture: required, is of the following format - 
            {
                "page container div": {
                  "components grid": {
                    "component 1 name": {
                      "component type": "str",
                      "component function": "str"
                    },
                    "component 2 name": {
                      "component type": "str",
                      "component function": "str"
                    }
                  }
              }
        } (At least one component required in grid)
**End of minimum architecture information specifications**
"""


# Initialize the JSON file
def initialize_json(app_name: str):
    data = {
        "Frontend language": "JavaScript",
        "Frontend framework": "React",
        "Frontend UI library": "Mantine",
        "Theme colors": "UI library default",
        "App name": app_name
    }
    dataJson = data
    with open("architecture.json", "w") as f:
        json.dump(data, f)


def addDetailsLLM(obj: str, dtl: str):
    dataJson = {}
    with open("architecture.json", "r") as f:
        dataJson = f.read()
    prompt = f"""The following is an example of a frontend architecture document: \n{jsonTemplate}\n Please create a similar architecture document, making assumptions where needed for page names and link routes(there shouldn't be any "placeholder"s), given the following from the user: Current architecture json:{dataJson}\n App objective : {obj}\n App detailed description: {dtl}\n.Do not change the lang/framework/library/app name. Do not add any fields that are not in the detailed description.(For example if the decription does not include a Navbar, don't add a navbar to the architecture, even though it is in the example).\n Only output pure JSON (all prop names etc enclosed in double quotes("")) , with nothing before or after it, not even backticks."""
    output = process_model_IO_google_family(human_message=prompt,
                                            system_message=None)
    llm_output = output["llm_output"]
    print(type(llm_output))
    with open("architecture.json", "w") as f:
        f.write(llm_output)
    print("Function callLLM called")


# Stub function for getLLMQn
def getLLMQn():
    global question
    with open("architecture.json", "r") as f:
        arch = f.read()
    prompt = f"""The following JSON describes everything required to create a frontend for an app:\n{arch}\n The following are the minimum specs needed to build an app:{min_arch_req}\n Based on the information you have, please ask a clarifying question that would help make the app JSON more clear. Do not reference the JSON or the specs in the question, do not use the placeholder names in the JSON while asking questions (Instead of asking where does link_1_name lead to, ask where does the first link in the header lead?), and do not ask for information that is already in the JSON. Please return only the question and nothing else before or after it. Do not ask questions that have already been asked in the askAnswerQn field(if it exists), even if you rephrase them. Example questions include asking for the names of links in the header, if not mentioned, the number of inputs in a form and what they are, etc. If you do not think any further information is required(you don't need to ask more questions), return `-1` with nothing before or after it(a python program will evaluate if you returned `-1`. The py statemement evaluating this is `if returnVal==-1:`).Only return a question, or `-1`, nothing else."""
    print("Get qn called")
    output = process_model_IO_google_family(human_message=prompt,
                                            system_message=None)
    question = output["llm_output"]
    print(question)
    return question


@app.post("/appName/")
async def set_app_name(appName: str):
    initialize_json(appName)
    return {"message": "architecture.json has been initialized"}


@app.post("/appObjective/")
async def set_app_objective(objective: str):
    global obj
    obj = objective
    #addDetailsLLM(objective)
    return {
        "message": "Objective has been consumed (stored to ram temporarily)"
    }


@app.post("/addDetails/")
async def add_details(detail: str):
    global dtls
    global obj
    dtls = detail
    addDetailsLLM(obj, dtls)
    return {"message": "Details/objective has been passed to LLMaddFn"}


@app.get("/getQuestion/")
async def get_question():
    global question
    ques = getLLMQn()
    question = ques
    if ques == "-1":
        return {"message": "Done"}
    else:
        return {"question": ques}


@app.post("/answeredQuestion/")
async def answerQuestion(answer: str):
    global qNum
    global question
    global jsonTemplate
    with open("architecture.json", "r") as f:
        dataJson = f.read()
    prompt = f"""
    The following is an architecture for the frontend of an app in JSON form:\n{dataJson}\n Based on the architecture, the user was asked the following question\n: {question}\n, and the user answered as follows\n: {answer}\n. Please modify the architecture JSON with the new information from the answer, and add a new JSON key (askAnswerQn_<number>) with the question and the answer to the JSON, and return the entire JSON. \n Only output pure JSON (all prop names etc enclosed in double quotes("")) , with nothing before or after it, not even backticks.
    """
    output = process_model_IO_google_family(human_message=prompt,
                                            system_message=None)
    llm_output = output["llm_output"]
    print(type(llm_output))
    with open("architecture.json", "w") as f:
        f.write(llm_output)
    print("Function callLLM called")
    if qNum != 3:
        question = getLLMQn()
        qNum += 1
        return {"question": question}
    else:
        qNum = 0
        return {"message": "Done"}

@app.get("/getAppZipFile/")
async def getZip():
    file_to_delete = "app_files.zip"
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
    #make files
    nodes.init_project()
    #zip files
    shutil.make_archive('app_files', 'zip', 'output_folder')
    #return zipped files
    return FileResponse("app_files.zip", headers={"Content-Disposition": "attachment"})

if __name__=="__main__":
    uvicorn.run(app, port=8080, host="0.0.0.0")