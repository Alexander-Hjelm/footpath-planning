[System.Serializable]
public class PatchData
{
    public int[,] edges {get; set;}
    public float[,] points {get; set;}
    public float stat_avg_len {get; set;}
    public float stat_var_len {get; set;}
    public float stat_avg_curv {get; set;}
    public float stat_var_curv {get; set;}
}
