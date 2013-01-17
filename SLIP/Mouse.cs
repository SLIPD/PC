using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Linq;

public class Mouse : MonoBehaviour {
	
	public bool isPlayerSelected = false;
	//public List<MPPlayer> playersList = new List<MPPlayer>();
	//public List<Tuple<int, int>> playerPath = new List<Tuple<int, int>>();
    public List<Tuple> playerPath = new List<Tuple>();

	
	// Use this for initialization
	void Start () {
	
	}
	
	void Update () {
				
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
				hit.collider.gameObject.renderer.material.color = Color.red;

			}
			else{
				Debug.Log("NO HIT");	
			}
			
		}
		
		
		if(Input.GetMouseButtonDown(1)){
			
			float x = 3.3f;
			float z = 5.5f;
			string nameTemp = GenerateTeams.instance.team1[0];
			GenerateTeams.instance.changePlayerPosition(x,z,nameTemp);
		}
		/*
			Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
			RaycastHit hit;
			Color initialColour;

			if(Physics.Raycast(ray, out hit)){
				double i = hit.collider.gameObject.transform.localPosition.x / 2.5;
				double j = hit.collider.gameObject.transform.localPosition.z / 2.5;
				Debug.Log("HIT at (" + i + ", " + j + ")");
				//initialColour = hit.collider.gameObject.renderer.material.color;
				//Debug.Log("This hit at " + hit.point );
				if(!isInList(hit.collider.gameObject.name,GenerateTeams.instance.team1) && !isInList(hit.collider.gameObject.name,GenerateTeams.instance.team2))
				{
					hit.collider.gameObject.renderer.material.color = Color.blue;
				}
				else
				{
					Debug.Log("Selected player: " + hit.collider.gameObject.name + "\n");
				}
			}
			else{
				Debug.Log("NO HIT");	
			}
			
		}	
		
		*/
		//Debug.Log(GenerateTeams.instance.team1[0]);
	}
	
	public void addCoordinateToPlayerPath(double i, double j)
	{
		Tuple coordinate = new Tuple();
		coordinate.first = (int)(i);
		coordinate.second = (int)(j);
		playerPath.Add(coordinate);
		
		foreach(Tuple pos in playerPath)
		{
			Debug.Log( "(" + pos.first + "," + pos.second + ")" );				
		}
		
	}
	
	public bool isInList(string name, string[] list)
	{
		foreach(string nm in list)
		{
			if(nm == name){
				return true;
			}
		}
		return false;
	}
}
