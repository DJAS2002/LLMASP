from llmasp.llm import LLMASP, LLMHandler
from llmasp.asp import Solver
# import argparse
from pathlib import Path
import yaml
import json
from tqdm import tqdm
from itertools import combinations, product
from colorama import Fore, Back, Style, init as colorama_init, just_fix_windows_console
from collections import defaultdict
colorama_init()

class Config:
    BEHAVIOR_PATH = Path('./specifications/behavior_translator_lacrosse.yml')
    APPLICATION_PATH = Path('./specifications/application_translator_lacrosse.yml')
    DATABASE_PATH = Path('./specifications/db_lacrosse.yml')
    VERBOSE = 1
    SINGLE_PASS = True
    MODEL = "llama3.1:8b"
    # MODEL = "llama3.1:70b"
    SEVER_URL = "http://localhost:11434/v1"
    EXPERIMENT = Path(r"./specifications/experiment_lacrosse.yml")


def load_experiment(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def generate_permutations(lines: list[str]) -> list[tuple[str, ...]]:
    result = []
    for size in range(1, len(lines) + 1):
        for combo in combinations(lines, size):
            result.append(combo)
    return result

def to_serializable(obj):
    if hasattr(obj, '__dict__'):
        return vars(obj)
    if isinstance(obj, (list, tuple)):
        return [to_serializable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj

def cc(text, fg="", bg=""):
    return bg + fg + text + Style.RESET_ALL

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
    experiment = load_experiment(str(Config.EXPERIMENT))
    user_inputs = experiment["user_inputs"]
    prompts = [line.strip() for line in experiment["prompt_templates"].splitlines() if line.strip()]
    permutations= generate_permutations(prompts)

    behavior_header = llmasp.behavior['preprocessing']['init']

    combinations = list(product(user_inputs, permutations))

    with open("Experiment_results.jsonl", "w") as f:
        for input_line, prompt in tqdm(combinations, desc="Experiments"):
            preprocess_init = behavior_header + "\n".join(prompt)
            llmasp.behavior['preprocessing']['init'] = preprocess_init
            created_facts_str, asp_input, queries, meta = llmasp.natural_to_asp(
                user_input=input_line,
                single_pass=Config.SINGLE_PASS,
            )
            record = {
                "model": Config.MODEL,
                "input": input_line,
                "prompt": prompt,
                "created_facts": created_facts_str,
                "queries": queries,
                "meta": to_serializable(meta)
            }
            f.write(json.dumps(record) + "\n")
            tqdm.write(created_facts_str)

        # add results to all_experiments and use [input_line"]["prompt"] as keys


        #     print(cc("Created ASP:",Fore.GREEN), "\n", created_facts_str)
        # # print(cc("Created Queries:",Fore.GREEN), "\n", queries)
        # print(cc("Created Meta:",Fore.GREEN), "\n", meta)
    # #llmasp.behavior['preprocessing']['init']
    # # get user input
    # user_input = input("Enter your query: ")
    # user_input = "give a list of days that teams t1, t2, t3 and t4 play."
    # user_input = "Is team t2 playing on day 3 and is team t3 playing on day 4?"
    # user_input = "When is team 't1' playing and is team t2 playing on day 4?"
    # user_input = "When is team 't1' playing?"
    # user_input = "Give me the full schedule"
    # user_input = "Give me all days on which team t1 plays team t2"
    # user_input = "Add team t5 and t6 in the men's league, add playing days 14 until 20 and show me the proposed schedule."
    # user_input = "What is the schedule?"

    # # Run the planner
    # response = llmasp.run(user_input= user_input,
    #                       single_pass=Config.SINGLE_PASS,
    #                       verbose=Config.VERBOSE)
    # # if response:
    #     # print(f"{'*'*50}")
    #     # print(f"{'*' * 50}")
    #     # print("Response from LLMASP:")
        # print(response)
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