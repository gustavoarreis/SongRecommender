# Interactive song recommender and playlist creator Flask app built using Spotify API.

## The Basics

Get your Spotify API credentials at https://developer.spotify.com/.
Store your credentials (API key, API secret and redirect URI) on a "config.cfg" file in your environment, along with your Spotify username. 
I've used this format for the config.cfg file:

    >[KEYS]
    >client_id: "xxxxxxx"
    >client_secret: "xxxxxxxx"
    >redirect_uri: "xxxxxxxx"
    >username: "xxxxxxx"

Codes use Python package "spotipy" to interact with Spotify API. Make sure to install it.

File "spotify.py" contains all the back-end interaction with the Spotify API. "app.py" contains the Flask app code. The html templates for each endpoint in the app are included as well as the .css static. 

## The Idea

"Similarity" between songs can mean several things. Key, tempo, instrumentation are all different characteristics of a song, but two songs can be similar while having none of these features in common. Songs can be similar because they evoke similar feelings of joy (or sadness), or because both are very danceable. 

Spotify has a [smart recommendation algorithm](https://www.linkedin.com/pulse/how-spotify-recommender-system-works-daniel-roy-cfa/?trk=read_related_article-card_title) that uses collaborative filtering (recommendations based on what similar users enjoy), Natural Language Processing and a machine learning classifier to cluster songs based on audio features. 

The Spotify API provides access to these audio features. Each song has numeric grades for each of these characteristics:
    
* **Danceability**: Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.
* **Energy**: Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
* **Loudness**: The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.
* **Mode**: Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.
* **Speechiness**: Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
* **Acousticness**: A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.
* **Instrumentalness**: Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
* **Liveness**: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.
* **Valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
* **Tempo**: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
* **Key**: The key the track is in. Integers map to pitches using standard Pitch Class notation . E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on.
* **Time Signature**: An estimated overall time signature of a track. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure).

What the app does is to further **enhance** this recommendation system by letting the user choose the criteria for track similarity. The user can select as many features as they want to describe what they like about the reference track/what they seek for similar tracks. The app then takes a large number of Spotify recommendations and calculates the [Euclidian distance](https://en.wikipedia.org/wiki/Euclidean_distance) between them using these features. The smaller the distance between tracks, the more similar they are. Notice the more features you choose, the greater the distance tends to be. 

The group of recommendations consists of the top 25 most similar. The app then provides an option to automatically create a playlist of recommendations using the Spotify user. 

Enjoy!