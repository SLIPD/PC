// This is the client DLL class code to use for the sockServer
// include this DLL in your Plugins folder under Assets
// using it is very simple
// Look at LinkSyncSCR.cs
 
using UnityEngine;
using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Net;
 
public class TeamData
{
	public List<int> grids = new List<int>();
	public string name;
}

public class TerritoriesData
{
	public Tuple gridCell = new Tuple();
	public string name;
}

public class PlayerData
{
	public double x;
	public double y;
	public string name;
}
	
public class HeightMapPoint
{
	public int x;
	public int y;
	public float z;
}
		

public class NetworkUDP : MonoBehaviour
{	
	const int READ_BUFFER_SIZE = 255;
	const int PORT_NUM = 10000;
	private TcpClient client;
	private byte[] readBuffer = new byte[READ_BUFFER_SIZE];
	public ArrayList lstUsers=new ArrayList();
	public string strMessage=string.Empty;
	public string res=String.Empty;
	private string pUserName;
	
	//public List<Tuple> teamTerritoryCoordinates = new List<Tuple>();
	//public List<string> teamNames = new List<string>();
	const char doubleQuote = '\"';
	
	public List<TerritoriesData> tData = new List<TerritoriesData>();
	public List<PlayerData> playerlist = new List<PlayerData>();
	public List<GameObject> gridCells = new List<GameObject>();
	public List<HeightMapPoint> points = new List<HeightMapPoint>();
	public List<int> team1Cell = new List<int>();
	public List<int> team2Cell = new List<int>();
	public List<string> namesOfAllPlayers = new List<string>();
	public string[] teams = new string[2] {"none", "none"};
	
	public bool receivedMSG = false;

	//public NetworkUDP(){}

	static public NetworkUDP instance;

	public string fnConnectResult(string sNetIP, int iPORT_NUM,string sUserName)
	{
		try 
		{		
			// GET LOCAL IP ADDRESS
			/*
			string strHostName = "";
			strHostName = System.Net.Dns.GetHostName();				
			IPHostEntry ipEntry = System.Net.Dns.GetHostEntry(strHostName);				
			IPAddress[] addr = ipEntry.AddressList;
			Debug.Log( addr[addr.Length-1].ToString() );
			sNetIP = addr[addr.Length-1].ToString();
			*/
			sNetIP = "localhost";
			// SET UP NEW TCP CLIENT AND CONNECT
			client = new TcpClient(sNetIP, PORT_NUM);
			client.GetStream().BeginRead(readBuffer, 0, READ_BUFFER_SIZE, new AsyncCallback(DoRead), null);
			Debug.Log("Connection Succeeded");
			//SendData("test");
			return "Connection Succeeded";
		} 
		catch(Exception ex)
		{
			return "Server is not active.  Please start server and try again.      " + ex.ToString();
		}
	}
	
	// SEND PLAYER PATH, USING JSON FORMAT
	public void sendPlayerPath(List<Tuple> playerPath, string playerName)
	{		
		string pathMsg = "{" + '"' + playerName + '"' +  ": ["; // playerName
		bool isFirts = true;
		foreach(Tuple t in playerPath)
		{
			if(!isFirts)
			{
				pathMsg+= ",";
			}
			pathMsg += "[";
			pathMsg += t.first.ToString() + ",";
			pathMsg += t.second.ToString() + "]";
			isFirts = false;
		}
		pathMsg += "]}\0";
		SendData(pathMsg);
	}
	
	private bool hasCommands(){
		//scan for command
		foreach(char c in strMessage){
			if(c == '\n' || c == '\r' || c == '}'){
					return true;
			}
		}
		return false;
	}
	
	private String getNextCommand(){
		StringBuilder b = new StringBuilder("");
		int counter = 0;
		foreach(char c in strMessage){
			if(c == '\n' || c == '\r' || c == '}'){
					b.Append(c);
					counter++;
					break;
			}
			b.Append(c);
			counter++;
		}
		strMessage = strMessage.Substring(counter);
		return b.ToString();
	}
	
	private string isCorrectOrder(string input)
	{
		if(input[2] == 's')
		{
			return input;	
		}
		else
		{
			if(input[2] == 'u')
			{	
				int l = input.Length-28;
				input = input.Substring(1,l);
				input = "{\"state\":\"position_update\"," + input + "}"; 
				//Debug.Log(input);
				return input;
			}
			else if(input[2] == 't')
			{
				int l = input.Length-24;
				input = input.Substring(1,l);
				input = "{\"state\":\"territories\"," + input + "}"; 
				//Debug.Log(input);
				return input;
			}
			else
			{
				input = "";
				return input;
			}	
		}
	}

