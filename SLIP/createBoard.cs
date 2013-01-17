using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;



public class Tuple
{
	public int first;
	public int second;
}

public class createBoard: MonoBehaviour
{

	//public Tile selectedCell = null;
	static public createBoard instance;
    public GameObject gridCell;
    public int gridWidth = 25;
    public int gridHeight = 25;

    private float cellWidth;
    private float cellHeight;
	
	public bool isPlayerSelected = false;
	public string currentSelectedPlayer = "";
	//public List<MPPlayer> playersList = new List<MPPlayer>();
	//public List<Tuple<int, int>> playerPath = new List<Tuple<int, int>>();
    public List<Tuple> playerPath = new List<Tuple>();
	public Color initCol = new Color();	
	public Color[] colours;
	public int[] territories;
	public List<Color> pathCols = new List<Color>();
	
	
    void setSizes()
    {
        cellWidth = gridCell.renderer.bounds.size.x;
        cellHeight = gridCell.renderer.bounds.size.z;
    }

    Vector3 calcInitPos()
    {
        Vector3 initPos;
		initPos = new Vector3(0,0,0);
        return initPos;
    }

    public Vector3 calcWorldCoord(Vector2 gridPos)
    {
        Vector3 initPos = calcInitPos();
        float x =  initPos.x + gridPos.x * cellWidth;
        float z = initPos.z + gridPos.y * cellHeight;
        return new Vector3(x, 0, z);
    }

    void createGrid()
    {
        GameObject Grid = new GameObject("Grid");

        for (float y = 0; y < gridHeight; y++)
        {
            for (float x = 0; x < gridWidth; x++)
            {
                GameObject cell = (GameObject)Instantiate(gridCell);
				cell.name = "cell_" + x.ToString() + "_" + y.ToString();
                Vector2 gridPos = new Vector2(x, y);
                cell.transform.position = calcWorldCoord(gridPos);
                cell.transform.parent = Grid.transform;
				initCol = cell.renderer.material.color;
            }
        }
    }
	
	void setColour(List<Tuple> paths, List<Color> cols)
	{
		int counter = 0;
		foreach(Tuple t in paths)
		{
			string tempName = "cell_" + t.first.ToString() + "_" + t.second.ToString();
			if(GameObject.Find(tempName))
			{
				GameObject.Find(tempName).renderer.material.color = cols[counter];
				counter++;
			}
		}
	}
	
	void Update () {
		
		/*
		if (Input.GetKeyDown(KeyCode.C)) {
        	cam1.enabled = !cam1.enabled;
        	cam2.enabled = !cam2.enabled;
    	}
    	*/
				
		// If User clicks on object it turns red
		if(Input.GetMouseButtonDown(0)){
			Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
			RaycastHit hit;
			Color initialColour;

			if(Physics.Raycast(ray, out hit)){
				
				//Debug.Log("HIT: " + hit.collider.gameObject.transform.localPosition);
				double i = hit.collider.gameObject.transform.localPosition.x / 2.5;
				double j = hit.collider.gameObject.transform.localPosition.z / 2.5;
				Debug.Log("HIT at (" + i + ", " + j + ")");
				
				//initialColour = hit.collider.gameObject.renderer.material.color;
				if(!isInList(hit.collider.gameObject.name))
				{
					if(isPlayerSelected)
					{
						if(!alreadyInPath(i,j)){
							pathCols.Add(hit.collider.gameObject.renderer.material.color);
							hit.collider.gameObject.renderer.material.color = Color.blue;
							addCoordinateToPlayerPath(i, j);
							NetworkUDP.instance.sendPlayerPath(playerPath, currentSelectedPlayer);
						}
					}
				}
				else if(isInList(hit.collider.gameObject.name))
				{	
					setColour(playerPath, pathCols);
					playerPath.Clear();
					pathCols.Clear();
					Debug.Log("Selected player: " + hit.collider.gameObject.name + "\n");
					currentSelectedPlayer = hit.collider.gameObject.name;
					isPlayerSelected = true;
				}
			}
			else{
				Debug.Log("NO HIT");	
			}
			
		}
		
	}
	
	public bool alreadyInPath(double i, double j)
	{
		foreach(Tuple s in playerPath){
			if(s.first == (int)i && s.second == (int)j){
				return true;	
			}
		}
		return false;
	}
	
	public void addCoordinateToPlayerPath(double i, double j)
	{
		Tuple coordinate = new Tuple();
		coordinate.first = (int)(i);
		coordinate.second = (int)(j);
		playerPath.Add(coordinate);
		
	}
	
	public bool isInList(string name)
	{
		foreach(string nm in GenerateTeams.instance.playersNames)
		{
			if(nm == name){
				return true;
			}
		}
		return false;
	}
	
    //The grid should be generated on game start
    void Start()
    {
		colours = new Color[4] {Color.red, Color.green, Color.blue, Color.black};
		territories = new int[9] {0,0,0,0,0,0,0,0,0};
		instance = this;
        setSizes();
        createGrid();
    }
}