using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using UnityEngine.SceneManagement;


public class mainGUI : MonoBehaviour {
	// Minimum size for the total width of the peg solitaire board
	private const string PY_PATH = "C:/Users/Spencer/AppData/Local/Programs/Python/Python36/python.exe";
	public const int MIN_SIZE = 7;
	// The minimum width for either horizontal or vertical peg channels
	public const int MIN_WIDTH = 3;
	// Arbitrary range for setting "some pegs" in Unity GUI
	public const int PEG_RANGE = 5;
	public UnityEngine.UI.Slider difficultySlider;
	public UnityEngine.UI.Dropdown adapterDropdown;
	public UnityEngine.UI.Dropdown sizeDropdown;
	public UnityEngine.UI.Dropdown shapeDropdown;
	public UnityEngine.UI.Dropdown themeDropdown;
	public UnityEngine.UI.Text debugOut;

	// Use this for initialization
	void Start () {
		// Acquire information from Unity UI
		debugOut = GameObject.Find("DebugText")
						     .GetComponent<UnityEngine.UI.Text>();
		difficultySlider = GameObject.Find("DifficultySlider")
									 .GetComponent<UnityEngine.UI.Slider>();
		adapterDropdown = GameObject.Find("AdaptiveDropdown")
								    .GetComponent<UnityEngine.UI.Dropdown>();
		sizeDropdown = GameObject.Find("SizeDropdown")
								 .GetComponent<UnityEngine.UI.Dropdown>();
		shapeDropdown = GameObject.Find("ShapeDropdown")
								  .GetComponent<UnityEngine.UI.Dropdown>();
		themeDropdown = GameObject.Find("ColorDropdown")
								  .GetComponent<UnityEngine.UI.Dropdown>();
		debugOut.text = "Click on 'Generate Puzzles' to make puzzles and see what numerical settings are set.";
	}
	
	// Update is called once per frame
	void Update () {
		
	}

	public void GenerateButtonClick () {
		ProcessStartInfo start = new ProcessStartInfo();
		string aspBoard = ASPMaker();
		string outputString = "";

        outputString += string.Format("Difficulty Slider = {0}.\n",
									  difficultySlider.value);
		outputString += string.Format("Adaptive Dropdown = {0}.\n",
		                              adapterDropdown.value);
		outputString += string.Format("Size = {0} x {0}.\n", 
								      (int) sizeDropdown.value + MIN_SIZE);
		outputString += string.Format("Shape = {0}.\n", shapeDropdown.value);
		outputString += string.Format("Theme = {0}.\n", themeDropdown.value);
		debugOut.text = outputString;

		string pythonFile = "C:/Users/Spencer/Desktop/Current_QTR_Doc's/CSC 570/ASP-Test/puzzle_asp_test.py";
		start.FileName = PY_PATH;
		start.Arguments = string.Format("\"{0}\" \"{1}\"",
		                                pythonFile, aspBoard);
		start.UseShellExecute = false;
		start.CreateNoWindow = false;
		start.RedirectStandardError = true;
		using (Process process = Process.Start(start)) {
			using (StreamReader reader = process.StandardError) {
				string result = reader.ReadToEnd();
				UnityEngine.Debug.Log(result);
				// Here is probably where we can put the ASCII boards into a array or simply let them sit in STDIN
				//    until they are read out of STDIN
			}
		}
	}

	/* Creates the text necessary for the Python clyngor library to recognize
	 *   it as ASP and make solutions for the given rules.
	 * Will be using the toggles, dropdowns, and sliders from the GUI.
	 */
	string ASPMaker() {
		string aspLogicRules = string.Format("#const width = {0}.",
		                                     (int) sizeDropdown.value + MIN_SIZE);
		int totalArea = 0;
	
		aspLogicRules += "dim(1..width).";
		aspLogicRules += "size(width,width).";

		Dictionary<int, string> shape = shapeUI((int) sizeDropdown.value + MIN_SIZE);
		totalArea = retrieveAreaFromDict(shape);
		aspLogicRules += retrieveRulesFromDict(shape);

		// How many pegs are requested?
		aspLogicRules += difficultyUI((int) difficultySlider.value, (int) adapterDropdown.value, totalArea - 1);
		aspLogicRules += string.Format("linked({0},{0}).", (int) Mathf.Ceil(((float) sizeDropdown.value + MIN_SIZE) / 2));
		aspLogicRules += "linked(X,Y) :- dim(X), dim(Y), DX=(-1..1), DY=(-1..1), (DX, DY) != (-1;1,-1;1), linked(X+DX,Y+DY), not out(X,Y).";
		
		// Get rid of any possibilities where the ASP does not link squares or where they are most likely unsolvable
		aspLogicRules += solvabilityRules();
		aspLogicRules += "unlinked(X,Y) :- dim(X), dim(Y), not out(X,Y), not linked(X,Y).";
        aspLogicRules += ":- dim(X), dim(Y), unlinked(X,Y).";

		// Display only certain predicates/atoms
		// aspLogicRules += "#show size/2.";
		// aspLogicRules += "#show linked/2.";
		// aspLogicRules += "#show area/1.";
		// aspLogicRules += "#show numpegs/1.";
		// aspLogicRules += "#show out/2.";
		// aspLogicRules += "#show peg/2.";

		return aspLogicRules;
	}