	private void DoRead(IAsyncResult ar)
	{ 
		int BytesRead;
		try
		{
			BytesRead = client.GetStream().EndRead(ar);
			if (BytesRead < 1) 
			{
				res="Disconnected";
				return;
			}

			strMessage += Encoding.ASCII.GetString(readBuffer, 0, BytesRead );//- 2);
			while(hasCommands()){
				
				if(!receivedMSG){
					string comm = getNextCommand();
					//Debug.Log(comm);
					comm = isCorrectOrder(comm);	
					ProcessCommands(comm);
				}
			}
			client.GetStream().BeginRead(readBuffer, 0, READ_BUFFER_SIZE, new AsyncCallback(DoRead), null);

		} 
		catch
		{
			res="Disconnected";
		}
	}

	// Process the command received from the server, and take appropriate action.
	private void ProcessCommands(string strMessage)
	{
		int charCounter = 0;
		int charIndex0 = 0;
		int charIndex1 = 0;
		
		//Debug.Log(strMessage);
		
		// GET MESSAGE TYPE
		strMessage.Replace(" ", null);
		
		foreach(char c in strMessage)
		{
			if(c == ':')
			{
				charIndex0 = charCounter;
				break;
			}
			charCounter++;
		}
		
		charCounter = 0;
		
		foreach(char c in strMessage)
		{
			if(c == ',')
			{
				charIndex1 = charCounter;
				break;
			}
			charCounter++;
		}
		
		int lengthOfMsg = strMessage.Length - 2 - charIndex1;
		string subMsg = strMessage.Substring(1+charIndex0, charIndex1-charIndex0-1);
		string msgData = strMessage.Substring(1+charIndex1, lengthOfMsg);
		Debug.Log(msgData);
		Debug.Log(subMsg);
		
			switch( subMsg )
			{
				case "\"territories\"":
					Debug.Log("territories");
					receivedMSG = true;
					processTerritoryMsg(msgData);
					break;
				case "\"steps\"":
					Debug.Log("steps");
					//receivedMSG = true;
					break;
				case "\"mesh_update\"":
					processHeightMapPoint(msgData);
					receivedMSG = true;
					Debug.Log("mesh_update");
					break;
				case "\"position_update\"":
					Debug.Log("position_update");
					receivedMSG = true;
					movePlayer(msgData);
					break;
			}
	}
	
	
	// Use a StreamWriter to send a message to server.
	private void SendData(string data)
	{
		StreamWriter writer = new StreamWriter(client.GetStream());
		writer.Write(data);// + (char) 13);
		writer.Flush();
	}
	
	private void getData()
	{
		SendData("");
	}

	void Start () 
	{
		Debug.Log("START NETWORKING");
		instance = this;
		Debug.Log( fnConnectResult("", 100000, "") );
		int ht = Convert.ToInt32(createBoard.instance.gridHeight);
		int wt = Convert.ToInt32(createBoard.instance.gridWidth);
		
		Debug.Log(ht + "," + wt);
		
		for(int i = 0; i < ht; i++)
		{
			for(int j = 0; j < wt; j++)
			{
				string celln = "cell_" + i.ToString() + "_" + j.ToString();
				GameObject t = GameObject.Find(celln);
				gridCells.Add(t);
			}			
		}
		//gridCells[11].gameObject.renderer.material.color = Color.black;
	}
	
	
	void processTerritoryMsg(string msgData)
	{
		
		// TODO: ONLY VALID cell numbers accepted
		TerritoriesData td = new TerritoriesData();
		int charCounter = 0;
		int charIndex0 = 0;
		
		// GET MESSAGE TYPE
		strMessage.Replace(" ", null);
		
		foreach(char c in msgData)
		{
			if(c == ':')
			{
				charIndex0 = charCounter;
				break;
			}
			charCounter++;
		}
		
		string data = msgData.Substring(3+charIndex0, msgData.Length-charIndex0-4);
		int bracketCount = 0;
		string number = "";
		string teamName = "";
		bool lastWasNumber = false;
		bool lastWasLetter = false;
		
		Tuple coordinate = new Tuple();
		Debug.Log(data);
		
		foreach(char m in data)
		{
			if(m == '[')
			{
				bracketCount++;
			}
			
			if(m == ']')
			{
				if(lastWasNumber)
				{
					coordinate.second = Int32.Parse(number);
					//Debug.Log(coordinate.second.ToString());
					int ind = coordinate.second + coordinate.first;//; * createBoard.instance.gridWidth;
					//Debug.Log(ind.ToString());
					td.gridCell.first = coordinate.first;
					//teamTerritoryCoordinates.Add(coordinate);
					coordinate = new Tuple();
					number = "";
					lastWasNumber = false;
				}
				bracketCount--;	
			}
			
			if(m == doubleQuote && lastWasLetter)
			{
				td.name = teamName;
				tData.Add(td);
				td = new TerritoriesData();
				lastWasLetter = false;
				teamName = "";
			}
			
			if(m ==',')
			{
				if(lastWasNumber)
				{
					coordinate.first = Int32.Parse(number);	
					number = "";
					lastWasNumber = false;
				}
			}
			if( Char.IsNumber(m) && !lastWasLetter)
			{
				number+= m;
				lastWasNumber = true;
			}
			if( Char.IsLetter(m) )
			{
				teamName+= m;
				lastWasLetter = true;
			}
			
			//Debug.Log(m.ToString());
		}
		//UpdateSync();
		
		
		//teamTerritoryCoordinates.Clear();
		//teamNames.Clear();
		//Debug.Log(data);
		
	}

