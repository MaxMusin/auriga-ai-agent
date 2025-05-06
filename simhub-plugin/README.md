# Plugin SimHub pour Auriga AI

Ce plugin permet de connecter SimHub à l'agent d'optimisation Auriga AI pour iRacing.

## Installation

1. Fermez SimHub s'il est en cours d'exécution
2. Copiez le dossier `AurigaAI` dans le répertoire des plugins SimHub :
   - Généralement situé dans `C:\Program Files (x86)\SimHub\PluginsSDK\`
   - Ou dans `%PROGRAMDATA%\SimHub\PluginsSDK\`
3. Lancez SimHub
4. Activez le plugin dans la liste des plugins disponibles

## Configuration

1. Dans SimHub, accédez au plugin "Auriga AI" dans le menu de gauche
2. Configurez l'URL de l'API (par défaut : http://localhost:8080)
3. Cliquez sur "Sauvegarder"

## Utilisation

1. Lancez iRacing et chargez un setup à tester
2. Dans SimHub, cliquez sur "Démarrer le test"
3. Effectuez un tour complet sur la piste
4. Après avoir franchi la ligne d'arrivée, évaluez les différents aspects du setup (stabilité, traction, etc.)
5. Ajoutez des notes si nécessaire
6. Les données seront automatiquement envoyées à l'API Auriga AI
7. Récupérez le prochain setup à tester en cliquant sur "Démarrer le test" à nouveau

## Métriques évaluées

Le plugin collecte automatiquement les données suivantes :
- Temps au tour
- Températures des pneus
- Usure des pneus
- Conditions météorologiques

Vous devez évaluer manuellement les aspects suivants :
- Stabilité générale de la voiture (1-10)
- Stabilité en entrée de virage (1-10)
- Stabilité en sortie de virage (1-10)
- Traction (1-10)
- Stabilité au freinage (1-10)

## Compilation (pour les développeurs)

Pour compiler le plugin, vous aurez besoin de :
1. Visual Studio 2019 ou supérieur
2. .NET Framework 4.7.2 ou supérieur
3. Références aux DLLs de SimHub (GameReaderCommon.dll, SimHub.Plugins.dll)

## Dépannage

Si vous rencontrez des problèmes :
1. Vérifiez que le serveur Auriga AI est en cours d'exécution
2. Vérifiez que l'URL de l'API est correcte
3. Consultez les logs de SimHub pour plus d'informations
