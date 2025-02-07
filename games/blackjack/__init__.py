import random
from custom_typing import SetupInput, INPUTS, MainReturn, Action
from typing import Any
from typing import Literal, Dict, Tuple, Optional
from custom_typing import ExtraInfo, AdvancedInputs


def generate_card_unicode(suit: str, rank: str) -> str:
    suits = {
        "Hearts": "B",
        "Diamonds": "C",
        "Clubs": "D",
        "Spades": "A",
    }
    ranks = {
        "Ace": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "10": "A",
        "Jack": "B",
        "Queen": "D",
        "King": "E",
    }

    return chr(int(f"1F0{suits[suit]}{ranks[rank]}", 16))


def get_worth(rank: str) -> int:
    return {
        "Ace": 11,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "Jack": 10,
        "Queen": 10,
        "King": 10,
    }[rank]


def get_worth_of_card(cards: list[str]) -> int:
    worth = 0
    for card in cards:
        worth += get_worth(card[1])
    return worth


empty = "🂠"


def combine_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    return {**dict1, **dict2}


class Card:
    def __init__(self, suit: str, rank: str, hidden: bool) -> None:
        self.suit = suit
        self.rank = rank
        self.hidden = hidden


class Game:
    def __init__(self) -> None:
        "The logic that would usually go here is moved to the 'setup' function"

    def main(
        self,
        input: int,
        info: ExtraInfo,
    ) -> Optional[MainReturn]:
        """
        A function called for every frame

        None: Something went wrong yet instead of raising an error, None can be returned to signalize that the game loop should be stopped

        Actions:
            "end": Displays the last frame and ends the game loop

            "change_inputs": Requires another variable neighboring 'actions'; 'inputs'. Changes the inputs if possible

            "error": Displays the given frame yet also signalized that something went wrong

        """
        action = Action(action="unset", value=None)

        frame = ""
        user = info["user_id"]
        if self.state == "select":
            if not user in self.all:
                self.all[user] = {}
                self.all[user]["money"] = 1000
                self.all[user]["betting"] = 0
                self.all[user]["took_action"] = False
                self.all[user]["end"] = ""
                self.all[user]["cards"] = []
                self.all[user]["username"] = info["username"]
                self.all[user]["selection"] = ""
            if self.all[user]["money"] == 0:
                self.all[user]["money"] = 250

            frame = "Place your bets:"
            if self.all[user]["selection"].strip("0") == "":
                self.all[user]["selection"] = ""

            if input < 10:  # 0-9
                self.all[user]["selection"] += str(input)
            elif input == 10:  # b
                self.all[user]["selection"] = self.all[user]["selection"][:-1]
            else:  # space
                self.state = "bet"

                action: Action = {"action": "change_inputs", "value": ["h", "s"]}

                rt = self.main(
                    input,
                    ExtraInfo(
                        user_id="",
                        username="Dealer",
                        old_frame="",
                        frame=0,
                        deltatime=0,
                        time_between_frame_start=0,
                        file_request_data=None,
                        container_height=info.get("container_height"),
                        container_width=info.get("container_width")
                    ),
                )
                if rt is None:
                    raise RuntimeError
                return MainReturn(
                    frame=rt["frame"],
                    action=action,
                )

            if self.all[user]["selection"] == "":
                self.all[user]["selection"] = "0"
            if int(self.all[user]["selection"]) > self.all[user]["money"]:
                self.all[user]["selection"] = str(self.all[user]["money"])

            frame += "\nPlayers:"
            for player in self.all:
                frame += "\n- %s> Betting %s$, Money Left: %s$" % (
                    self.all[player]["username"],
                    self.all[user]["selection"],
                    self.all[player]["money"] - int(self.all[user]["selection"]),
                )
            if any(self.all[player]["betting"] != 0 for player in self.all):
                action = self.selection_input_change_continue
            else:
                action = self.selection_input_change
        elif self.state == "bet":
            if user == "":  # dealer turn
                if len(self.dealer) == 0:

                    self.dealer.append(self.take_card())
                    self.dealer.append(self.take_card())
                    for player in self.all:
                        if self.all[player]["selection"].strip("0") == "":
                            self.all[player]["betting"] = 0
                            continue
                        self.all[player]["betting"] = int(self.all[player]["selection"])
                        self.all[player]["money"] -= int(self.all[player]["selection"])
                        if self.all[player]["betting"] == 0 or self.all[player]["end"]:
                            continue
                        self.all[player]["end"] = ""
                        self.all[player]["took_action"] = False
                        self.all[player]["cards"].append(self.take_card())
                        self.all[player]["cards"].append(self.take_card())
                else:
                    dealer_worth = get_worth_of_card(self.dealer)
                    if dealer_worth > 21:
                        return self.end("dealer_bust", info)
                    elif dealer_worth == 21:
                        return self.end("dealer_blackjack", info)
                    else:
                        while get_worth_of_card(self.dealer) <= 17:
                            self.dealer.append(self.take_card())
                            if get_worth_of_card(self.dealer) > 21:
                                return self.end("dealer_bust", info)
                        return self.end("dealer_stand", info)

                for player in self.all:
                    if self.all[player]["betting"] == 0 or self.all[player]["end"]:
                        continue
                    self.all[player]["took_action"] = False

            else:
                if not self.all[user]["took_action"]:
                    if get_worth_of_card(self.all[user]["cards"]) == 21:
                        self.all[user]["end"] = "blackjack"
                    if get_worth_of_card(self.all[user]["cards"]) > 21:
                        self.all[user]["end"] = "player_bust"

                    if input == 0:  # hit
                        self.all[user]["cards"].append(self.take_card())
                    elif input == 1:  # stand
                        self.all[user]["took_action"] = True

                    if get_worth_of_card(self.all[user]["cards"]) == 21:
                        self.all[user]["end"] = "blackjack"
                    if get_worth_of_card(self.all[user]["cards"]) > 21:
                        self.all[user]["end"] = "player_bust"

            if all(
                [
                    self.all[player]["betting"] == 0 or self.all[player]["end"]
                    for player in self.all
                ]
            ):
                return self.end("all_end", info)

            frame = "Dealer: %s (%s)" % (
                self.visualize_cards(self.dealer),
                get_worth_of_card(self.dealer),
            )

            #################################################################################### IF ALL PLAYERS ENDED THEIR TURN

            reset_action = all(
                [
                    self.all[player]["took_action"]
                    for player in self.all
                    if self.all[player]["betting"] != 0 or self.all[player]["end"]
                ]
            )
            if reset_action:

                for player in self.all:
                    self.all[player]["took_action"] = False
                rt = self.main(
                    input,
                    ExtraInfo(
                        user_id="",
                        username="Dealer",
                        old_frame="",
                        frame=0,
                        deltatime=0,
                        time_between_frame_start=0,
                        file_request_data=None,
                        container_height=info.get("container_height"),
                        container_width=info.get("container_width")
                    ),
                )
                if rt is None:
                    raise RuntimeError
                return MainReturn(
                    frame=rt["frame"],
                    action={"action": "change_inputs", "value": ["h", "s"]},
                )

            for player in self.all:
                if self.all[player]["betting"] == 0:
                    continue
                frame += "\n%s: %s (%s)" % (
                    self.all[player]["username"],
                    self.visualize_cards(self.all[player]["cards"]),
                    get_worth_of_card(self.all[player]["cards"]),
                )
        elif self.state == "end":
            frame = info["old_frame"]
            self.state = "credits"
            return MainReturn(frame=frame, action=self.selection_input_change)
        elif self.state == "credits":
            self.state = "select"
            rt = self.main(input, info)
            if rt is None:
                raise RuntimeError
            return MainReturn(frame=rt["frame"], action=action)
        else:
            raise NotImplementedError("Unknown state: %s" % self.state)

        return MainReturn(frame=frame, action=action)

    def end(self, end: str, info):
        frame = "Game ended, results:\nDealers cards: %s (%s)" % (
            self.visualize_cards(self.dealer),
            get_worth_of_card(self.dealer),
        )
        dealer_bust = get_worth_of_card(self.dealer) > 21
        dealer_worth = get_worth_of_card(self.dealer)

        for player in self.all:
            reason = ""
            player_card_worth = get_worth_of_card(self.all[player]["cards"])
            if player_card_worth == 21:
                self.all[player]["end"] = "blackjack"
            if player_card_worth > 21:
                self.all[player]["end"] = "busted"

            # Player Black jacks
            if self.all[player]["end"] == "blackjack":
                if not dealer_worth == 21:
                    gain = 2.5
                    self.all[player]["money"] += self.all[player]["betting"] * gain
                    reason = "Blackjack"
                    frame += "\n%s won %s$" % (self.all[player]["username"], gain)
                else:
                    # Dealer Blackjacks
                    gain = self.all[player]["betting"]
                    self.all[player]["money"] += gain
                    reason = "Player and Dealer tied with blackjack"
                    frame += "\n%s Regained their %s$" % (
                        self.all[player]["username"],
                        gain,
                    )
            # Dealer busts
            elif dealer_bust:
                gain = 2
                self.all[player]["money"] += self.all[player]["betting"] * gain
                reason = "Player won because dealer busted"
                frame += "\n%s won %s$" % (self.all[player]["username"], gain)
            elif player_card_worth == dealer_worth:
                gain = self.all[player]["betting"]
                self.all[player]["money"] += self.all[player]["betting"]
                reason = "Player and Dealer tied"
                frame += "\n%s Regained their %s$" % (
                    self.all[player]["username"],
                    gain,
                )
            elif self.all[player]["end"] == "" and player_card_worth > dealer_worth:
                gain = self.all[player]["betting"] * 2
                frame += "\n%s won %s$" % (self.all[player]["username"], gain)
                self.all[player]["money"] += gain
                reason = "Player has higher card value: %s" % player_card_worth
            else:
                frame += "\n%s lost %s$" % (
                    self.all[player]["username"],
                    self.all[player]["betting"],
                )
                if reason == "":
                    reason = self.all[player]["end"]
            frame += ", with deck: %s (%s), reason: %s" % (
                self.visualize_cards(self.all[player]["cards"]),
                player_card_worth,
                reason,
            )
            self.all[player]["betting"] = 0

        if end == "all_end":
            next = self.main(
                0,
                ExtraInfo(
                    user_id="",
                    username="Dealer",
                    old_frame=frame,
                    frame=0,
                    deltatime=0,
                    time_between_frame_start=0,
                        file_request_data=None,
                        container_height=info.get("container_height"),
                        container_width=info.get("container_width")
                ),
            )
            if next is None:
                raise RuntimeError
            return MainReturn(frame=next["frame"], action=self.selection_input_change)
        else:
            for player in self.all:
                if self.all[player]["end"] == "":
                    self.all[player]["end"] = end

        self.state = "end"

        return self.main(
            0,
            ExtraInfo(
                user_id="",
                username="Dealer",
                old_frame=frame,
                frame=0,
                deltatime=0,
                time_between_frame_start=0,
                        file_request_data=None,
                        container_height=info.get("container_height"),
                        container_width=info.get("container_width")
            ),
        )

    def visualize_cards(self, cards: list[list[str]]):
        new = ""
        for suit, rank in cards:
            new += "%s " % generate_card_unicode(suit, rank)
        return new[:-1]

    def regenerate_cards(self):
        self.cards = []
        ranks = [
            "Ace",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
        ]
        suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
        for suit in suits:
            for rank in ranks:
                self.cards.append([suit, rank])
        random.shuffle(self.cards)

    def take_card(self):
        return self.cards.pop()

    def setup(
        self,
        info: SetupInput,
    ) -> Tuple[
        str,
        INPUTS,
    ]:
        "The custom replacement to __init__"
        self.all = {}
        self.dealer = []
        self.regenerate_cards()

        self.selection_input = AdvancedInputs(presets="0-9", custom=["BACKSPACE"])
        self.selection_input_continue = AdvancedInputs(
            presets="0-9", custom=["BACKSPACE", " "]
        )
        self.selection_input_change = Action(
            action="change_inputs",
            value=self.selection_input,
        )
        self.selection_input_change_continue = Action(
            action="change_inputs",
            value=self.selection_input,
        )

        self.state = "select"
        return (
            "Place your bets:",
            self.selection_input,
        )

    def info(self) -> Dict[Literal["name", "id", "description"], str]:
        "Before the game is run, this function is called when adding the game to the library in order to give the user a preview of what to expect"
        return {
            "name": "Blackjack",
            "id": "blackjack",
            "description": "I'm not addicted, but I can still play some blackjack",
        }