	// MOVE PLAYER TO CURRENT POSITION
	void movePlayer(string msgData)
	{
		int charCounter = 0;
		int charIndex0 = 0;
		
		// GET MESSAGE TYPE
		msgData.Replace(" ", null);
		
		foreach(char c in msgData)
		{
			if(c == ':')
			{
				charIndex0 = charCounter;
				break;
			}
			charCounter++;
		}
		
		string data = msgData.Substring(3+charIndex0, msgData.Length-charIndex0-4);
		//Debug.Log(data);
		
		string number = "";
		string playerName = "";
		bool lastWasNumber = false;
		bool lastWasLetter = false;		
		PlayerData pData = new PlayerData();
		
		foreach(char m in data)
		{	
			if(m == ']')
			{
				if(lastWasNumber)
				{
					pData.y = Double.Parse(number);
					//GenerateTeams.instance.changePlayerPosition( (float)pData.x, (float)pData.y, pData.name);
					Debug.Log(pData.x.ToString());
					Debug.Log(pData.y.ToString());
					Debug.Log(pData.name);
					playerlist.Add(pData);
					pData = new PlayerData();
					number = "";
					lastWasNumber = false;
				}
			}
			
			if(m == doubleQuote && lastWasLetter)
			{
				lastWasLetter = false;
				pData.name = playerName;
				playerName = "";
			}
			
			if(m ==',')
			{
				if(lastWasNumber)
				{
					pData.x = Double.Parse(number);
					number = "";
					lastWasNumber = false;
				}
			}
			if( (Char.IsNumber(m) || m == '.' )&& !lastWasLetter)
			{
				number += m;
				lastWasNumber = true;
			}
			if(Char.IsNumber(m) && lastWasLetter)
			{
				playerName+=m;
			}
			if( Char.IsLetter(m) || m == '_')
			{
				lastWasLetter = true;
				playerName += m;
			}
			
			//Debug.Log(m.ToString());
		}
		//UpdateSync();
	}
	
	void updateTerrain(int x, int y, float z)
	{	
		//Debug.Log(x.ToString());
		//Debug.Log(y.ToString());
		int newX = Convert.ToInt32((Convert.ToDouble(x) / Convert.ToDouble(createBoard.instance.gridWidth)) * Convert.ToDouble(generateTerrain.instance.Tw));
		int newY = Convert.ToInt32((Convert.ToDouble(y) / Convert.ToDouble(createBoard.instance.gridHeight)) * Convert.ToDouble(generateTerrain.instance.Th));
		//Debug.Log(newX.ToString());
		//Debug.Log(newY.ToString());
		generateTerrain.instance.UpdateTerrainHeight(newX, newY, z);
		
	}
	
