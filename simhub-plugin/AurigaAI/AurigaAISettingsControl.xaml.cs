using System;
using System.Windows;
using System.Windows.Controls;

namespace AurigaAI
{
    /// <summary>
    /// Logique d'interaction pour AurigaAISettingsControl.xaml
    /// </summary>
    public partial class AurigaAISettingsControl : UserControl
    {
        private AurigaAIPlugin plugin;
        private AurigaAISettings settings;

        public AurigaAISettingsControl(AurigaAIPlugin plugin)
        {
            InitializeComponent();
            this.plugin = plugin;
            this.settings = new AurigaAISettings();
            this.settings.Load();
            
            // Initialise les contrôles avec les valeurs des paramètres
            this.ApiUrlTextBox.Text = this.settings.ApiUrl;
            this.DriverNotesTextBox.Text = this.settings.DriverNotes;
            this.CarStabilitySlider.Value = this.settings.CarStability;
            this.CornerEntryStabilitySlider.Value = this.settings.CornerEntryStability;
            this.CornerExitStabilitySlider.Value = this.settings.CornerExitStability;
            this.TractionSlider.Value = this.settings.Traction;
            this.BrakingStabilitySlider.Value = this.settings.BrakingStability;
        }

        private void SaveButton_Click(object sender, RoutedEventArgs e)
        {
            // Sauvegarde les paramètres
            this.settings.ApiUrl = this.ApiUrlTextBox.Text;
            this.settings.DriverNotes = this.DriverNotesTextBox.Text;
            this.settings.CarStability = (int)this.CarStabilitySlider.Value;
            this.settings.CornerEntryStability = (int)this.CornerEntryStabilitySlider.Value;
            this.settings.CornerExitStability = (int)this.CornerExitStabilitySlider.Value;
            this.settings.Traction = (int)this.TractionSlider.Value;
            this.settings.BrakingStability = (int)this.BrakingStabilitySlider.Value;
            
            this.settings.Save();
            
            MessageBox.Show("Paramètres sauvegardés avec succès", "Auriga AI", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void StartTestButton_Click(object sender, RoutedEventArgs e)
        {
            // Démarre le test du setup
            plugin.PluginManager.ExecuteCommand("StartSetupTest");
        }

        private void StopTestButton_Click(object sender, RoutedEventArgs e)
        {
            // Arrête le test du setup
            plugin.PluginManager.ExecuteCommand("StopSetupTest");
        }
    }
}
