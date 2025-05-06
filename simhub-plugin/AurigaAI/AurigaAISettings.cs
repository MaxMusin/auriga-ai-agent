using System;
using System.IO;
using System.Xml.Serialization;

namespace AurigaAI
{
    [Serializable]
    public class AurigaAISettings
    {
        // URL de l'API Auriga AI
        public string ApiUrl { get; set; } = "http://localhost:8080";
        
        // Notes du pilote (commentaires généraux sur le setup)
        public string DriverNotes { get; set; } = "";
        
        // Évaluations subjectives du pilote
        public int CarStability { get; set; } = 5;
        public int CornerEntryStability { get; set; } = 5;
        public int CornerExitStability { get; set; } = 5;
        public int Traction { get; set; } = 5;
        public int BrakingStability { get; set; } = 5;
        
        // Chemin du fichier de configuration
        private static readonly string SettingsFilePath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "SimHub",
            "Plugins",
            "AurigaAI",
            "Settings.xml"
        );
        
        /// <summary>
        /// Charge les paramètres depuis le fichier
        /// </summary>
        public void Load()
        {
            try
            {
                // Vérifie si le répertoire existe, sinon le crée
                var directory = Path.GetDirectoryName(SettingsFilePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                
                // Vérifie si le fichier existe
                if (File.Exists(SettingsFilePath))
                {
                    using (var stream = new FileStream(SettingsFilePath, FileMode.Open))
                    {
                        var serializer = new XmlSerializer(typeof(AurigaAISettings));
                        var settings = (AurigaAISettings)serializer.Deserialize(stream);
                        
                        // Copie les paramètres
                        this.ApiUrl = settings.ApiUrl;
                        this.DriverNotes = settings.DriverNotes;
                        this.CarStability = settings.CarStability;
                        this.CornerEntryStability = settings.CornerEntryStability;
                        this.CornerExitStability = settings.CornerExitStability;
                        this.Traction = settings.Traction;
                        this.BrakingStability = settings.BrakingStability;
                    }
                }
            }
            catch (Exception)
            {
                // En cas d'erreur, utilise les valeurs par défaut
            }
        }
        
        /// <summary>
        /// Sauvegarde les paramètres dans le fichier
        /// </summary>
        public void Save()
        {
            try
            {
                // Vérifie si le répertoire existe, sinon le crée
                var directory = Path.GetDirectoryName(SettingsFilePath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }
                
                // Sauvegarde les paramètres
                using (var stream = new FileStream(SettingsFilePath, FileMode.Create))
                {
                    var serializer = new XmlSerializer(typeof(AurigaAISettings));
                    serializer.Serialize(stream, this);
                }
            }
            catch (Exception)
            {
                // Ignore les erreurs de sauvegarde
            }
        }
    }
}
