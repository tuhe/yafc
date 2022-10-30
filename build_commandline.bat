del /s /q Build 
dotnet publish CommandLineToolExample/CommandLineToolExample.csproj -r win-x64 -c Release -o CommandLineToolExample/Build/Windows -p:PublishTrimmed=true
