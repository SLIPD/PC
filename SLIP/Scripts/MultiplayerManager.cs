using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class MultiplayerManager : MonoBehaviour 
{
	public static MultiplayerManager instance;
	
	public string playerName = "";
	
	private string matchName = "";
	private string matchPassword = "";
	private int matchMaxPlayers = 4;
	
	public List<MPPlayer> playersList = new List<MPPlayer>();
	public List<MapSettings> mapList = new List<MapSettings>();
	
	public MapSettings currentMap = null;
	public int oldPrefix;
	public bool isMatchStarted = false;

	
	void Start()
	{
		instance = this;
		playerName = PlayerPrefs.GetString("Player Name");
		currentMap = mapList[0];
	}
	
	void FixedUpdate()
	{
		instance = this;
	}
	
	public void StartServer(string serverName, string serverPassword, int maxPlayers)
	{
		matchName = serverName;
		matchPassword = serverPassword;
		matchMaxPlayers = maxPlayers;
		Network.InitializeServer(4, 2222, false);
		MasterServer.RegisterHost("SLIP MATCH", matchName, "");
		//Network.InitializeSecurity();
	}
	
	void OnServerInitialized()
	{
		ServerPlayerJoinRequest(playerName, Network.player);
	}
	
	void OnConnectedToServer()
	{
		networkView.RPC("ServerPlayerJoinRequest", RPCMode.Server, playerName, Network.player);
	}
	
	void OnPlayerConnected(NetworkPlayer player)
	{
		foreach( MPPlayer p in playersList)
		{
			networkView.RPC("ClientAddPlayerToList", player, p.teamName, p.playerNetwork);
		}		
		networkView.RPC("ClientGetMultiplayerSettings", player, currentMap.mapName, "", "");
    }	
	
	void OnPlayerDisconnected(NetworkPlayer id)
	{
		networkView.RPC("ClientRemovePlayerFromList", RPCMode.All, id);
	}
	
	[RPC]
	void ServerPlayerJoinRequest(string playerName, NetworkPlayer view)
	{
		networkView.RPC("ClientAddPlayerToList", RPCMode.All, playerName, view);
	}
	
	[RPC]
	void ClientAddPlayerToList(string playerName, NetworkPlayer view)
	{
		MPPlayer team = new MPPlayer();
		team.teamName = playerName;
		team.playerNetwork = view;
		playersList.Add(team);
	}
	
	[RPC]
	void ClientRemovePlayerFromList(NetworkPlayer view)
	{
		MPPlayer tempPlayer = null;
		
		foreach(MPPlayer player in playersList)
		{
			if(player.playerNetwork == view)
			{
				tempPlayer = player;
			}
		}
		
		if(tempPlayer != null)
		{
			playersList.Remove(tempPlayer);	
		}
	}
	
	[RPC]
	void ClientGetMultiplayerSettings(string map, string mode, string others)
	{
		currentMap = GetMap(map);	
	}
	
	public MapSettings GetMap(string name)
	{
		MapSettings get = null;	
		foreach(MapSettings mapSet in mapList)
		{
			if(mapSet.mapName == name)
			{
				get = mapSet;
				break;
			}
		}			
		return get;
	}
	
	[RPC] 
	void ClientLoadMultiplayerMap(string map, int prefix)
	{
		Network.SetLevelPrefix(prefix);
		Application.LoadLevel(map);
	}
	
}

[System.Serializable]
public class MPPlayer
{
	public string teamName;
	public NetworkPlayer playerNetwork;
}

[System.Serializable]
public class MapSettings
{
	public string mapName;
	public string mapLoadName;
	public Texture mapTexture;
}