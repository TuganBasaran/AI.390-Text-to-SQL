import json
import pandas as pd
import time
from gemini_utils import generate_sql

df = pd.read_csv("data/orders.csv")
df["order_date"] = pd.to_datetime(df["order_date"])

with open("data/testbench.json") as f:
    tests = json.load(f)

total = len(tests)
match_count = 0

# usage of 15 sized chunks
for chunk_start in range(0, len(tests), 15):
    chunk = tests[chunk_start:chunk_start+15]

    for i, test in enumerate(chunk, chunk_start + 1):
        generated_sql = generate_sql(test["question"])
        expected_sql = test["expected_sql"]

        print(f"\n🧪 Test {i}: {test['question']}")
        print(f"✅ Expected:\n{expected_sql}")
        print(f"🤖 Generated:\n{generated_sql}")

        clean_expected = expected_sql.lower().replace(" ", "").replace(";", "")
        clean_generated = generated_sql.lower().replace(" ", "").replace(";", "")

        if clean_expected in clean_generated:
            print("✅ MATCH")
            match_count += 1
        else:
            print("❌ MISMATCH")

        time.sleep(2)

    print("\n🕐 15 queries completed. Waiting for 1 minute...\n")
    time.sleep(60) #waiting for one minute after 1 chunk executed

#the percentage of match-mismatch
print(f"\n🎯 TEST RESULT: {match_count}/{total} matched ({round(match_count/total*100)}%)")