	/*
	 * Stated predicates and integrity constraints to help in the solvability of the peg puzzle boards
	 * ...it also may decrease the search space of the ASP board generation
	 */
	string solvabilityRules() {
		string rules = "";
		rules = "noneighbor(X,Y,N) :- peg(X,Y), N = #count {neighbor(A,B) : (A,B)=(X+1,Y;;X,Y+1;;X-1,Y;;X,Y-1), peg(A,B), peg(X,Y)}, dim(X), dim(Y).";
		rules += "x(X,Y) :- (X,Y) = #min { (A,B) : dim(A), dim(B), linked(A,B) }.";
		rules += "y(X,Y) :- dim(X), dim(Y), x(X-1,Y;;X,Y-1), linked(X,Y).";
		rules += "z(X,Y) :- dim(X), dim(Y), y(X-1,Y;;X,Y-1), linked(X,Y).";
		rules += "x(X,Y) :- dim(X), dim(Y), z(X-1,Y;;X,Y-1), linked(X,Y).";
		rules += "y(X,Y) :- dim(X), dim(Y), z(X+1,Y;;X,Y+1), linked(X,Y).";
		rules += "z(X,Y) :- dim(X), dim(Y), x(X+1,Y;;X,Y+1), linked(X,Y).";
		rules += "x(X,Y) :- dim(X), dim(Y), y(X+1,Y;;X,Y+1), linked(X,Y).";
		rules += "xcount(N) :- N = #count { x(X,Y) : dim(X), dim(Y), peg(X,Y), x(X,Y) }.";
		rules += "ycount(N) :- N = #count { y(X,Y) : dim(X), dim(Y), peg(X,Y), y(X,Y) }.";
		rules += "zcount(N) :- N = #count { z(X,Y) : dim(X), dim(Y), peg(X,Y), z(X,Y) }.";
		rules += "nosoln(1) :- A == B, B == C, xcount(A), ycount(B), zcount(C).";
		rules += "nosoln(5) :- A == 0, B == 0, C == 0, xcount(A), ycount(B), zcount(C).";
		rules += ":- dim(X), dim(Y), noneighbor(X,Y,0).";
		rules += ":- nosoln(1).";
		return rules;
	}

    string difficultyUI(int difficulty, int adapt, int maxPegs) {
		string rules = "";
		int mid = (int) Mathf.Ceil(((float) sizeDropdown.value + MIN_SIZE) / 2);

		// Determine the number of pegs allowed through the shape-established areas
		rules += string.Format("diffoffset(A) :- A = AR * (3 + {0}) * 15 / 100, area(AR).", difficulty);
		rules += "numpegs(A) :- A = #min { AR - 1; OFFS}, area(AR), diffoffset(OFFS).";

		// Are we changing difficulty or not?
		if (adapt == 0 || adapt == 1) {
			rules += "pegadaptrange(0..5).";
		}
		else {
			rules += "pegadaptrange(0..0).";
		}

		// Do we increase or decrease the difficulty?
		if (adapt == 0) {
			rules += "pegadapt(A) :- A = -1 * AR * 10 / 100, area(AR).";
		}
		else if (adapt == 1) {
			rules += "pegadapt(A) :- A = AR * 10 / 100, area(AR).";
		}
		else {
			rules += "pegadapt(0).";
		}

		// Add the rules for # OF PEGS
		rules += "N + P * C { peg(A,B) : dim(A), dim(B), not out(A,B) } END-1";
		rules += " :- pegadaptrange(P), pegadapt(C), numpegs(N), area(END).";
		return rules;
	}

