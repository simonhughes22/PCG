from dataclasses import dataclass
from typing import Any, List
from utils import Singleton, StringUtils

RULES = """

# group vocab items
north,south,east,west                   =><CompassDir>
above,up,climb up                       =><VerticalUp>
below,down,climb down                   =><VerticalDown>
sword,shield,torch,key                  =><PickUpAble>
potion                                  =><Consumable>

dragon,troll,snake,rat                  =><Creature>
attack,fight,hit,punch                  =><FightVerb>
headbutt,headbut,kick                   =><FightVerb>

# collapse different vocab
pick up,pickup,take                     =>get
hold,grab,equip,wield                   =>hold
kill                                    =>attack

# actions
move|go|head <CompassDir>               =>[move] <CompassDir>
move|go|head <VerticalUp>               =>[move] above
<VerticalUp>                            =>[move] above
move|go <VerticalDown>                  =>[move] below
<VerticalDown>                          =>[move] below

<FightVerb> <Creature>                  =>[fight] <Creature> <FightVerb>
use|drink|consume <Consumable>          =>[consume] <Consumable>

get <PickUpAble>                        =>[pickup] <PickUpAble>
get <Consumable>                        =>[pickup] <Consumable>
drop <PickUpAble>                       =>[drop] <PickUpAble>
drop <Consumable>                       =>[drop] <Consumable>

hold <PickUpAble>                       =>[hold] <PickUpAble>

# special commands
quit,exit                               =>[end_game]
describe                                =>[describe]
describe room|place                     =>[describe]
where am i|i?                           =>[describe]
info                                    =>[info]

help,h,?                                =>[help]
inventory                               =>[list_inventory]
holding|holding?                        =>[holding]
what am i holding|holding?              =>[holding]
drop all                                =>[drop_all]

""".strip().split("\n")

@dataclass
class Token(object):
    token: str
    data: Any

@dataclass
class ParseResult(object):
    is_valid: bool
    method: str = ""
    args: Any = None

class Parser(Singleton):
    StopWords = set("a,an,the".split(","))

    def __init__(self):
        self.build_fst(RULES)

    # handles | (or) tokens
    def generate_or_variants(self, tokens):
        l_toks = [[]]
        for token in tokens:
            new_l = []
            for tok in token.split("|"):
                for lst in l_toks:
                    new_l.append(lst + [tok])
            l_toks = new_l
        return l_toks

    def build_fst(self, rules):
        all_tokens = set()
        fst = dict()
        for line in rules:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            left, right = line.split("=>")
            left = left.strip()
            right = right.strip()

            lhs_phrases = [phrase.strip().split(" ") for phrase in left.split(",")]
            assert "," not in right, "Multiple right hand phrases not supported for now"

            rhs_phrases = [t.strip() for t in right.split(" ") if len(t.strip()) > 0]
            all_tokens.update(rhs_phrases)
            for tokens in lhs_phrases:
                # remove empty tokens
                raw_tokens = [t for t in tokens if len(t.strip()) > 0]
                if not raw_tokens:
                    continue

                # Generate permutations of lhs rule when OR chars present
                lst_tokens = self.generate_or_variants(raw_tokens)
                for tokens in lst_tokens:
                    all_tokens.update(tokens)
                    # build dictionary for phrase
                    dct = fst
                    for tok in tokens[:-1]:
                        if tok not in dct:
                            dct[tok] = tuple([None, dict()])
                        dct = dct[tok][1]
                    # last token
                    tok = tokens[-1]
                    if tok not in dct:
                        dct[tok] = tuple([rhs_phrases, dict()])
                    else:
                        rhs_tpl = dct[tok]
                        assert rhs_tpl[0] is None, (left, right, tokens, rhs_tpl)
                        # update tuple
                        dct[tok] = tuple([rhs_phrases, rhs_tpl[1]])

        self.fst = fst
        self.vocab = all_tokens

    def process_rules(self, tokens: List[Token]) -> List[Token]:
        rule_matched = True
        def hash_tokens(toks):
            return  ",".join([t.token for t in toks])

        tok_hash = hash_tokens(tokens)
        while rule_matched:
            tokens, rule_matched = self.process_rules_inner(tokens)
            new_tok_hash = hash_tokens(tokens)
            # Prevent loops - has the set of tokens changed?
            if new_tok_hash == tok_hash:
                break
            tok_hash = new_tok_hash
        return tokens

    def process_rules_inner(self, tokens: List[Token]):
        output = []
        ix = 0
        rule_matched = False

        while ix < len(tokens):
            current_tok = tokens[ix]
            if current_tok.token not in self.vocab:
                ix += 1
                continue

            if current_tok.token not in self.fst:
                # skip unrecognized for now
                output.append(current_tok)
            else:
                best_rhs = None
                dct = self.fst
                num_tokens_matched = 0  # how long into the tokens array did we go?
                remainder = tokens[ix:]
                for tok in remainder:

                    if not tok.token in dct:
                        break
                    num_tokens_matched += 1
                    emit, dct = dct[tok.token]
                    if emit:
                        best_rhs = emit
                    # partial match only
                    if not dct:
                        break
                if not best_rhs:
                    output.append(current_tok)
                else:
                    rule_matched = True
                    matched = remainder[:num_tokens_matched]
                    diff = [t.token for t in matched if t.token not in best_rhs]
                    str2token = dict([(t.token, t) for t in matched])
                    # print(matched, best_rhs)
                    for str_tok in best_rhs:
                        data = diff
                        if str_tok in str2token:
                            # if token on both sides, carry over the data, e.g. move|go <CompassDir>  =>[move] <CompassDir>
                            data = str2token[str_tok].data
                        new_tok = Token(token=str_tok, data=data)
                        output.append(new_tok)
                    ix += num_tokens_matched - 1  # minus 1 as we are about to add one in a sec
            ix += 1
        return output, rule_matched

    def parse(self, s):
        tokens = [Token(data=t, token=t) for t in StringUtils.clean(s).split(" ")
                  if t not in Parser.StopWords]

        if not tokens:
            return ParseResult(is_valid=False)

        tokens = self.process_rules(tokens)
        for i in range(len(tokens)):
            tok = tokens[i]
            if tok.token.startswith("["):
                method = tok.token[1:-1]
                args = [t.data for t in tokens[i + 1:]]
                return ParseResult(is_valid=True, method=method, args=args)

        return ParseResult(is_valid=False)