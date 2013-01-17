using UnityEngine;
using System.Collections;

public class MainMenuGUI : MonoBehaviour {
	
	public MainMenuGUI instance;
	
	public string currentMenu;
	public string matchName;
	public string matchPassword;
	public int maxPlayers = 2;	
	
	private Vector2 scrollLobby = Vector2.zero;
	
	// Use this for initialization
	void Start ()
	{	
		instance = this;
		currentMenu = "MainMenu";
		matchName = "Welcome" + Random.Range(0,5000);
	}
	
	void FixedUpdate()
	{
		instance = this;
	}
	
	// Unity standard GUI method
	void OnGUI()
	{		
		if(currentMenu == "MainMenu"){
			mainMenu();	
		}
		
		if(currentMenu == "LobbyMenu"){
			lobbyMenu();
		}
		
		if(currentMenu == "HostMenu"){
			hostMenu();
		}		
		if(currentMenu == "ChooseMap"){
			chooseMenu();
		}	
	}
	
	// Set new goal menu
	public void navigateTo(string nextMenu)
	{
		currentMenu = nextMenu;
	}
	
	// Main menu
	private void mainMenu()
	{	
		if(GUI.Button(new Rect(10,10,200,50), "Host Game"))
		{
			navigateTo("HostMenu");
		}
		
		if(GUI.Button(new Rect(10,70,200,50), "Refresh"))
		{
			MasterServer.RequestHostList("SLIP MATCH");
		}
		
		GUI.Label(new Rect(220, 10, 130, 30), "Player Name");
		MultiplayerManager.instance.playerName = GUI.TextField(new Rect(350, 10, 150, 30), MultiplayerManager.instance.playerName);	
		
		if(GUI.Button(new Rect(510,10,100,30), "Save Name"))
		{
			PlayerPrefs.SetString("Player Name", MultiplayerManager.instance.playerName);
		}	
		
		GUILayout.BeginArea(new Rect(Screen.width - 400, 0, 400, Screen.height), "SERVER LIST", "BOX");
		
		foreach(HostData match in MasterServer.PollHostList())
		{
			GUILayout.BeginHorizontal("BOX");			
			GUILayout.Label(match.gameName);
			
			if(GUILayout.Button("Connect"))
			{
				Network.Connect(match);
			}
			
			GUILayout.EndHorizontal();
		}
		
		GUILayout.EndArea();
	}
	
	// Host menu
	private void hostMenu()
	{
		
		// Create buttons
		if(GUI.Button(new Rect(10,10,200,50), "Back to Main Menu"))
		{
			navigateTo("MainMenu");
		}
		
		if(GUI.Button(new Rect(10,60,200,50), "Start Server"))
		{
			MultiplayerManager.instance.StartServer(matchName, matchPassword, maxPlayers);
		}
				
		if(GUI.Button(new Rect(10,160,200,50), "Choose Map"))
		{
			navigateTo("ChooseMap");
		}
		
		// Set textfields
		GUI.Label(new Rect(220, 10, 130, 30), "Match Name");
		matchName = GUI.TextField(new Rect(400, 10, 200, 30), matchName);		
		
		GUI.Label(new Rect(220, 50, 130, 30), "Match Password");
		matchPassword = GUI.PasswordField(new Rect(400, 50, 200, 30), matchPassword, '*');
		
		GUI.Label(new Rect(220, 90, 130, 30), "Match Max Players");
		GUI.Label(new Rect(400, 90, 200, 30), maxPlayers.ToString());
		maxPlayers = Mathf.Clamp(maxPlayers, 2, 4);
		
		if(GUI.Button(new Rect(425,90,25,30), "+"))
		{
			maxPlayers+=1;
		}
		
		if(GUI.Button(new Rect(450,90,25,30), "-"))
		{
			maxPlayers-=1;
		}
		
		GUI.Label(new Rect(650, 10, 130, 30), MultiplayerManager.instance.currentMap.mapName);	
		
	}
	
	// Lobby menu
	private void lobbyMenu()
	{
		scrollLobby = GUILayout.BeginScrollView(scrollLobby, GUILayout.MaxWidth(200));
		
		foreach(MPPlayer player in MultiplayerManager.instance.playersList)
		{
			GUILayout.Box(player.teamName);
		}
		
		GUILayout.EndScrollView();
		GUI.Box(new Rect(250, 10, 200, 40), MultiplayerManager.instance.currentMap.mapName);
		
		if(Network.isServer)
		{
			if (GUI.Button(new Rect(Screen.width-200, Screen.height - 80, 200, 40), "Start MATCH"))
			{
				MultiplayerManager.instance.networkView.RPC("ClientLoadMultiplayerMap", RPCMode.All, MultiplayerManager.instance.currentMap.mapLoadName, MultiplayerManager.instance.oldPrefix + 1);	
				MultiplayerManager.instance.oldPrefix +=1;
				MultiplayerManager.instance.isMatchStarted = true;
			}
		}
	
		if (GUI.Button(new Rect(Screen.width-200, Screen.height - 40, 200, 40), "Disconnect"))
		{
			Network.Disconnect();
		}
	}
	
	private void chooseMenu()
	{
		if(GUI.Button(new Rect(10,10,200,50), "Back"))
		{
			navigateTo("HostMenu");
		}
		
		GUI.Label(new Rect(220, 10, 130, 30), "Choose Map");
		GUILayout.BeginArea(new Rect(350, 10, 150, Screen.height));
		
		foreach(MapSettings setting in MultiplayerManager.instance.mapList)
		{
			if(GUILayout.Button(setting.mapName))
			{
				navigateTo("HostMenu");
				MultiplayerManager.instance.currentMap = setting;
			}
		}
		
		GUILayout.EndArea();
	}
	
	void OnServerInitialized()
	{
		navigateTo("LobbyMenu");
	}
	
	void OnConnectedToServer()
	{
		navigateTo("LobbyMenu");
	}
	
	void OnDisconnectedFromServer(NetworkDisconnection info)
	{
		navigateTo("MainMenu");
	}
}