	void processHeightMapPoint(string msgData)
	{
		int charCounter = 0;
		int charIndex0 = 0;
		
		// GET MESSAGE TYPE
		strMessage.Replace(" ", null);
		
		foreach(char c in msgData)
		{
			if(c == ':')
			{
				charIndex0 = charCounter;
				break;
			}
			charCounter++;
		}
		
		string data = msgData.Substring(3+charIndex0, msgData.Length-charIndex0-4);
		Debug.Log(data);

		string number = "";
		HeightMapPoint point = new HeightMapPoint();
		int numC = 0;
		bool lastWasNumber = false;
		
		foreach(char m in data)
		{
			if( Char.IsNumber(m) || m == '.' )
			{
				number += m;
				lastWasNumber = true;
			}
			else
			{
				if(numC == 0 && lastWasNumber)
				{
					point.x = (Convert.ToInt32(number));
					Debug.Log(number);
					numC++;
					number = "";
					lastWasNumber = false;
				}
				else if(numC == 1 && lastWasNumber)
				{
					point.y = (Convert.ToInt32(number));
					numC++;
					number = "";
					lastWasNumber = false;
				}
				else if(lastWasNumber && numC == 2)
				{
					point.z = (float) (Convert.ToDouble(number));
					points.Add(point);
					
					Debug.Log(point.x.ToString());
					Debug.Log(point.y.ToString());
					Debug.Log(point.z.ToString());

					point = new HeightMapPoint();
					numC = 0;
					number = "";
					lastWasNumber = false;
				}

			}
			
		}
		//UpdateSync();
		
	}
	
	int notGood = 0;
	
	void Update () 
	{
		
		//if(notGood < 100){
		//	SendData("UPDATE");
		//	notGood++;
		//}
		
		if(receivedMSG){

			foreach(TerritoriesData d in tData)
			{
				int idxName = -1;
				
				if(d.name == teams[0]){
					idxName = 0;
				}
				else if(d.name == teams[1]){
					idxName = 1;	
				}
				else{
					if(teams[0] == "none"){
						teams[0] = d.name;
						idxName = 0;
					}
					else if(teams[1] == "none"){
						teams[1] = d.name;
						idxName = 1;
					}
				}
				
				if(idxName == 0)
				{
					int minX = d.gridCell.first * createBoard.instance.gridWidth /3;
					int maxX = d.gridCell.first * createBoard.instance.gridWidth /3 + (createBoard.instance.gridWidth/3);				
					int minY = d.gridCell.second * createBoard.instance.gridHeight /3;
					int maxY = d.gridCell.second * createBoard.instance.gridHeight /3+ (createBoard.instance.gridHeight/3);
					
					if(maxX > createBoard.instance.gridWidth)
					{
						maxX = createBoard.instance.gridWidth;
					}
					if(maxY > createBoard.instance.gridHeight)
					{
						maxY = createBoard.instance.gridHeight;
					}				
					for(int u = minX; u < maxX; u++){
						for(int v = minY; v < maxY; v++){
							string temp = "cell_" + u.ToString() + "_" + v.ToString();
							GameObject.Find(temp).renderer.material.color = Color.green;
						}
					}
					
				}
				else if(idxName == 1)
				{
					int minX = d.gridCell.first * createBoard.instance.gridWidth /3;
					int maxX = d.gridCell.first * createBoard.instance.gridWidth /3 + (createBoard.instance.gridWidth/3);				
					int minY = d.gridCell.second * createBoard.instance.gridHeight /3;
					int maxY = d.gridCell.second * createBoard.instance.gridHeight /3+ (createBoard.instance.gridHeight/3);
					
					if(maxX > createBoard.instance.gridWidth)
					{
						maxX = createBoard.instance.gridWidth;
					}
					if(maxY > createBoard.instance.gridHeight)
					{
						maxY = createBoard.instance.gridHeight;
					}
					for(int u = minX; u < maxX; u++){
						for(int v = minY; v < maxY; v++){
							string temp = "cell_" + u.ToString() + "_" + v.ToString();
							GameObject.Find(temp).renderer.material.color = Color.red;
						}
					}
				}
				else
				{
					Debug.Log("tData error");	
				}
			}
			
			
			
			foreach(PlayerData p in playerlist)
			{
				GenerateTeams.instance.changePlayerPosition( (float)p.x, (float)p.y, p.name);
			}
			
			foreach(HeightMapPoint p in points)
			{
				updateTerrain(p.x, p.y, p.z);
			}
			
			tData.Clear();
			points.Clear();
			playerlist.Clear();
			team1Cell.Clear();
			team2Cell.Clear();
			receivedMSG = false;
		}
	}
	
}
