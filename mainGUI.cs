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
	public UnityEngine.UI.Dropdown neighborDropdown;
	public UnityEngine.UI.Dropdown pegDropdown;
	public UnityEngine.UI.Dropdown shapeDropdown;
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
		neighborDropdown = GameObject.Find("NeighborDropdown")
									 .GetComponent<UnityEngine.UI.Dropdown>();
		pegDropdown = GameObject.Find("PegDropdown")
								.GetComponent<UnityEngine.UI.Dropdown>();
		shapeDropdown = GameObject.Find("ShapeDropdown")
								  .GetComponent<UnityEngine.UI.Dropdown>();
		debugOut.text = "Click on 'Generate Puzzles' to make puzzles and see what numerical settings are parsed.";
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
		outputString += string.Format("Neighbors = {0}.\n", 
								      neighborDropdown.value);
		outputString += string.Format("Pegs = {0}.\n", pegDropdown.value);
		outputString += string.Format("Shape = {0}.\n", shapeDropdown.value);
		debugOut.text = outputString;

		// string pythonFile = "C:/Users/Spencer/Desktop/Current_QTR_Doc's/CSC 570/Puzzle PCG/peg_solitaire/peg_board.py";
		System.Console.Write("HELLO WORLD!");
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
			}

		}
	}

	/* Creates the text necessary for the Python clyngor library to recognize
	 *   it as ASP and make solutions for the given rules.
	 * Will be using the toggles, dropdowns, and sliders from the GUI.
	 */
	string ASPMaker() {
		string aspLogicRules = string.Format("#const width = {0}.",
		                                     difficultySlider.value + MIN_SIZE);
		aspLogicRules += "dim(1..width).";
		int lostArea = 0;
		int minNeighbors = 4;
		int mid = (int) Mathf.Ceil((difficultySlider.value + MIN_SIZE) / 2);
		if (difficultySlider.value > difficultySlider.maxValue / 2) {
			minNeighbors = 3;
		}
		// If implemented, adaptive difficulty rules would go here;
		//   Idea: Flag each board with a CPU-gen'd difficulty rating

		// Cut the square shape down based on the shape dropdown
		Dictionary<int, string> shape = shapeUI((int) difficultySlider.value + MIN_SIZE);
		// Should retrieve only one key-value pair
		foreach (int key in shape.Keys) {
			lostArea = key;
			aspLogicRules += shape[key];
		}
		// How many pegs are requested?
		aspLogicRules += dropdownUI((int) difficultySlider.value, lostArea, minNeighbors);
		aspLogicRules += string.Format("linked({0},{0}).", mid);
		aspLogicRules += "unlinked(X,Y) :- dim(X), dim(Y), not out(X,Y), not linked(X,Y).";
		aspLogicRules += "linked(X,Y) :- dim(X), dim(Y), neighbor(X, Y, DX, DY), linked(X + DX, Y + DY).";
        aspLogicRules += ":- dim(X), dim(Y), unlinked(X,Y).";
		// aspLogicRules += "#show out/2.";
		// aspLogicRules += "#show peg/2.";

		return aspLogicRules;
	}

    string dropdownUI(int difficulty, int boardSize, int minNeighbors) {
		string rules = "";
		int mid = (int) Mathf.Ceil((difficultySlider.value + MIN_SIZE) / 2);

		// Add the rules for NEIGHBORS
		// Example clyngor Output: tuple ('neighbor', (1, 4, 0, -1))
		switch((int) neighborDropdown.value) {
			case 0:
				rules += minNeighbors;
				rules += " {neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,-1,0); neighbor(X,Y,1,0)}";
				rules += " 4";
				break;
			case 1:
				rules += minNeighbors;
				rules += " {neighbor(X,Y,-1,-1); neighbor(X,Y,-1,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)} ";
				rules += "4";
				break;
			case 2:
				rules += minNeighbors * 2;
				rules += " {neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,-1,0); neighbor(X,Y,1,0);";
				rules += " neighbor(X,Y,-1,-1); neighbor(X,Y,-1,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)} ";
				rules += "8";
				break;
			default:
				rules += "4 {neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,-1,0); neighbor(X,Y,1,0)} 4";
				break;
		}
	    rules += " :- dim(X), dim(Y).";
		// Being a neighbor is established both ways 
		rules += "neighbor(X+DX,Y+DY,DX-DX-DX,DY-DY-DY) :- neighbor(X,Y,DX,DY)";
		rules += ", linked(X+DX,Y+DY).";

		// Add the rules for # OF PEGS
		// Example: 10 { peg(A,B) : linked(A,B), (A,B) != (<mid>, <mid>) } 15.
		//    For every linked point, place between 10 and 15 pegs, inclusive,
		//    where no peg sits in point (<mid>, <mid>)
		// Example clyngor output: tuple ('peg', (1,4))
		switch((int) pegDropdown.value) {
			case 0:
				rules += string.Format("{0} {{ peg(A,B) : ", boardSize - 1);
				rules += "dim(A), dim(B), not out(A,B),";
				rules += string.Format(" (A,B) != ({0},{0}) }} {1}.",
				                       mid, boardSize - 1);
				break;
			// Put rules for all pegs to be filled except one
			case 1:
			    int numPegs = (int) ((boardSize - 1) * 0.1 * (difficulty + 1));
				rules += numPegs + " {{ peg(A,B) : dim(A), dim(B), not out(A, B),";
				rules += string.Format(" (A,B) != ({0},{0}) }} {1}.", mid, numPegs + PEG_RANGE);
				break;
			default:
				rules += string.Format("{0} {{ peg(A,B) : ", boardSize - 1);
				rules += "dim(A), dim(B), not out(A,B),";
				rules += string.Format(" (A,B) != ({0},{0}) }} {1}.",
				                       mid, boardSize - 1);
				break;
		}
		return rules;
	}

	Dictionary<int, string> shapeUI(int width) {
		string rules = "";
		Dictionary<int, string> returnVal = new Dictionary<int, string>();
		int area = width * width;
		switch((int) shapeDropdown.value) {
			// Square shape, don't take away anything
			case 0:
				break;

			// Random shape, take away random rows or squares
			// Req: 3+ width or length for rows or columns respectively
			case 1:
				// Get random values for the size of sections that will be "out"
				int rnd_x, rnd_y, rnd_x_end, rnd_y_end;
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
			    rules += string.Format("xrange(1..{0}; {1}..{2}).",
									   rnd_x, width - rnd_x_end + 1, width);
			    rules += string.Format("yrange(1..{0}; {1}..{2}).",
									   rnd_y, width - rnd_y_end + 1, width);
				rules += "out(X,Y) :- xrange(X), yrange(Y).";
				area -= (rnd_x * rnd_y) + (rnd_x_end * rnd_y_end) + (rnd_x * rnd_y_end) + (rnd_y * rnd_x_end);
				break;

			// Rectangle shape, take away rows at a time
			// Req: 3+ width or length for rows or columns respectively
			case 2:
				// Randomize which sides (horiz, vert) get deleted
				if (UnityEngine.Random.value < 0.5)
					rules += string.Format("out(X,Y) :- dim(X), Y = (1; {0}).",
										   width);
				else
					rules += string.Format("out(X,Y) :- dim(Y), X = (1; {0}).",
						    			   width);
				area -= 2 * width;
				break;

			// Cross shape, take away squares of the grid
			case 3:
				int rnd = (int) (UnityEngine.Random.value * (width / 2)) + 1;
				int rnd_end = (int) (UnityEngine.Random.value * (width - rnd - MIN_WIDTH));
			    rules += string.Format("range(1..{0}; {1}..{2}).", rnd, width - rnd_end, width);
				rules += "out(X,Y) :- range(X), range(Y).";
				area -= (rnd * rnd) + 2 * (rnd * (rnd_end + 1)) + ((rnd_end + 1) * (rnd_end + 1));
				break;
			
			default:
				break;
		}
		returnVal.Add(area, rules);
		return returnVal;
	}

	string pegBoardSolver() {
		/*
		Copy the Rogo puzzle solver idea by having a set of "moves" where
		the set is filled by "hop" atoms that specify two pairs of coord's, the
		hopping peg and the hopped peg.

		Some problems: How do we dynamically know what spaces have pegs or not?
		State held by: board[i,j,t], where coordinates (i,j) hold a 0/1 value
			at time t and tell whether a peg exists there or not.
		Move Prereq: Two consecutive pegs and one gap all in a row
		Move Effect: One peg and two gaps all in a row
		Win Condition: No moves available and One peg left
		Lose Condition: No moves available and more than one peg left
		Number of moves till solution: n_pegs - 1
		 */
		return "";
	}
}
