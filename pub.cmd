touch readme.md
touch *.py
touch *.sh
git add -A :/
git commit -m "updated %date% @ %time%"
git push
start "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" https://github.com/johnwargo/Raspberry-Pi-Relay-Timer