	Dictionary<int, string> shapeUI(int width) {
		string rules = "";
		Dictionary<int, string> returnVal = new Dictionary<int, string>();
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		int area = width * width;

		switch((int) shapeDropdown.value) {
			// Square shape, don't take away anything
			case 0:
				rules += "square.";
				rules += string.Format("sqarea({0}) :- square.", area);
				break;

			// Square Ears - digs into the middle of the board from the outside edge
			case 1:
				rules += "ears.";
				tempDict = genEars(width);
				area = retrieveAreaFromDict(tempDict);
				rules += retrieveRulesFromDict(tempDict);
				break;

			// Rectangle shape, take away rows at a time
			// Req: 3+ width or length for rows or columns respectively
			case 2:
				rules += "rect.";
				tempDict = genRect(width);
				area = retrieveAreaFromDict(tempDict);
				rules += retrieveRulesFromDict(tempDict);
				break;

			// Cross shape, take away squares of the grid
			case 3:
				rules += "cross.";
				tempDict = genCross(width);
				area = retrieveAreaFromDict(tempDict);
				rules += retrieveRulesFromDict(tempDict);
				break;
			
			// Generate H-letters
			case 4:
				rules += "hshape.";
				tempDict = genHshape(width);
				area = retrieveAreaFromDict(tempDict);
				rules += retrieveRulesFromDict(tempDict);
				break;

			// Corners have random area from 0 to however much is allowed given MIN_WIDTH
			case 5:
				rules += "corner.";
				tempDict = genCorner(width);
				area = retrieveAreaFromDict(tempDict);
				rules += retrieveRulesFromDict(tempDict);
				break;

			// Random shape, take away random rows or squares
			// Req: 3+ width or length for rows or columns respectively
			case 6:
				// Place SQUARE rules
				rules += "1 { square; ears; rect; cross; hshape; corner } 1.";
				rules += string.Format("sqarea({0}) :- square.", area);
				// Place SQUARE EARS rule
				tempDict = genEars(width);
				rules += retrieveRulesFromDict(tempDict);
				// Place RECTANGLE rules
				tempDict = genRect(width);
				rules += retrieveRulesFromDict(tempDict);
				// CROSS rules
				tempDict = genCross(width);
				rules += retrieveRulesFromDict(tempDict);
				// H-SHAPE rules
				tempDict = genHshape(width);
				rules += retrieveRulesFromDict(tempDict);
				// CORNER RMV rules
				tempDict = genCorner(width);
				rules += retrieveRulesFromDict(tempDict);
				break;

			default:
				rules += "square.";
				rules += string.Format("sqarea({0}) :- square.", area);
				break;
		}
		// Place rules for what area to use
		rules += "area(A) :- square, sqarea(A).";
		rules += "area(A) :- ears, earsarea(A).";
		rules += "area(A) :- rect, rectarea(A).";
		rules += "area(A) :- cross, crossarea(A).";
		rules += "area(A) :- hshape, harea(A).";
		rules += "area(A) :- corner, cornerarea(A).";
		returnVal.Add(area, rules);
		return returnVal;
	}

	/** genEars
	 * Provides the ASP rules necessary for generating a square shape with ears
	 * param: int width - the width of the board
	 */
	Dictionary<int, string> genEars(int width) {
		string rules = "";
		int area = width * width;
		// int mid = (int) Mathf.Ceil((float) sizeDropdown.value / 2);
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		// int deepIdx = (int) (UnityEngine.Random.value * 2) + 1;
		int deepIdx = 1;
		int wideIdx1 = deepIdx + MIN_WIDTH;
		int wideIdx2 = width - (deepIdx - 1) - MIN_WIDTH;

		rules += string.Format("eardeeprange(1..{0};{1}..width).", deepIdx, width - (deepIdx - 1));
		rules += string.Format("earwiderange({0}..{1}).", wideIdx1, wideIdx2);
		rules += "out(X,Y) :- ears, eardeeprange(X), earwiderange(Y).";
		rules += "out(X,Y) :- ears, eardeeprange(Y), earwiderange(X).";

		area -= 4 * (deepIdx * (1 + wideIdx2 - wideIdx1));
		rules += string.Format("earsarea({0}) :- ears.", area);
		tempDict.Add(area, rules);
		return tempDict;
	}

	/** genRect
	 * Provides the ASP rules necessary for generating a rectangular shape
	 * param: int width - the width of the board
	 */
	Dictionary<int, string> genRect(int width) {
		string rules = "";
		int area = width * width;
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		// Randomize which sides (horiz, vert) get deleted and how large
		int firstIdx = (int) UnityEngine.Random.value * (width / 2 - 2) + 1;
		int secondIdx = (width + 1) - (int) (UnityEngine.Random.value * (width - firstIdx - MIN_WIDTH - 1));

		rules += "1 { rectshape(1;2) } 1 :- rect.";
		rules += string.Format("out(X,Y) :- rectshape(1), dim(X), Y = (1..{0}; {1}..{2}).", firstIdx, secondIdx, width);
		rules += string.Format("out(X,Y) :- rectshape(2), dim(Y), X = (1..{0}; {1}..{2}).", firstIdx, secondIdx, width);
		area -= (firstIdx * width + (width - secondIdx + 1) * width);
		rules += string.Format("rectarea({0}) :- rect.", area);
		
		tempDict.Add(area, rules);
		return tempDict;
	}

