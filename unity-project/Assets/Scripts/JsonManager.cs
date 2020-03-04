using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using UnityEngine;

public class JsonManager
{
    public static void SaveObjectToJsonFile<T>(string fileName, T obj)
    {
        SaveStringToJsonFile(fileName, ObjectToJsonString<T>(obj));
    }

    /**
     * fileName must be the full path with filename but with no extension
     * */
    private static void SaveStringToJsonFile(string fileName, string jsonString)
    {
        StreamWriter writer = new StreamWriter(String.Format("{0}.json", fileName));
        writer.WriteLine(jsonString);
        writer.Close();
    }

    public static string ObjectToJsonString<T>(T obj)
    {
        JsonSerializerSettings settings = new JsonSerializerSettings
        {
            TypeNameHandling = TypeNameHandling.All
        };
        return JsonConvert.SerializeObject(obj, Formatting.Indented, settings);
    }

    private static T JsonStringToObject<T>(string objString)
    {
        JsonSerializerSettings settings = new JsonSerializerSettings
        {
            TypeNameHandling = TypeNameHandling.All
        };
        return JsonConvert.DeserializeObject<T>(objString, settings);
    }

    public static T ReadObject<T>(string fileName)
    {
        string jsonString = ReadJsonFileToString(fileName);
        return JsonStringToObject<T>(jsonString);
    }

    private static string ReadJsonFileToString(string fileName)
    {
        StreamReader reader = new StreamReader(String.Format("{0}.json", fileName)); 
        string contents = reader.ReadToEnd();
        reader.Close();
        return contents;
    }
}
