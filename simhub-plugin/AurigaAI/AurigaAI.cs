using GameReaderCommon;
using SimHub.Plugins;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace AurigaAI
{
    [PluginDescription("Auriga AI - Optimisation de setup iRacing")]
    [PluginAuthor("Maxime Musin")]
    [PluginName("Auriga AI")]
    public class AurigaAIPlugin : IPlugin, IDataPlugin, IWPFSettings
    {
        public PluginManager PluginManager { get; set; }
        private HttpClient httpClient;
        private AurigaAISettings settings;
        private int currentSetupId = -1;
        private string currentCarId = "";
        private string currentTrackId = "";
        private bool isTestingSetup = false;
        private bool hasCompletedLap = false;
        private Dictionary<string, object> telemetryData = new Dictionary<string, object>();
        private Dictionary<string, object> weatherData = new Dictionary<string, object>();

        /// <summary>
        /// Instance of the current plugin manager
        /// </summary>
        public PluginManager PluginManager { get; set; }

        /// <summary>
        /// Gets the left menu icon. Return null if no icon should be displayed
        /// </summary>
        public ImageSource PictureIcon => this.ToIcon(Properties.Resources.icon);

        /// <summary>
        /// Gets a short plugin title to show in left menu. Return null if no text should be displayed
        /// </summary>
        public string LeftMenuTitle => "Auriga AI";

        /// <summary>
        /// Called one time per game data update, contains all normalized game data,
        /// raw data are intentionally "hidden" under a generic object type (A plugin SHOULD NOT USE IT)
        /// </summary>
        /// <param name="data">Current game data, normalized across games</param>
        public void DataUpdate(PluginManager pluginManager, ref GameData data)
        {
            if (data.GameRunning && data.GameName == "IRacing")
            {
                // Si nous sommes en train de tester un setup
                if (isTestingSetup && currentSetupId > 0)
                {
                    // Collecte des données de télémétrie
                    CollectTelemetryData(data);

                    // Vérifie si un tour a été complété
                    if (data.NewData.LastLapTime > 0 && !hasCompletedLap)
                    {
                        hasCompletedLap = true;
                        
                        // Ajoute le temps au tour aux données de télémétrie
                        telemetryData["lap_time"] = data.NewData.LastLapTime;
                        
                        // Envoie les données à l'API
                        SendTelemetryData();
                    }
                }
                else
                {
                    // Vérifie si nous avons changé de voiture ou de circuit
                    if (data.NewData.CarId != currentCarId || data.NewData.TrackId != currentTrackId)
                    {
                        currentCarId = data.NewData.CarId;
                        currentTrackId = data.NewData.TrackId;
                        
                        // Réinitialise l'état
                        ResetState();
                    }
                }
            }
        }

        /// <summary>
        /// Called at plugin manager stop, close/dispose anything needed here
        /// </summary>
        public void End(PluginManager pluginManager)
        {
            // Dispose of HttpClient
            httpClient?.Dispose();
        }

        /// <summary>
        /// Returns the settings control, return null if no settings control is required
        /// </summary>
        public System.Windows.Controls.Control GetWPFSettingsControl(PluginManager pluginManager)
        {
            return new AurigaAISettingsControl(this);
        }

        /// <summary>
        /// Called once after plugins are loaded
        /// </summary>
        public void Init(PluginManager pluginManager)
        {
            // Initialize settings
            settings = new AurigaAISettings();
            settings.Load();
            
            // Initialize HttpClient
            httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(10);
            
            // Add command to start testing a setup
            pluginManager.AddCommand("StartSetupTest", (a, b) =>
            {
                StartSetupTest();
            });
            
            // Add command to stop testing a setup
            pluginManager.AddCommand("StopSetupTest", (a, b) =>
            {
                StopSetupTest();
            });
            
            // Add property to show current setup ID
            pluginManager.AddProperty("CurrentSetupId", this.GetType(), currentSetupId);
            
            // Add property to show if we're testing a setup
            pluginManager.AddProperty("IsTestingSetup", this.GetType(), isTestingSetup);
        }

        private async void StartSetupTest()
        {
            if (string.IsNullOrEmpty(settings.ApiUrl))
            {
                pluginManager.SetMessage("Auriga AI: URL de l'API non configurée");
                return;
            }
            
            try
            {
                // Récupère le prochain setup à tester
                var response = await httpClient.GetAsync($"{settings.ApiUrl}/api/v1/setup/next");
                
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var setupInfo = JsonConvert.DeserializeObject<SetupInfo>(content);
                    
                    currentSetupId = setupInfo.id;
                    isTestingSetup = true;
                    hasCompletedLap = false;
                    telemetryData.Clear();
                    weatherData.Clear();
                    
                    // Met à jour les propriétés
                    pluginManager.SetPropertyValue("CurrentSetupId", this.GetType(), currentSetupId);
                    pluginManager.SetPropertyValue("IsTestingSetup", this.GetType(), isTestingSetup);
                    
                    pluginManager.SetMessage($"Auriga AI: Test du setup #{currentSetupId} démarré");
                }
                else
                {
                    pluginManager.SetMessage($"Auriga AI: Erreur lors de la récupération du setup - {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                pluginManager.SetMessage($"Auriga AI: Erreur - {ex.Message}");
            }
        }

        private void StopSetupTest()
        {
            isTestingSetup = false;
            pluginManager.SetPropertyValue("IsTestingSetup", this.GetType(), isTestingSetup);
            pluginManager.SetMessage("Auriga AI: Test du setup arrêté");
        }

        private void ResetState()
        {
            currentSetupId = -1;
            isTestingSetup = false;
            hasCompletedLap = false;
            telemetryData.Clear();
            weatherData.Clear();
            
            // Met à jour les propriétés
            pluginManager.SetPropertyValue("CurrentSetupId", this.GetType(), currentSetupId);
            pluginManager.SetPropertyValue("IsTestingSetup", this.GetType(), isTestingSetup);
        }

        private void CollectTelemetryData(GameData data)
        {
            // Collecte des données de télémétrie pertinentes
            
            // Températures des pneus
            telemetryData["tire_avg_temp_fl"] = data.NewData.TyreTempFrontLeft;
            telemetryData["tire_avg_temp_fr"] = data.NewData.TyreTempFrontRight;
            telemetryData["tire_avg_temp_rl"] = data.NewData.TyreTempRearLeft;
            telemetryData["tire_avg_temp_rr"] = data.NewData.TyreTempRearRight;
            
            // Usure des pneus (si disponible)
            if (data.NewData.TyreWearFrontLeft.HasValue)
                telemetryData["tire_wear_fl"] = data.NewData.TyreWearFrontLeft.Value;
            if (data.NewData.TyreWearFrontRight.HasValue)
                telemetryData["tire_wear_fr"] = data.NewData.TyreWearFrontRight.Value;
            if (data.NewData.TyreWearRearLeft.HasValue)
                telemetryData["tire_wear_rl"] = data.NewData.TyreWearRearLeft.Value;
            if (data.NewData.TyreWearRearRight.HasValue)
                telemetryData["tire_wear_rr"] = data.NewData.TyreWearRearRight.Value;
            
            // Données météo
            weatherData["track_temp"] = data.NewData.TrackTemperature;
            weatherData["air_temp"] = data.NewData.AirTemperature;
            
            // Note: Les métriques subjectives comme la stabilité devront être saisies manuellement
            // par le pilote via l'interface utilisateur
        }

        private async void SendTelemetryData()
        {
            if (string.IsNullOrEmpty(settings.ApiUrl) || currentSetupId <= 0)
            {
                return;
            }
            
            try
            {
                // Prépare les données à envoyer
                var telemetryPayload = new
                {
                    setup_id = currentSetupId,
                    lap_time = telemetryData["lap_time"],
                    telemetry_data = telemetryData,
                    weather_conditions = weatherData,
                    driver_notes = settings.DriverNotes
                };
                
                // Convertit en JSON
                var json = JsonConvert.SerializeObject(telemetryPayload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                
                // Envoie à l'API
                var response = await httpClient.PostAsync($"{settings.ApiUrl}/api/v1/telemetry", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<TelemetryResponse>(responseContent);
                    
                    pluginManager.SetMessage($"Auriga AI: Données envoyées avec succès - Score: {result.score}");
                    
                    // Réinitialise l'état pour le prochain test
                    ResetState();
                }
                else
                {
                    pluginManager.SetMessage($"Auriga AI: Erreur lors de l'envoi des données - {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                pluginManager.SetMessage($"Auriga AI: Erreur - {ex.Message}");
            }
        }
    }

    public class SetupInfo
    {
        public int id { get; set; }
        public string car_id { get; set; }
        public string track_id { get; set; }
        public object setup_parameters { get; set; }
        public string generation_time { get; set; }
        public string status { get; set; }
        public string source { get; set; }
        public string file_path { get; set; }
    }

    public class TelemetryResponse
    {
        public bool success { get; set; }
        public int telemetry_id { get; set; }
        public double score { get; set; }
        public int? next_setup_id { get; set; }
    }
}
