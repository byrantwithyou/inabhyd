import pathlib
import os
from random import seed, shuffle, randint
from functools import reduce
from itertools import count
from ontology import *
from util import *

MIN_HOP = 1
MIN_N = MIN_HOP
MAX_HOP = 4
NUM_MAX_FEW_SHOT_EXAMPLES = 8
SEED = 62471893


def generate_single_example(config: OntologyConfig):
    while True:
        try:
            ontology = Ontology(config)
            break
        except MyWarning as e:
            pass

    return ontology


def log_composite_examples(log_file, composite_examples):
    import pickle

    with open(log_file, 'wb') as file:
        pickle.dump(composite_examples, file)


def check_parameters(args):
    if args.n < MIN_N:
        raise MyError("Must have at least 1 example!")
    if not args.recover_membership and not args.recover_ontology and not args.recover_property:
        raise MyError("Must allow to recover at least one type of axioms!")
    if args.OOD and \
            (args.few_shot_examples < args.recover_membership +
             args.recover_ontology + args.recover_property):
        raise MyError(f"""Must have at least {
            args.recover_membership + args.recover_ontology + args.recover_property} demo examples in the OOD setting!""")
    if args.max_hop < args.min_hop:
        args.min_hop, args.max_hop = args.max_hop, args.min_hop
    if not args.OOD and args.test_hop_diff:
        raise MyError("OOD must be set if test-hop-diff is not zero!")
    if args.test_hop_diff + args.max_hop > MAX_HOP:
        raise MyError(f"Test hop is larger than {MAX_HOP}!")
    if args.test_hop_diff + args.min_hop < MIN_HOP:
        raise MyError(f"Test hop is smaller than {MIN_HOP}!")
    if args.difficulty == Difficulty.SINGLE and args.recover_membership + args.recover_ontology + args.recover_property > 1:
        raise MyError(
            "Under single difficulty level, only one type of axiom missing is supported!")
    if args.difficulty == Difficulty.SINGLE and args.mix_hops:
        raise MyError("SINGLE difficulty level doesn't support mix hop!")
    suffix = []
    if args.few_shot_examples != NUM_MAX_FEW_SHOT_EXAMPLES:
        suffix.append(f"{args.few_shot_examples}shot")
    if args.OOD:
        suffix.append("OOD")
    if args.recover_membership:
        suffix.append("membership")
    if args.recover_ontology:
        suffix.append("ontology")
    if args.recover_property:
        suffix.append("property")
    if args.difficulty != Difficulty.EASY:
        suffix.append(args.difficulty.name.lower())
    if args.seed != SEED:
        suffix.append(f"{args.seed}SEED")
    if args.mix_hops:
        suffix.append("mix")
    return "_".join(suffix)


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--few-shot-examples", "-f", type=int,
                        default=0, help="Number of few shot examples", choices=range(NUM_MAX_FEW_SHOT_EXAMPLES + 1))
    parser.add_argument("--OOD", "-O", action='store_true', help="Support OOD")
    parser.add_argument("--recover-membership", "-m",
                        action='store_true', help="Support recover membership")
    parser.add_argument("--recover-ontology", "-o",
                        action='store_true', help="Support recover ontology")
    parser.add_argument("--recover-property", "-p",
                        action='store_true', help="Support recover property")
    parser.add_argument("--model", type=str, required=True,
                        choices=["gpt", "llama", "gemmi", 'deepseek', 'dry', 'r1', 'o1'])
    parser.add_argument("--min-hop", "-minh", type=int, default=MIN_HOP,
                        help="Min hop in few shot examples", choices=range(MIN_HOP, MAX_HOP + 1))
    parser.add_argument("--max-hop", "-maxh", type=int, default=MAX_HOP,
                        help="Max hop in few shot examples", choices=range(MIN_HOP, MAX_HOP + 1))
    parser.add_argument("-n", type=int, default=100,
                        help="Number of examples per hop")
    parser.add_argument("--test-hop-diff", "-dhop", type=int, default=0,
                        help="The difference between test hop and train hop. OOD must be set.")
    parser.add_argument("--difficulty", "-d", type=str,
                        default='easy',
                        help="""Difficulty mode. Must be chosen from 'single', 'easy', 'medium', or 'hard'. \
                        The more difficult, the more probability that an axiom is missing from the ontology.""",
                        choices=[difficulty.name.lower() for difficulty in Difficulty])
    parser.add_argument("--seed", "-s", type=int, default=SEED,
                        help="Seed for random generations")
    parser.add_argument("--mix-hops", "-mh", action="store_true",
                        help="Allow mix hop reasoning in an ontology tree")
    args = parser.parse_args()
    args.difficulty = Difficulty[args.difficulty.upper()]
    seed(args.seed)
    return args


