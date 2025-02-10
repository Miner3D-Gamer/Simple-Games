"""The opposite of RregEx; GenEx instead of validating/parsing strings, it generates them. I have not yet tested it extensively."""

import random
from typing import NoReturn
import math

from string import ascii_letters

quotes = ["'", '"']


def expect_next_action(
    string: str, plus: str, inp_idx: int, end: str = ""
) -> tuple[str, int] | NoReturn:
    if string == "":
        return "", inp_idx
    idx = -1
    for char in string:
        idx += 1
        if char == " ":
            continue
        else:
            if plus and not char == "[":
                if char == plus:
                    return expect_next_action(string[idx + 1 :], "", inp_idx + idx)
                if char == end:
                    return string[idx + 1 :], inp_idx + idx
                raise Exception(
                    "Expected %s but got %s in %s (Did you close one too many brackets?) at character %s"
                    % (plus, char, string, inp_idx + idx)
                )
            else:
                return string[idx:], inp_idx + idx

    raise Exception("Expected action got '%s' at character %s" % string, inp_idx + idx)


def skip_until_outside(string: str, idx: int) -> NoReturn | tuple[str, str, int]:
    table = {
        "(": ")",
        "{": "}",
        "[": "]",
    }
    inverse_value = [v for k, v in table.items()]
    depth = 0
    outside_indicator = table[string[0]]
    total = ""
    for idx, char in enumerate(string):
        if char in table:
            depth += 1
            continue
        elif char in inverse_value:
            depth -= 1
            if depth == 0:
                if char != outside_indicator:
                    raise Exception(
                        "Expected %s instead of %s to exit" % (outside_indicator, char)
                    )
                return string[1:idx], string[idx + 1 :], idx
            continue
        total += char

    raise Exception("%s brackets have not been closed at character %s" % (depth, idx))
    # raise Exception("Something went wrong while parsing, gathered: '%s' from '%s'" % (total, string))


def separate_action(
    string: str, separator: str, first: bool, idx: int, end: str = ""
) -> tuple[dict, str]:
    if not first:
        string, idx = expect_next_action(string, separator, idx, end)
    if not string:
        return {}, ""
    if string[0] in quotes:
        full = ""
        inside_string = string[0]
        string = string[1:]
        escaping = False
        for char_idx, char in enumerate(string):
            if char == inside_string:
                if escaping:
                    full += char
                    escaping = False
                    continue
                return {
                    "type": "string",
                    "value": full,
                }, string[char_idx + 1 :]
            if char == "\\":
                escaping = True
                continue
            if escaping:
                raise Exception(
                    "Expected string end after escape character (%s) but got %s"
                    % (inside_string, char)
                )

            full += char

    if string[0] in "[":
        return {
            "type": "list",
            "value": wrapper(string[1:], ",", "]", idx),
        }, ""

    function = ""

    for idx, char in enumerate(string):
        if char in ascii_letters + "_":
            function += char
        elif char == "(":
            inputs, next, idx = skip_until_outside(string[idx:], idx)
            next = next.lstrip()
            # if next and (next[0] in ascii_letters or next[0] == "("):
            #     all_inputs = wrapper(inputs, ",", "", idx)
            #     # Multifunction!
            #     while True:
            #         if next == "":
            #             break
            #         if next[0] == " ":
            #             next = next[1:]
            #             continue
            #         if next[0] == "(":
            #             next_inputs, next, idx = skip_until_outside(next, idx)
            #             all_inputs.extend(wrapper(next_inputs, ",", "", idx))
            #             continue
            #         if next[0] in ascii_letters:
            #             next_multi_function_part, next = separate_action(
            #                 next, "+", True, idx, ""
            #             )
            #             function += "_" + next_multi_function_part["name"]
            #             all_inputs.extend(next_multi_function_part["inputs"])
            #             continue
            #         raise Exception(next)

            #     return {
            #         "type": "multi_function",
            #         "name": function,
            #         "inputs": all_inputs,
            #     }, next

            return {
                "type": "function",
                "name": function,
                "inputs": wrapper(inputs, ",", "", idx),
            }, next

    raise Exception(
        "Expected next action but got invalid characters '%s' (Did you forget to quote them?)"
        % string
    )


