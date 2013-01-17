using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
	
public class GenerateTeams : MonoBehaviour {
	
	public static GenerateTeams instance;

	
	int numberOfTeams = 2;
	int numberofPlayers = 2;
	
	public GameObject Character;

	
	//List<String> players = new List<String>();
	public string[] team1 = new string[2];
	public string[] team2 = new string[2];	
	
	
//	void generateTeams(){
//			
//		GameObject teams = new GameObject("TEAMS");
//		
//		team1[0] = "t1_player1";
//		team1[1] = "t1_player2";
//		team2[0] = "t2_player1";
//		team2[1] = "Kit";
//				
//		for (int y = 0; y < 2; y++)
//        {
//            for (int x = 0; x < 2; x++)
//            {
//				if(y % 2 == 0){
//					
//					float xi = 2.5f *x;
//					float yi = 2.5f *y;
//					float zi = 1.0f;
//
//					Vector3 initPos = new Vector3(xi, zi, yi);
//					
//	                GameObject cell = (GameObject)Instantiate(Character);	           
//	                cell.transform.position = initPos;
//	                cell.transform.parent = teams.transform;
//					cell.gameObject.renderer.material.color = Color.green;
//					cell.gameObject.name = team1[x];
//				}
//				else if(y % 2 != 0){
//					
//					float xi = 2.5f *x;
//					float yi = 2.5f *y;
//					float zi = 1.0f;
//
//					Vector3 initPos = new Vector3(xi, zi, yi);
//					
//	                GameObject cell = (GameObject)Instantiate(Character);	           
//	                cell.transform.position = initPos;
//	                cell.transform.parent = teams.transform;
//					cell.gameObject.renderer.material.color = Color.yellow;
//					cell.gameObject.name = team2[x];
//				}
//            }
//        }
//		
//	}
	
	public List<string> playersNames = new List<string>();
	
	public void createPlayer(float x, float z, string playerName)
	{
		GameObject cell = (GameObject)Instantiate(Character);
		string tName = "cell_" + x.ToString() + "_" + z.ToString();
		//Debug.Log(tName);
		Vector3 newPos = new Vector3(GameObject.Find(tName).transform.position.x, GameObject.Find("cell_0_0").transform.position.y+1.2f, GameObject.Find(tName).transform.position.z);
        cell.transform.position = newPos;
		if(playerName == "BASE"){
			cell.gameObject.renderer.material.color = Color.black;			
		}
		else{
			cell.gameObject.renderer.material.color = Color.magenta;			
		}
		cell.gameObject.name = playerName;
		playersNames.Add(playerName);
	}
	
	public void changePlayerPosition(float x, float z, string playerName)
	{
		
		if(GameObject.Find(playerName))
		{
			string cellN = "cell_" + x.ToString() + "_" + z.ToString();
			Debug.Log(cellN);
			Vector3 newPos = new Vector3(GameObject.Find(cellN).transform.position.x, GameObject.Find(playerName).transform.position.y, GameObject.Find(cellN).transform.position.z);
			GameObject.Find(playerName).transform.position = newPos;						
		}
		else
		{
			createPlayer(x, z, playerName);
		}
		
		
	}
	
	// Use this for initialization
	void Start () {
		//generateTeams();
		instance = this;
	}
	
	// Update is called once per frame
	void Update () {
	
		// SET NEW 
	}
}
