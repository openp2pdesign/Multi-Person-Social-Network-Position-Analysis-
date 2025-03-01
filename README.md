# Multi-Person-Social-Network-Position-Analysis-
Python code for the Multi-Person Social Network Position Analysis methodology, for identifying the position in time, activities and social network of interactions over digital platforms as a way for integrating the first-person perspective of a designer, her team (second-person) and community (third-person). 

## 01_github

Requirements for Virtualenv in `requirements.txt`.  
Run first `01_github_data.ipynb` with Jupyter Lab/Notebook to extract the data. Get the Github token from https://github.com/settings/tokens  
Run then `02_analysis.ipynb` to finalize the data analysis, saving images.  

## 02_twitter

Requirements for Virtualenv in `requirements.txt`.
Add a .csv file with the `team` users from GitHub (to be found in Twitter) in `data/github2twitter_users.csv`
Add the developer details in the script before running, get them from: https://developer.x.com/en

`OAUTH_TOKEN = ""`  
`OAUTH_SECRET = ""`  
`CONSUMER_KEY = ""`  
`CONSUMER_SECRET = ""`  

Run the script in the terminal.

## 03_analysis

Requirements for Virtualenv in `requirements.txt`.  
Add network data as .graphml in `data/github.graphml` and `data/twitter.graphml`.  
`graph-tool` (necessariy for similarity computing in `Analysis_Jaccard_Similarity_Github.ipynb` and `Analysis_Jaccard_Similarity_Twitter.ipynb`) nont included in `requirements.txt"`, see here how to install and run it https://graph-tool.skewed.de/
The notebooks have already code for installing it in Google Colab.

Run files with Jupyter Lab/Notebook in no particular order.