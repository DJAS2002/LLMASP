########################################################
# Code copied from
# https://github.com/FinnAlberts/SchASPLM
########################################################

import tempfile
import atexit
import os

from clingo.ast import parse_files
from clingo import Control

def _save_file_tmp(asp_input):
    # Tijdelijk .lp bestand aanmaken
    tmp = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.lp',
        delete=False,  # Handmatig beheren voor atexit
        encoding='utf-8'
    )
    tmp.write(asp_input)
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    # Registreer verwijdering bij afsluiten programma
    atexit.register(lambda p=tmp_path: os.path.exists(p) and os.remove(p))

    return tmp_path

# NOTE GEORGE: I also tried parse_string, but parse_files seemed more helpful. For parse_string you would need exactly one Clingo statement on each line, but in some
# cases, e.g. with choice rules, a single statement can span multiple lines.

def _extract_line_number_from_error(msg):
    """
    Try to extract the line number from a Clingo error message.
    """
    # Example: "Results/CTDeepseek:1:34-41: error: syntax error, unexpected <VARIABLE>"
    # The line nr is between the first and second ":" symbol.
    parts = msg.split(":")
    if len(parts) > 2 and parts[2].isdigit():
        return int(parts[2])

    return None

def _check_file_syntax(filename:str):
    """
    Parse an entire ASP/Clingo file and collect all syntax errors using Clingo's logger.
    Returns a list of error dictionaries (empty if syntax is correct).
    """

    # Read the file too, so we can log the actual program lines in case of an error.
    with open(filename, "r", encoding="utf-8") as f:
        file_lines = f.readlines()

    errors = []

    def collector(_stmt):
        # Not needed here, but required by Clingo API
        pass

    def logger(code, msg):

        line_number = _extract_line_number_from_error(msg)
        code_line = file_lines[line_number - 1].strip()

        if "FULL PROGRAM" in code_line:
            return  # Don't log this non-informative message; every program has the line "----------------------------FULL PROGRAM----------------------------"

        errors.append({
            "type": str(code).strip(),
            "message": str(msg).strip(),
            "line number": line_number,
            "code": code_line
        })

    try:
        parse_files([filename], collector, logger=logger)
    except RuntimeError as e:
        pass  # This error is always generated if an error is found, but not very useful to log "on top".
        # errors.append({"type": "RuntimeError", "message": str(e), "line": None, "col": None})

    return errors



def _parse_file_and_print_errors(filename:str):
    """
    Parse the given ASP/Clingo file and print syntax errors if any.
    """
    # filename = _save_file_tmp(asp_input)
    print(f"\nChecking syntax of: {filename}\n" + "=" * 100)
    errors = _check_file_syntax(filename)

    if not errors:
        print("File is syntactically correct.")
        return

    print("Syntax errors found:\n")
    for err in errors:
        print(f"  Line nr: {err['line number']}")
        print(f"  Type   : {err['type']}")
        print(f"  Message: {err['message']}")
        print(f"  Code   : {err['code']}")
        print()
    return errors

def _check_grounding(asp_input:str):
    messages =[]

    def on_message(code, msg):
        messages.append((code, msg))

    ctl = Control(logger= on_message)

    ctl.add("base",[],asp_input)
    try:
        ctl.ground()
    except RuntimeError as e:
        # print("Grounding mislukt:", e)
        # print("Gelogde berichten:")
        # for code, msg in messages:
        #     print(f"  [{code}] {msg}")
        return messages

def parse_file_and_print_errors(asp_input:str):
    filename = _save_file_tmp(asp_input)
    return _parse_file_and_print_errors(filename)

def check_file_syntax(asp_input:str):
    filename = _save_file_tmp(asp_input)
    return _check_file_syntax(filename)

def check_asp_input(asp_input:str, verbose=0):
    filename = _save_file_tmp(asp_input)
    if verbose == 1:
        _parse_file_and_print_errors(filename)
        return
    elif verbose == 0:
        return _check_file_syntax(filename)
    else:
        raise ValueError(f"Invalid verbose: {verbose}")


def check_grounding(asp_input:str):
    return _check_grounding(asp_input=asp_input)




#
# Core code; specify the files to check here and runs the parser for each file. All errors are printed to console.
#
if __name__ == "__main__":
    filenames = (
        r"C:\Users\engineer\Documents\Projects\SchASPLM\Results\Heyninck et al (original research)/CTLlama8B",
        # "Results/CTDeepseek",
        # "Results/CTLlama8B",
        # #"Results/ETDeepseek",     # Doesn't exist? Not sure why
        # "Results/ETLlama8B",
        # "Results/NSDeepseek",
        # "Results/NSLlama8B",
        # "Results/SSDeepseek",
        # "Results/SSLlama8B"
    )

    for filename in filenames:
        parse_file_and_print_errors(filename)