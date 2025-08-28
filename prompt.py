import argparse
import pickle
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str,
                    required=True, help="Files to generate prompts")
parser.add_argument("--models", "-m", type=str, help="Model to run")
args = parser.parse_args()
print(args)
with open(args.file, 'rb') as file:
    examples = pickle.load(file)
# for example in examples[:1]:
#     print(type(example))

# from openai import OpenAI
# import argparse
# client = OpenAI()
# import json, sys

# # parser = argparse.ArgumentParser()
# # parser.add_argument("--model", "-m", type=str,
# #                     default='gpt-4o-mini', choices=['gpt-4o-mini', 'o1'])
# # args = parser.parse_args()
# prompt = """
#             "theories": "bongits are starples. every yumpus is mean. each serpee is a shimpee. each starple is not bitter. each yempor is a bongit. every yumpus is translucent. Jennifer is a zhomple. every zhomple is a shimpee. Heather is a serpee. yumpuses are starples. every kurpor is nervous. Alexander is a starple. Christopher is a zhomple. Patricia is a fomple. Donald is a starple. each shimpee is a starple. Jerry is a numpus. kurpors are not floral. numpuses are yumpuses. every kurpor is a bongit. each fomple is a yumpus. George is an urpant. every bongit is kind. Michael is a shimpee. Andrew is a lemper. Kevin is a yempor. Gregory is an urpant. Joshua is a starple. each lemper is a yumpus. each starple is not moderate. Elizabeth is a zhomple. Karen is an urpant. each quimpant is a bongit. Lisa is a quimpant.",
#             "observations": "Karen is a shimpee. Ronald is not moderate. Edward is not floral. Gregory is a shimpee. Ronald is mean. Michael is bright. Joshua is bright. George is a shimpee. Christopher is not sad. Donald is a lirpin. Melissa is not bitter. Melissa is a lirpin. Edward is kind. Alexander is bright. Edward is nervous. Jennifer is not sad. Lisa is a lirpin. Elizabeth is not sad. Ronald is translucent. Melissa is not moderate. Melissa is kind.",
# Please come up with hypothesis to explain observations. Don't show step-by-step reasoning.
# """
# prompt = prompt.strip()
# # if args.model == 'gpt-4o-mini':
# messages=[
#     {"role": "developer", "content":
#     """You are a helpful assitant that performs abduction and induction reasoning.
#     Your job is to choose or come up with hypotheses that explain observations with given theories.
#     There are three requirements.
#     1. When you are asked to choose between hypotheses, only output the final choice as a single capitalized letter.Choose the set of hypotheses that can explain ALL observations. If there are multiple hypotheses that can explain all observations, choose the one where each hypothesis on avearge explain most number of observations.
#     2. When you are asked to come up hypotheses, keep your hypotheses short but clear.
#     Each hypothesis should have the format A is (not) B, where it can either conjecture a property of a concept (e.g., Cat is lovely.), relationship between an entity and a concept (e.g., Sally is a cat.), or relationship between concepts (e.g., Cats are mammals.).
#     You may come up with multiple hypotheses. Each one should take one line.
#     Each hypothesis should explain as many observations as possible.
#     3. When you are asked to show step-by-step reasoning, show how to use your hypotheses and given theories to deductively explain ALL observations. Each reasoning step should also take the format of A is (not) B. Each reasoning step should take one line. You should explain each observation separately.
#     """},
#     {
#         "role": "user",
#         "content": f"{prompt}"
#     }
# ]
# # else:
# #     messages=[
# #         # {"role": "system", "content": "You are a helpful assistant."},
# #         {
# #             "role": "user",
# #             "content": f"{prompt}"
# #         }
# #     ]


# completion = client.chat.completions.create(
#     model='o1',
#     messages=messages,
#     # temperature= 0
# )
# response = completion.choices[0].message.content
# # with open(args.o, "a") as file:
# #     file.write(prompt.replace("\n", " ") + "\n")
# #     file.write(response.replace("\n", " ") + "\n")
# # print(data[0]["test_example"]["readable_ontology"])
# print(response)
