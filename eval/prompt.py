import json, os, sys

t, path = sys.argv[1], sys.argv[2]
truth = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "truth.json")))
qs = {k: v[0] for k, v in truth[t]["questions"].items()}
print(
    f"Use the Read tool to view the image at {path}. Then answer the questions below about what the image shows.\n"
    "Reply with only a JSON object that maps each question id to your answer as a string, with no other text.\n"
    'Write "UNREADABLE" as the answer when you cannot read a value with confidence. Copy codes exactly as shown.\n\n'
    "Questions:\n" + json.dumps(qs, indent=1)
)