def wrapper(string: str, plus: str, end: str, idx: int) -> list[dict]:
    all_actions = []
    action, further = separate_action(string, plus, True, idx, end)
    if action != {}:
        all_actions.append(action)
    while True:
        action, further = separate_action(further, plus, False, idx, end)
        if action != {}:
            all_actions.append(action)
        if not further:
            break
    # return_list = []
    # for idx in range(len(all_actions) - 1):
    #     last = (idx % (len(all_actions) - 1)) == 0
    #     now = all_actions[idx]
    #     future = all_actions[idx + 1]
    #     if now["type"] == future["type"] == "function":
    #         print("HERE")
    #         if future["name"].startswith("_"):
    #             return_list.append(
    #                 {
    #                     "type": "function",
    #                     "name": now["name"] + future["name"],
    #                     "inputs": now["inputs"] + future["inputs"],
    #                 }
    #             )
    #         else:
    #             return_list.append(now)
    #             if last:
    #                 return_list.append(future)
    #     else:
    #         print(now["type"], future["type"])
    #         return_list.append(now)
    #         if last:
    #             return_list.append(future)

    return all_actions


def split_genex_into_actions(string):
    # 3(.5) Modes:
    # Expecting next action
    # Extracting string/function
    # Skipping subcode

    return wrapper(string, "+", "", 0)


