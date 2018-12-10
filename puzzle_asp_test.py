import clyngor
clyngor.CLINGO_BIN_PATH = "/usr/local/bin/clingo"
from clyngor import ASP, solve
import peg_solitaire_game as psg
import peg_solitaire_board_cmp as bcomp
import sys
import re
import time


if __name__ == "__main__":
    # ASP input from the C# settings
    if len(sys.argv) != 3:
        exit()

    answerSet = [x.strip() for x in re.split(
                    "(?<=[A-Za-z0-9\)\}])\.{1}(?=[A-Za-z0-9\(\{:%])",
                    sys.argv[1])]

    # Solve using clyngor wrapper; Get the peg atoms from the answer
    count = 0
    maxCount = 1000
    answers = ASP(sys.argv[1], options="--rand-freq=1 --seed=1")
    shapeList = []

    t_0 = time.time()
    for answer in answers:
        shapeList.append(answer)

        count += 1
        if count >= maxCount:
            break
    t_1 = time.time()

    print("Created {0} Answer Sets...".format(len(shapeList)))
    print("It took {0} seconds.".format(t_1 - t_0))

    if (sys.argv[2] == '0'):
        psg.main(shapeList)
    else:
        bcomp.main(shapeList, cmp=sys.argv[2])
