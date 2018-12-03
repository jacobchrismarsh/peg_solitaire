string[][] readFile(string file){
     string text = System.IO.File.ReadAllText(file);
     string[] lines = Regex.Split(text, "\r\n");
     int rows = lines.Length;
     
     string[][] levelBase = new string[rows][];
     for (int i = 0; i < lines.Length; i++)  {
         string[] stringsOfLine = Regex.Split(lines[i], " ");
         levelBase[i] = stringsOfLine;
     }
     return levelBase;
 }

 public Transform player;
 public Transform floor_valid;
 public Transform floor_obstacle;
 public Transform floor_checkpoint;

 public const string peg = "*";
 public const string out = "█";
 public const string hole = "O";

 void Start() {
     string[][] jagged = readFile("successful_boards_ascii.txt");

     // create planes based on matrix
     for (int y = 0; y < jagged.Length; y++) {
         for (int x = 0; x < jagged[0].Length; x++) {
             switch (jagged[y][x]){
             case peg:
                 Instantiate(floor_valid, new Vector3(x, 0, -y), Quaternion.identity);
                 Instantiate(player, new Vector3(0, 0.5f, 0), Quaternion.identity);
                 break;
             case hole:
                 Instantiate(floor_valid, new Vector3(x, 0, -y), Quaternion.identity);
                 break;
             case out:
                 Instantiate(floor_obstacle, new Vector3(x, 0, -y), Quaternion.identity);
                 break;
             }
         }
     }
 }
