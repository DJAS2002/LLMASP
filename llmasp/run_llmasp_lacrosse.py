from llmasp.llm import LLMASP, LLMHandler
from llmasp.asp import Solver
# import argparse
from pathlib import Path




class Config:
    BEHAVIOR_PATH = Path('./specifications/behavior_translator_lacrosse.yml')
    APPLICATION_PATH = Path('./specifications/application_translator_lacrosse.yml')
    DATABASE_PATH = Path('./specifications/db_lacrosse.yml')
    VERBOSE = 1
    SINGLE_PASS = False
    MODEL = "llama3.1:8b"
    SEVER_URL = "http://localhost:11434/v1"



def main():

    # initialize LLM Handler with the specified model and server URL
    llm = LLMHandler(Config.MODEL, Config.SEVER_URL)

    # initialize the ASP solver
    solver  = Solver()

    # Initialize LLMASP with the specified files
    llmasp = LLMASP(config_file= str(Config.APPLICATION_PATH),
                    behavior_file= str(Config.BEHAVIOR_PATH),
                    llm=llm,
                    solver=solver
                    )

    # get user input
    # user_input = input("Enter your query: ")
    user_input = "give a list of days that teams t1, t2, t3 and t4 play."
    user_input = "Is team t2 playing on day 3 and is team t3 playing on day 4?"
    user_input = "When is team 't1' playing and is team t2 playing on day 4?"
    user_input = "When is team 't1' playing?"
    # Run the planner
    response = llmasp.run(user_input= user_input,
                          single_pass=Config.SINGLE_PASS,
                          verbose=Config.VERBOSE)
    print("Response from LLMASP:")
    print(response)
    return

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="LLMASP LaCrosse Planner")
    # parser.add_argument("--files", nargs="+",
    #                     default=[".\\instances\\instances.lp", ".\\encodings\\encodings.lp"],
    #                     help="Logic program files (default: instances + encodings)")
    # parser.add_argument("--verbose", action="store_true",
    #                     help="Verbose solver output")
    # args = parser.parse_args()


   main()