def GenEx(string: str):
    actions = split_genex_into_actions(string)
    final = ""

    def is_string_int(x):
        if x["type"] == "string":
            return x["value"].isdigit()
        return False

    def input_error(all_inputs: list[dict], rules: dict, function: str):
        return
        inputs = rules["inputs"]
        expected = len(inputs)
        gotten = len(all_inputs)
        if gotten != expected:
            raise Exception(
                "Expected %s inputs but got %s for %s, given %s"
                % (expected, gotten, function, all_inputs)
            )
        for idx in range(expected):
            given_input = all_inputs[idx]
            expected_input = inputs[idx]

            expected_type_pre = expected_input["type"]
            if isinstance(expected_type_pre, str):
                expected_type_pre = [expected_type_pre]

            for expected_type in expected_type_pre:
                if expected_type == "any":
                    break
                elif expected_type == "int":
                    if is_string_int(given_input):
                        break
                else:
                    if given_input["type"] == expected_type:
                        break
            else:
                raise Exception(
                    "Expected input %s to be of type %s but got type %s for %s, given %s"
                    % (
                        idx,
                        expected_input["type"],
                        given_input["type"],
                        function,
                        all_inputs,
                    )
                )

        # got = len(all_inputs)
        # if got != expected:
        #     raise Exception(
        #         "Expected %s inputs but got %s for %s, given %s"
        #         % (expected, got, function, all_inputs)
        #    )

    custom_functions = {}
    custom_variables = {}

    def handle_function(function: str, inputs: list):

        def choice_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return random.choice(resolved[0]["value"])

        def range_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)

            return {
                "type": "list",
                "value": [
                    {"type": "string", "value": str(i)}
                    for i in range(
                        int(resolved[0]["value"]), int(resolved[1]["value"]) + 1
                    )
                ],
            }

        def number_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)

            return {
                "type": "string",
                "value": str(
                    random.randint(
                        int(resolved[0]["value"]), int(resolved[1]["value"])
                    ),
                ),
            }

        def repeat_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            return_list = []
            amount = resolve_input(inputs[0])

            for i in range(int(amount["value"])):
                to_repeat = resolve_input(inputs[1], True)
                if to_repeat["type"] == "string":
                    if to_repeat["value"] == "&RETURN":
                        break
                input_error([amount, to_repeat], function_info, function)
                return_list.append(to_repeat)
            return {
                "type": "list",
                "value": return_list,
            }

        def loop_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            return_list = []

            while True:
                to_repeat = resolve_input(inputs[0], True)
                if to_repeat["type"] == "string":
                    if to_repeat["value"] == "&RETURN":
                        break
                input_error([to_repeat], function_info, function)
                return_list.append(to_repeat)
            return {
                "type": "list",
                "value": return_list,
            }

        def join_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            revolved = [resolve_input(x) for x in inputs]
            input_error(revolved, function_info, function)
            string = revolved[1]
            repeat_list = revolved[0]

            final = to_string(repeat_list["value"][0])  # type: ignore
            for i in repeat_list["value"][1:]:
                # input_error([string, i], function_info, function)
                final += string["value"]
                final += to_string(i)  # type: ignore
            return {
                "type": "string",
                "value": final,
            }

        def is_condition_true(condition) -> bool:
            if is_string_int(condition):
                return condition["value"] != "0"

            return condition["value"]

        def if_else_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)

            if is_condition_true(resolved[0]):
                return resolved[1]
            else:
                return resolved[2]

        def equal_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": ("1" if resolved[0]["value"] == resolved[1]["value"] else "0"),
            }

        def add_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) + int(resolved[1]["value"])),
            }

        def subtract_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) - int(resolved[1]["value"])),
            }

        def multiply_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) * int(resolved[1]["value"])),
            }

        def divide_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            if resolved[1]["value"] == 0:
                return {"type": "string", "value": "ERROR"}
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) // int(resolved[1]["value"])),
            }

        def find_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"][int(resolved[1]["value"])],
            }

        def length_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {"type": "string", "value": str(len(resolved[0]["value"]))}

        def split_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "list",
                "value": [
                    {"type": "string", "value": x}
                    for x in resolved[0]["value"].split(resolved[1]["value"])
                ],
            }

        def get_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            if len(resolved[0]["value"]) >= int(resolved[1]["value"]):
                return {"type": "string", "value": "ERROR"}
            return {
                "type": "string",
                "value": resolved[0]["value"][int(resolved[1]["value"])],
            }

        def shuffle_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "list",
                "value": random.sample(resolved[0]["value"], len(resolved[0]["value"])),
            }

        def reverse_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            type = resolved[0]["type"]
            if type == "string":
                return {
                    "type": "string",
                    "value": resolved[0]["value"][::-1],
                }
            elif type == "list":
                return {
                    "type": "list",
                    "value": resolved[0]["value"][::-1],
                }
            else:
                raise Exception("Unknown type %s" % type)

        def concat_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            type = resolved[0]["type"]
            if type == "string":
                return {
                    "type": "string",
                    "value": resolved[0]["value"] + resolved[1]["value"],
                }
            elif type == "list":
                return {
                    "type": "list",
                    "value": resolved[0]["value"] + resolved[1]["value"],
                }
            else:
                raise Exception("Unknown type %s" % type)

        def clamp_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            type = resolved[0]["type"]
            if is_string_int(resolved[0]):

                def clamp(min, max, value):
                    if value < min:
                        return min
                    elif value > max:
                        return max
                    else:
                        return value

                return {
                    "type": "string",
                    "value": str(
                        clamp(
                            int(resolved[1]["value"]),
                            int(resolved[2]["value"]),
                            int(resolved[0]["value"]),
                        )
                    ),
                }
            if type == "string":
                return {
                    "type": "string",
                    "value": resolved[0]["value"][
                        int(resolved[1]["value"]) : int(resolved[2]["value"])
                    ],
                }
            elif type == "list":
                return {
                    "type": "list",
                    "value": resolved[0]["value"][
                        int(resolved[1]["value"]) : int(resolved[2]["value"])
                    ],
                }
            else:
                raise Exception("Unknown type %s" % type)

        def upper_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].upper(),
            }

        def lower_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].lower(),
            }

        def capitalize_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].capitalize(),
            }

        def title_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].title(),
            }

        def strip_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].strip(),
            }

        def lstrip_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].lstrip(),
            }

        def rstrip_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].rstrip(),
            }

        def replace_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": resolved[0]["value"].replace(
                    resolved[1]["value"], resolved[2]["value"]
                ),
            }

        def mod_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) % int(resolved[1]["value"])),
            }

        def abs_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(abs(int(resolved[0]["value"]))),
            }

        def floor_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.floor(int(resolved[0]["value"]))),
            }

        def ceil_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.ceil(int(resolved[0]["value"]))),
            }

        def round_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(round(int(resolved[0]["value"]))),
            }

        def min_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(min(int(resolved[0]["value"]), int(resolved[1]["value"]))),
            }

        def max_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(max(int(resolved[0]["value"]), int(resolved[1]["value"]))),
            }

        def contains_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"] in resolved[1]["value"]),
            }

        def startswith_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].startswith(resolved[1]["value"])),
            }

        def endswith_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].endswith(resolved[1]["value"])),
            }

        def sort_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "list",
                "value": sorted(resolved[0]["value"]),
            }

        def unique_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "list",
                "value": list(set(resolved[0]["value"])),
            }

        def pow_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) ** int(resolved[1]["value"])),
            }

        def log_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    math.log(int(resolved[0]["value"]), int(resolved[1]["value"]))
                ),
            }

        def sqrt_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.sqrt(int(resolved[0]["value"]))),
            }

        def sin_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.sin(int(resolved[0]["value"]))),
            }

        def cos_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.cos(int(resolved[0]["value"]))),
            }

        def tan_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.tan(int(resolved[0]["value"]))),
            }

        def asin_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.asin(int(resolved[0]["value"]))),
            }

        def acos_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.acos(int(resolved[0]["value"]))),
            }

        def atan_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.atan(int(resolved[0]["value"]))),
            }

        def atan2_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    math.atan2(int(resolved[0]["value"]), int(resolved[1]["value"]))
                ),
            }

        def count_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].count(resolved[1]["value"])),
            }

        def ljust_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].ljust(int(resolved[1]["value"]))),
            }

        def rjust_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].rjust(int(resolved[1]["value"]))),
            }

        def mjust_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(resolved[0]["value"].center(int(resolved[1]["value"]))),
            }

        def and_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    1
                    if (
                        is_condition_true(resolved[0])
                        and is_condition_true(resolved[1])
                    )
                    else 0
                ),
            }

        def or_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    1
                    if (
                        is_condition_true(resolved[0]) or is_condition_true(resolved[1])
                    )
                    else 0
                ),
            }

        def not_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(0 if is_condition_true(resolved[0]) else 1),
            }

        def greater_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) > int(resolved[1]["value"])),
            }

        def less_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) < int(resolved[1]["value"])),
            }

        def greater_or_equal_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) >= int(resolved[1]["value"])),
            }

        def less_or_equal_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(int(resolved[0]["value"]) <= int(resolved[1]["value"])),
            }

        def exp_func(inputs: list[dict[str, str]], function_info: dict, function: str):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(math.exp(int(resolved[0]["value"]))),
            }

        def greatest_common_divisor_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    math.gcd(int(resolved[0]["value"]), int(resolved[1]["value"]))
                ),
            }

        def common_multiple_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            return {
                "type": "string",
                "value": str(
                    math.lcm(int(resolved[0]["value"]), int(resolved[1]["value"]))
                ),
            }

        def set_var_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            custom_variables[resolved[0]["value"]] = resolved[1]
            return {"type": "string", "value": ""}

        def get_var_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            got = custom_variables.get(
                resolved[0]["value"], {"type": "string", "value": "ERROR"}
            )
            return got

        def set_func_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            input_error(resolved, function_info, function)
            custom_functions[resolve_input(inputs[0])["value"]] = inputs[1]
            return {"type": "string", "value": ""}

        def get_func_func(
            inputs: list[dict[str, str]], function_info: dict, function: str
        ):
            resolved = [resolve_input(x) for x in inputs]
            input_error(resolved, function_info, function)
            got = custom_functions.get(
                resolved[0]["value"], {"type": "string", "value": "ERROR"}
            )
            return resolve_input(got, True)

        # def return_func(
        #     inputs: list[dict[str, str]], function_info: dict, function: str
        # ):
        #     resolved = [resolve_input(x) for x in inputs]
        #     input_error(resolved, function_info, function)

        #     return resolve_input(got)

        functions = {
            "choice": {
                "inputs": [{"type": ["list", "string"]}],
                "func": choice_func,
            },
            "range": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": range_func,
            },
            "randint": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": number_func,
            },
            "repeat": {
                "inputs": [{"type": "int"}, {"type": "any"}],
                "func": repeat_func,
            },
            "join": {
                "inputs": [{"type": "list"}, {"type": "string"}],
                "func": join_func,
            },
            "if_else": {
                "inputs": [{"type": "string"}, {"type": "any"}, {"type": "any"}],
                "func": if_else_func,
            },
            "equals": {
                "inputs": [{"type": "any"}, {"type": "any"}],
                "func": equal_func,
            },
            "add": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": add_func,
            },
            "subtract": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": subtract_func,
            },
            "multiply": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": multiply_func,
            },
            "divide": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": divide_func,
            },
            "find": {
                "inputs": [{"type": ["list", "string"]}, {"type": "str"}],
                "func": find_func,
            },
            "get": {
                "inputs": [{"type": ["list", "string"]}, {"type": "int"}],
                "func": get_func,
            },
            "len": {
                "inputs": [{"type": ["list", "string"]}],
                "func": length_func,
            },
            "split": {
                "inputs": [{"type": ["list", "string"]}, {"type": "string"}],
                "func": split_func,
            },
            "shuffle": {
                "inputs": [{"type": ["list", "string"]}],
                "func": shuffle_func,
            },
            "reverse": {
                "inputs": [{"type": ["list", "string"]}],
                "func": reverse_func,
            },
            "concat": {
                "inputs": [{"type": ["list", "string"]}, {"type": ["list", "string"]}],
                "func": concat_func,
            },
            "clamp": {
                "inputs": [
                    {"type": ["list", "string", "int"]},
                    {"type": "int"},
                    {"type": "int"},
                ],
                "func": clamp_func,
            },
            "mod": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": mod_func,
            },
            "abs": {
                "inputs": [{"type": "int"}],
                "func": abs_func,
            },
            "floor": {
                "inputs": [{"type": "int"}],
                "func": floor_func,
            },
            "ceil": {
                "inputs": [{"type": "int"}],
                "func": ceil_func,
            },
            "min": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": min_func,
            },
            "max": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": max_func,
            },
            "contains": {
                "inputs": [{"type": ["list", "string"]}, {"type": "any"}],
                "func": contains_func,
            },
            "replace": {
                "inputs": [
                    {"type": ["string"]},
                    {"type": "string"},
                    {"type": "string"},
                ],
                "func": replace_func,
            },
            "upper": {"inputs": [{"type": "string"}], "func": upper_func},
            "lower": {"inputs": [{"type": "string"}], "func": lower_func},
            "title": {"inputs": [{"type": "string"}], "func": title_func},
            "strip": {"inputs": [{"type": "string"}], "func": strip_func},
            "lstrip": {"inputs": [{"type": "string"}], "func": lstrip_func},
            "rstrip": {"inputs": [{"type": "string"}], "func": rstrip_func},
            "capitalize": {"inputs": [{"type": "string"}], "func": capitalize_func},
            "startswith": {
                "inputs": [{"type": "string"}, {"type": "string"}],
                "func": startswith_func,
            },
            "endswith": {
                "inputs": [{"type": "string"}, {"type": "string"}],
                "func": endswith_func,
            },
            "sort": {
                "inputs": [{"type": ["list"]}],
                "func": sort_func,
            },
            "unique": {
                "inputs": [{"type": ["list"]}],
                "func": unique_func,
            },
            "round": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": round_func,
            },
            "pow": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": pow_func,
            },
            "sqrt": {"inputs": [{"type": "int"}], "func": sqrt_func},
            "log": {"inputs": [{"type": "int"}, {"type": "int"}], "func": log_func},
            "sin": {"inputs": [{"type": "int"}], "func": sin_func},
            "cos": {"inputs": [{"type": "int"}], "func": cos_func},
            "tan": {"inputs": [{"type": "int"}], "func": tan_func},
            "asin": {"inputs": [{"type": "int"}], "func": asin_func},
            "acos": {"inputs": [{"type": "int"}], "func": acos_func},
            "atan": {"inputs": [{"type": "int"}], "func": atan_func},
            "atan2": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": atan2_func,
            },
            "count": {
                "inputs": [{"type": ["list", "string"]}, {"type": "string"}],
                "func": count_func,
            },
            "ljust": {
                "inputs": [{"type": "string"}, {"type": "int"}, {"type": "string"}],
                "func": ljust_func,
            },
            "rjust": {
                "inputs": [{"type": "string"}, {"type": "int"}, {"type": "string"}],
                "func": rjust_func,
            },
            "mjust": {
                "inputs": [{"type": "string"}, {"type": "int"}, {"type": "string"}],
                "func": mjust_func,
            },
            "and": {
                "inputs": [{"type": "string"}, {"type": "string"}],
                "func": and_func,
            },
            "or": {
                "inputs": [{"type": "string"}, {"type": "string"}],
                "func": or_func,
            },
            "not": {
                "inputs": [{"type": "string"}],
                "func": not_func,
            },
            "greater": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": greater_func,
            },
            "less": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": less_func,
            },
            "greater_or_equal": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": greater_or_equal_func,
            },
            "less_or_equal": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": less_or_equal_func,
            },
            "exp": {"inputs": [{"type": "int"}], "func": exp_func},
            "greatest_commond_ivisor": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": greatest_common_divisor_func,
            },
            "commonmultiple": {
                "inputs": [{"type": "int"}, {"type": "int"}],
                "func": common_multiple_func,
            },
            "set_var": {
                "inputs": [{"type": "string"}, {"type": "any"}],
                "func": set_var_func,
            },
            "get_var": {
                "inputs": [{"type": "string"}],
                "func": get_var_func,
            },
            "create_function": {
                "inputs": [{"type": "string"}, {"type": "any"}],
                "func": set_func_func,
            },
            "call_function": {
                "inputs": [{"type": "string"}],
                "func": get_func_func,
            },
            "return": {
                "inputs": [],
                "func": lambda x, y, z: {"type": "string", "value": "&RETURN"},
            },
            "loop": {
                "inputs": [{"type": "any"}],
                "func": loop_func,
            },
            # "return": {
            #     "inputs": [],
            #     "func": return_func,
            # },
        }

        function_info = functions.get(function)
        if function_info is None:
            raise Exception(
                "Unknown function '%s' (Action list: %s)" % (function, actions)
            )

        def resolve_input(input, inside_recursion: bool = False):
            if input["type"] in ["list", "string"]:
                return input
            elif input["type"] == "function":
                return handle_function(input["name"], input["inputs"])
            else:
                raise Exception("Unknown type %s" % input["type"])

        resolved = inputs

        # input_error(resolved, function_info, function)

        return function_info["func"](inputs, function_info, function)

        raise Exception(
            "Unknown function %s (with inputs resolved to %s, original inputs %s)"
            % (function, resolved, inputs)
        )

    def to_string(action: dict):
        type = action["type"]
        if type == "string":
            return action["value"]
        elif type in ["function", "multi_function"]:
            return to_string(handle_function(action["name"], action["inputs"]))
        elif type == "list":
            return "[" + ", ".join([to_string(i) for i in action["value"]]) + "]"

        raise Exception("Unknown type %s" % type)

    for action in actions:
        final += to_string(action)

    return final


__all__ = ["GenEx"]
# string = r"'You\\'re a '+choice(['idiot','fool','coward']) + ' for gambling, here is todays number: ' + join(repeat('6', choice(range('1', '6'))), '')"

# string = r"if (equals('2', choice(range('1', '3')))) ('You won') else ('You lost')"
# string = "repeat('10', if_else (randint('0','3'), 'hi', return()))"


# print(GenEx(string))
