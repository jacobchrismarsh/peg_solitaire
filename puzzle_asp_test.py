from clyngor import ASP, solve
import peg_solitaire_game as psg
import sys
import re

if __name__ == "__main__":
    # ASP input from the C# settings
    if len(sys.argv) != 2:
        exit()

    answerSet = [x.strip() for x in re.split(
                    "(?<=[A-Za-z0-9\)\}])\.{1}(?=[A-Za-z0-9\(\{:%])",
                    sys.argv[1])]

    # Solve using clyngor wrapper; Get the peg atoms from the answer
    count = 0
    maxCount = 1000
    answers = ASP(sys.argv[1], options="--rand-freq=1 --seed=1", time_limit=5)
    shapeList = []

    for answer in answers:
        shapeList.append(answer)

        count += 1
        if count >= maxCount:
            break

    print("Created the Answer Sets...")
    psg.main(shapeList)