using UnityEngine;
using System.Collections;

public class generateTerrain : MonoBehaviour {
	
	public Terrain terr;
	float[,] heightMapBackup;
	bool init = true;
	public float[,] initHeightMap;
	static public generateTerrain instance;
	public int Tw;
	public int Th;
	
	void Start () {
		terr = (Terrain) GetComponent(typeof(Terrain));
		terr.name = "Terrain";
		Tw = terr.terrainData.heightmapWidth;
		Th = terr.terrainData.heightmapHeight;
		heightMapBackup = terr.terrainData.GetHeights(0, 0, Tw, Th);
		initHeightMap = terr.terrainData.GetHeights(0, 0, Tw, Th);
		
		for (int i=0; i<Tw; i++)
		{
			for (int j=0; j<Th; j++)
			{
				initHeightMap[i,j] = 0;//desiredHeight;//desiredHeight;
			}
		}
		
		Debug.Log("START TERRAIN");
		terr.terrainData.SetHeights(0,0,initHeightMap);
		
		Debug.Log(terr.detailObjectDistance.ToString());
		Terrain.activeTerrain.detailObjectDistance = 10000;
		Terrain.activeTerrain.basemapDistance = 1000;
		//terr.detailObjectDistance = 1000;
		instance = this;
		//generateTerrain.instance.UpdateTerrainHeight(0, 0, 8.0f);
		//generateTerrain.instance.UpdateTerrainHeight(128, 128, 8.0f);
		
	}
	
	void OnApplicationQuit ()
    {
        terr.terrainData.SetHeights(0, 0, heightMapBackup);
    }
	
	public void UpdateTerrainHeight(int i, int j, float h) {
	
		initHeightMap[i,j] = 0.0004f * h;//desiredHeight;//desiredHeight;
		terr.terrainData.SetHeights(0,0,initHeightMap);
		
	}
	
	// Update is called once per frame
	public void UpdateTest() {
		
		int Tw = terr.terrainData.heightmapWidth-1;
		int Th = terr.terrainData.heightmapHeight-1;
		
		//Debug.Log(Tw + " , " + Th);
		
		float[,] heightMapData = new float[Tw, Th];
		float[,] heightMap = terr.terrainData.GetHeights(0, 0, Tw, Th);

		float desiredHeight = 1.0f;
		//Debug.Log(heightMap.Length);
				
		// we set each sample of the terrain in the size to the desired height
		init = true;
		
		
		if(init){
			for (int i=0; i<Tw; i++)
			{
				for (int j=0; j<Th; j++)
				{
					if(i > 60 && i < 64 && j> 60 && j < 64){
						if(desiredHeight > 0.005f)
						{
							desiredHeight = 0.0f;
						}
						//Debug.Log("DKJIUJDNL");
						heightMap[i,j] = 0.002f;//desiredHeight;//desiredHeight;
						desiredHeight += 0.002f;//desiredHeight + 1.0f;
					}
				}
			}
			terr.terrainData.SetHeights(0,0,heightMap);

			init = false;
		}
		
		// go raising the terrain slowly
		desiredHeight += Time.deltaTime;
		
		// set the new height
		//terr.terrainData.SetHeights(1,1,heightMap);
	}
}
