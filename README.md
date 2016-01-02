# audio_player
stream audio from youtube to raspberry pi

Developed on windows, so it will also mostly work on that as well. Uses omx player on the pi and ffplay.exe on windows. 

It uses youtube-dl to download the audio only version of the videos and the youtube api to search for them.  You'll need a google api key with the youtube api enabled on your account (https://cloud.google.com/console)

Expects a config.json file to live where the code does of the form

{
"host': "raspberry pi ip address", 
"user': "raspberry pi user",
"password": "raspberry pi password",
"api_key": "google api key"
}