	/** genCross
	 * Provides the ASP rules necessary for generating a Cross shape.
	 * param: int width - the width of the board
	 */
	Dictionary<int, string> genCross(int width) {
		string rules = "";
		int area = width * width;
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		int rnd = (int) (UnityEngine.Random.value * (width / 2)) + 1;
		int rnd_end = (int) (UnityEngine.Random.value * (width - rnd - MIN_WIDTH));

		rules += string.Format("range(1..{0}; {1}..{2}).", rnd, width - rnd_end, width);
		rules += "out(X,Y) :- cross, range(X), range(Y).";
		area -= (rnd * rnd) + 2 * (rnd * (rnd_end + 1)) + ((rnd_end + 1) * (rnd_end + 1));
		rules += string.Format("crossarea({0}) :- cross.", area);

		tempDict.Add(area, rules);
		return tempDict;
	}

	/** genHshape
	 * Provides the ASP rules necessary for generating an H shape sideways or standing upright.
	 * param: int width - the width of the board
	 */
	Dictionary<int, string> genHshape(int width) {
		string rules = "";
		int area = width * width;
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		//int mid = (int) Mathf.Ceil((float) width / 2);

		rules += "1 { hside(1;2) } 1 :- hshape.";
		rules += string.Format("hxrange({0}..{1};{2}..{3}).", 1, (int) ((width - MIN_WIDTH) / 2),
			                   width - (int) ((width - MIN_WIDTH) / 2) + 1, width);
		rules += string.Format("hyrange({0}..{1}).", 1 + MIN_WIDTH, width - MIN_WIDTH);
		rules += string.Format("out(X,Y) :- hside(1), hxrange(X), hyrange(Y).");
		rules += string.Format("out(X,Y) :- hside(2), hyrange(X), hxrange(Y).");
		area -= 2 * ((int) ((width - MIN_WIDTH) / 2)) * (width - MIN_WIDTH - MIN_WIDTH);
		rules += string.Format("harea({0}) :- hshape.", area);

		tempDict.Add(area, rules);
		return tempDict;
	}

	/** genCorner
	 * Provides the ASP rules necessary for generating a square shape with random Corner removals.
	 * param: int width - the width of the board
	 */
	Dictionary<int, string> genCorner(int width) {
		string rules = "";
		int area = width * width;
		Dictionary<int, string> tempDict = new Dictionary<int, string>();
		int rnd_x, rnd_y, rnd_x_end, rnd_y_end;

		// Get random values for the size of sections that will be "out"
		if (UnityEngine.Random.value < 0.5) {
			rnd_x = (int) (UnityEngine.Random.value *
							(width - MIN_WIDTH)) + 1;
			rnd_y = (int) (UnityEngine.Random.value *
							Mathf.Ceil((float) width / 2)) + 1;
		}
		else {
			rnd_x = (int) (UnityEngine.Random.value *
							Mathf.Ceil((float) width / 2)) + 1;
			rnd_y = (int) (UnityEngine.Random.value *
							(width - MIN_WIDTH)) + 1;
		}
		// These two determine the range of the second range
		rnd_x_end = (int) (UnityEngine.Random.value *
							(width - rnd_x - MIN_WIDTH));
		rnd_y_end = (int) (UnityEngine.Random.value *
							(width - rnd_y - MIN_WIDTH));
		// Make the ASP rules for the ASP solver

		rules += string.Format("randxrange(1..{0}; {1}..{2}).",
								rnd_x, width - rnd_x_end + 1, width);
		rules += string.Format("randyrange(1..{0}; {1}..{2}).",
								rnd_y, width - rnd_y_end + 1, width);
		rules += "out(X,Y) :- corner, randxrange(X), randyrange(Y).";
		area -= (rnd_x * rnd_y) + (rnd_x_end * rnd_y_end) + (rnd_x * rnd_y_end) + (rnd_y * rnd_x_end);
		rules += string.Format("cornerarea({0}) :- corner.", area);

		tempDict.Add(area, rules);
		return tempDict;
	}

	int retrieveAreaFromDict(Dictionary<int, string> shapeDict) {
		int[] keys = new int[1];
		shapeDict.Keys.CopyTo(keys, 0);
		return keys[0];
	}

	string retrieveRulesFromDict(Dictionary<int, string> shapeDict) {
		string[] rules = new string[1];
		shapeDict.Values.CopyTo(rules, 0);
		return rules[0];
	}
}