def get_train_test_configs(args, hops):
    config = OntologyConfig(hops, args.recover_membership,
                            args.recover_ontology,
                            args.recover_property, args.difficulty, args.mix_hops)
    if not args.OOD:
        return [config] * args.few_shot_examples, config
    num_recover_membership = randint(
        args.recover_membership, args.few_shot_examples - args.recover_ontology - args.recover_property)
    num_recover_ontology = randint(
        args.recover_ontology, args.few_shot_examples - num_recover_membership - args.recover_property)
    num_recover_property = args.few_shot_examples - \
        num_recover_membership - num_recover_ontology
    train_configs = [config.easiest_recover_membership,
                     config.easiest_recover_ontology, config.easiest_recover_property]
    weights = [num_recover_membership,
               num_recover_ontology, num_recover_property]
    return reduce(lambda x, y: x + y,  [[train_config] * weight for train_config,
                                        weight in zip(train_configs, weights)], []), config.add_hop(args.test_hop_diff)


if __name__ == "__main__":

    #     response = client.responses.create(
    #         model="gpt-4.1",
    #         input="Write a one-sentence bedtime story about a unicorn."
    #     )

    # print(response.output_text)

    args = parse_arguments()
    is_open_ai = (args.model == 'gpt' or args.model == 'o1')
    if is_open_ai:
        from openai import OpenAI
        client = OpenAI()
    else:
        from together import Together

    log_suffix = check_parameters(args)
    for hops in range(args.min_hop, args.max_hop + 1):
        log_file = f"{hops}hop_{
            f"{hops + args.test_hop_diff}testhop_" if args.test_hop_diff != 0 else ""}{log_suffix}"
        # log_file = log_file + ".pkl"
        pathlib.Path(log_file).unlink(missing_ok=True)
        composite_examples = []
        for _ in range(args.n):
            composite_example = {
                "few_shot_examples": [],
                "test_example": None,
            }
            train_configs, test_config = get_train_test_configs(args, hops)
            for train_config in train_configs:
                composite_example["few_shot_examples"].append(
                    generate_single_example(train_config))

            composite_example["test_example"] = generate_single_example(
                test_config)
            shuffle(composite_example["few_shot_examples"])
            # PROMPT = " Please come up with hypothesis to explain observations."
            # for example in composite_example["few_shot_examples"]:
            #     composite_example["prompt"] += "Q: " + example["theories"] + " " + example["observations"] + PROMPT + os.linesep
            #     composite_example["prompt"] += "A: " + example["CoT"] + os.linesep
            # composite_example["prompt"] += "Q: " + composite_example["test_example"]["theories"] + " " + composite_example["test_example"]["observations"] + PROMPT + os.linesep

            composite_examples.append(composite_example)
        shuffle(composite_examples)
        content = """You are a helpful assitant that performs abduction and induction reasoning.
        Your job is to come up with hypotheses that explain observations with given theories. Each hypothesis should explain as many observations as possible.
        You can come up with multiple hypotheses and each hypothesis should take one line with the format A is B or A is not B.
    .   Only output final hypotheses.
 """
        replies = []
        model = ''
        if args.model == 'gpt':
            model = "gpt-4o"
        if args.model == 'llama':
            model = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'
        if args.model == 'gemmi':
            model = "google/gemma-2-27b-it"
        if args.model == 'deepseek':
            model = "deepseek-ai/DeepSeek-V3"
        if args.model == 'dry':
            model = "dry"
        if args.model == "r1":
            model = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
        if args.model == 'o1':
            model = 'o1'
        if model != "dry":
            for i, composite_example in enumerate(composite_examples):
                if i % 5 == 0:
                    print(i)
                # assert len(composite_example['few_shot_examples']) == 0
                ontology = composite_example['test_example']

                if args.model != 'r1' and args.model != 'o1':
                    template = " Please come up with hypothesis to explain observations."
                    PROMPT = "Q: " + ontology.theories + \
                        " We observe that: " + ontology.observations + template
                    completion = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "developer" if is_open_ai else "system",
                                "content": content},
                            {
                                "role": "user",
                                "content": PROMPT,
                            },
                        ],
                        temperature=0,
                    )
                if args.model == 'r1' or args.model == 'o1':
    #                         content = """You are a helpful assitant that performs abduction and induction reasoning.
    #     Your job is to come up with hypotheses that explain observations with given theories. Each hypothesis should explain as many observations as possible.
    #     You can come up with multiple hypotheses and each hypothesis should take one line with the format A is B or A is not B.
    # .   Only output final hypotheses."""

                    # template = " Please come up with hypothesis to explain observations. You can come up with multiple hypotheses. Each hypothesis should take one line with the format A is B or A is not B. Each hypothesis should explain as many observations as possible. Final hypotheses should come after the thinking process."
                    template = " Please come up with hypotheses to explain observations. Put only most possible final hypotheses in the end without explanation."
                    PROMPT = template + ontology.theories + \
                        " We observe that: " + ontology.observations
                    completion = client.chat.completions.create(
                        model=model,
                        messages=[
                            # {"role": "developer" if is_open_ai else "system", "content": content},
                            {
                                "role": "user",
                                "content": PROMPT,
                            },
                        ],
                        # temperature=0,
                        # top_p=.95
                    )

                replies.append(completion.choices[0].message.content)
                # print(replies[0])

            import pickle
            with open(log_file + f"_reply_{args.model}.pkl", "wb") as file:
                pickle.dump(replies, file)
                # print(completion.choices[0].message.content)

        # log_composite_examples(log_file, composite_examples)
