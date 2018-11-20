using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using UnityEngine.SceneManagement;


public class mainGUI : MonoBehaviour {
	public const int MIN_SIZE = 5;
	public const int PEG_RANGE = 5;
	public UnityEngine.UI.Slider difficultySlider;
	public UnityEngine.UI.Dropdown adapterDropdown;
	public UnityEngine.UI.Dropdown neighborDropdown;
	public UnityEngine.UI.Dropdown pegDropdown;
	public UnityEngine.UI.Toggle randomShape;
	public UnityEngine.UI.Toggle squareShape;
	public UnityEngine.UI.Toggle rectangleShape;
	public UnityEngine.UI.Toggle crossShape;

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
		randomShape = GameObject.Find("RandomToggle")
								.GetComponent<UnityEngine.UI.Toggle>();
		squareShape = GameObject.Find("SquareToggle")
						        .GetComponent<UnityEngine.UI.Toggle>();
		rectangleShape = GameObject.Find("RectangleToggle")
						           .GetComponent<UnityEngine.UI.Toggle>();
		crossShape = GameObject.Find("CrossToggle")
							   .GetComponent<UnityEngine.UI.Toggle>();
		debugOut.text = "Click checkboxes, dropdowns, and sliders for debugging output.";
	}
	
	// Update is called once per frame
	void Update () {
		
	}

	public void GenerateButtonClick () {
		ProcessStartInfo start = new ProcessStartInfo("python");
		string aspBoard = ASPMaker();

		// start.FileName = "C:/Users/Spencer/Desktop/Current_QTR_Doc's/CSC 570/Puzzle PCG/peg_solitaire/peg_board.py";
		// start.Arguments = string.Format("{0}", aspBoard);
		// start.UseShellExecute = true;
		// start.RedirectStandardOutput = true;

		// using(Process process = Process.Start(start))
		// {
		// 	using(StreamReader reader = process.StandardOutput)
		// 	{
		// 		string result = reader.ReadToEnd();
		// 		//Console.Write(result);
		// 	}
		// }
		string outputString = "";
        outputString += string.Format("Difficulty Slider = {0}. ",
									  difficultySlider.value);
		outputString += string.Format("Adaptive Dropdown = {0}. ",
		                              adapterDropdown.value);
		outputString += string.Format("Neighbors = {0}. ", 
								      neighborDropdown.value);
		outputString += string.Format("Pegs = {0}. ", pegDropdown.value);
		outputString += string.Format("Shape = {0} {1} {2} {3}.", 
									  randomShape.isOn, squareShape.isOn, 
									  rectangleShape.isOn, crossShape.isOn);
		debugOut.text = outputString;
	}

	/* Creates the text necessary for the Python clyngor library to recognize
	 *   it as ASP and make solutions for the given rules.
	 * Will be using the toggles, dropdowns, and sliders from the GUI.
	 */
	string ASPMaker() {
		string aspLogicRules = string.Format("#const width = {0}.",
		                                     difficultySlider.value + MIN_SIZE);
		aspLogicRules += "dim(1..width).";
		int minNeighbors = 4;
		if (difficultySlider.value > difficultySlider.maxValue / 2) {
			minNeighbors = 3;
		}
		// If implemented, adaptive difficulty rules would go here;
		//   Idea: Flag each board with a CPU-gen'd difficulty rating

		aspLogicRules += dropdownUI((int) difficultySlider.value, minNeighbors);
		// Cut the square shape down based on the shape dropdown
		if (randomShape.isOn) {

		}
		else {
            if (squareShape.isOn) {

			}
			if (rectangleShape.isOn) {

			}
			if (crossShape.isOn) {

			}
		}
		aspLogicRules += string.Format("linked({0},{0}).",
		                               (int) difficultySlider.value + MIN_SIZE);
		aspLogicRules += "linked(X,Y) :- neighbor(X, Y, DX, DY), linked(X + DX, Y + DY), not linked(X,Y).";
        aspLogicRules += ":- dim(X), dim(Y), not linked(X, Y).";

		return aspLogicRules;
	}

    string dropdownUI(int difficulty, int minNeighbors) {
		string rules = "";
		int mid = (int) difficulty + MIN_SIZE;
		int boardSize = ((int) difficulty + MIN_SIZE) *
		                ((int) difficulty + MIN_SIZE);

		// Add the rules for NEIGHBORS
		// Example clyngor Output: tuple ('neighbor', (1, 4, 0, -1))
		switch((int) neighborDropdown.value) {
			case 0:
				rules += minNeighbors;
				rules += "{neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)}";
				rules += "4";
				break;
			case 1:
				rules += minNeighbors;
				rules += "{neighbor(X,Y,-1,-1); neighbor(X,Y,-1,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)}";
				rules += "4";
				break;
			case 2:
				rules += minNeighbors * 2;
				rules += "{neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1);";
				rules += " neighbor(X,Y,-1,-1); neighbor(X,Y,-1,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)}";
				rules += "8";
				break;
			default:
				rules += "4 {neighbor(X,Y,0,-1); neighbor(X,Y,0,1);";
				rules += " neighbor(X,Y,1,-1); neighbor(X,Y,1,1)} 4";
				break;
		}
	    rules += " :- dim(X), dim(Y).";
		// Being a neighbor is established both ways 
		rules += "neighbor(X+DX,Y+DY,DX-DX-DX,DY-DY-DY) :- neighbor(X,Y,DX,DY).";

		// Add the rules for # OF PEGS
		// Example: 10 { peg(A,B) : linked(A,B), (A,B) != (<mid>, <mid>) } 15.
		//    For every linked point, place between 10 and 15 pegs, inclusive,
		//    where no peg sits in point (<mid>, <mid>)
		// Example clyngor output: tuple ('peg', (1,4))
		switch((int) pegDropdown.value) {
			case 0:
				rules += (boardSize - 1) + " { peg(A,B) :";
				rules += string.Format(" linked(A,B), (A,B) != ({0},{0})} {1}.",
				                       mid, boardSize - 1);
				break;
			// Put rules for all pegs to be filled except one
			case 1:
			    int numPegs = (int) ((boardSize - 1) * 0.1 * (difficulty + 1));
				rules += numPegs + " { peg(A,B) : linked(A,B), (A,B) } ";
				rules += string.Format("(A,B) != ({0},{0}) } {1}.",
				                       mid, numPegs + PEG_RANGE);
				break;
			default:
				rules += (boardSize - 1) + " { peg(A,B) :";
				rules += string.Format(" linked(A,B), (A,B) != ({0},{0})} {1}.",
				                       mid, boardSize - 1);
				break;
		}
		return rules;
	}

	string toggleUI() {
		string rules = "";
		return rules;
	}

	List<int> GuiArgsList() {
		List<int> ArgsList = new List<int>();
		// Next, we get settings put in the Unity GUI so we can decide on a designer's criteria for the next set of puzzles
		return ArgsList;
	}
}
