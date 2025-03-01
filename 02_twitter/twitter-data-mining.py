# -*- encoding: utf-8 -*-
#
# Social Network Analysis of Twitter lists members connections (Ego Networks)
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: GPL v.3
#
# Requisite:
# pip install twitter
# pip install networkx
#

# Import libraries
from twitter import *
import networkx as nx
from time import sleep
import sys
import os
import unicodedata
import pandas as pd
import json

# Some global variables
graph = nx.DiGraph()
locations = {}
errors = 0
protected_users = 0

# Your Twitter App details
# Get them from http://dev.twitter.com
OAUTH_TOKEN = ""
OAUTH_SECRET = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""


##########################################################################
#
# load_connections: load connections (followers, following) in one list of Twitter accounts
#

def load_connections(user_list, option):

    global errors
    global protected_users
    connections = {}

    for p in user_list:
        query = {}
        counting = 0
        cursor = -1
        connections[p] = []

        while cursor != "0":

            # API: https://dev.twitter.com/docs/api/1.1/get/friends/ids
            try:
                if option == "followers":
                    query = twitter.followers.ids(
                        user_id=p, count=5000, cursor=cursor)
                else:
                    query = twitter.friends.ids(
                        user_id=p, count=5000, cursor=cursor)
                cursor = query["next_cursor_str"]
                for idtocheck1 in query["ids"]:
                    connections[p].append(idtocheck1)

            except Exception as e:
                if "Rate limit exceeded" in str(e):
                    print("Rate exceeded... waiting 15 minutes before retrying")
                    notworking = False
                    # Countdown http://stackoverflow.com/questions/3249524/print-in-one-line-dynamically-python
                    for k in range(1, 60 * 15):
                        remaining = 60 * 15 - k
                        sys.stdout.write(
                            "\r%d seconds remaining   " % remaining)
                        sys.stdout.flush()
                        sleep(1)
                    sys.stdout.write("\n")

                    if option == "followers":
                        try:
                            query = twitter.followers.ids(
                            user_id=p, count=5000, cursor=cursor)
                        except:
                            cursor = "0"
                            errors += 1
                            notworking = True
                    else:
                        try:
                            query = twitter.friends.ids(
                            user_id=p, count=5000, cursor=cursor)
                        except:
                            cursor = "0"
                            errors += 1
                            notworking = True

                    if notworking is False:
                        cursor = query["next_cursor_str"]
                        for idtocheck2 in query["ids"]:
                            connections[p].append(idtocheck2)

                elif "Not authorized" in str(e):
                    print("There were some errors with user", i, "... most likely it is a protected user")
                    cursor = "0"
                    errors += 1
                    protected_users += 1

                else:
                    print("Some error happened with user", i)
                    cursor = "0"
                    errors += 1

    return connections

##########################################################################
#
# Main
#

if __name__ == "__main__":

    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    print()
    print(".....................................................")
    print("Connections among members in users searched on Twitter by keywords")
    print("")

    # Log in
    # api_version="2"
    # Issue: get API v2 academic registration, to do pagination of results without replications
    # Issue: transform into a platform_analysis module, author-team-community
    twitter = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET), api_version="1.1")
    # Search keywords
    keywords = ["fablab", "fab lab", 
                "makerspace", "hackerspace", 
                "diybio", "techshop", 
                "repaircafe", "repair cafe", 
                "makerfaire", "maker faire", 
                "diy-bio", "diybio", 
                "diy-bio lab", "diybio lab", "diybiolab", 
                "hacklab", "sewing cafe", "sewingcafe"]
    # Author
    author = ['openp2pdesign']
    # Team
    github_users = pd.read_csv("data/github2twitter_users.csv")
    github_users.set_index("Unnamed: 0", inplace=True)
    team = [x for x in github_users["twitter"].tolist() if str(x) != 'nan']

    print("Keywords:")
    print(keywords)
    print()
    # Search
    print("Searching these terms:")
    print()
    search_results = []
    members = []
    members_usernames = []
    members_data = {}
    search_results_stats = {}
    for word in keywords:
        print(word)
        search_results_word = []
        # Pagination issue https://twittercommunity.com/t/odd-pagination-behavior-with-get-users-search/148502
        # Only the first 1,000 matching results are available.
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
        for i in range(50):
            try:
                search = twitter.users.search(q=word,page=i,count=20)
                search_results.append(search)
                for k in search:
                    search_results_word.append(k)
            except Exception as e:
                print(i-1, 'pages of results with', len(search_results_word),' results')
                break
        search_results_stats[word] = search_results_word
    for result in search_results:
        for user in result:
            members_data[user["id"]] = user
            members.append(user["id"])
            members_usernames.append(user["screen_name"])

    # TEAM
    # Search (directly) for team members
    print()
    print("Team:")
    print(team)
    print()
    print("Looking up for these Team users:")
    for user in team:
        print(user)
        try:
            search = twitter.users.lookup(screen_name=user,page=i)
            search_results.append(search)
        except:
            pass
    for result in search_results:
        for user in result:
            members_data[user["id"]] = user
            members.append(user["id"])
            members_usernames.append(user["screen_name"])

    # AUTHOR
    # Search (directly) for author
    print()
    print("Authors:")
    print(author)
    print()
    print("Looking up for these authors:")
    for user in author:
        print(user)
        try:
            search = twitter.users.lookup(screen_name=user, page=i)
            search_results.append(search)
        except:
            pass
    for result in search_results:
        for user in result:
            members_data[user["id"]] = user
            members.append(user["id"])
            members_usernames.append(user["screen_name"])

    # Save results as JSON
    with open('search_results_stats.json', 'w') as fps:
        json.dump(search_results_stats, fps)
    # Remove duplicates
    members = list(dict.fromkeys(members))

    print("")
    print("Checking the connections among the users...")

    # Load connections of each member
    for k,l in enumerate(members):
        print()
        print(k+1,"/", len(members))
        print("USER:", members_data[l]["screen_name"])
        print("Loading connections...")
        followers = load_connections([l], "followers")
        friends = load_connections([l], "friends")

        # Add edges...
        print("Building the graph...")

        for f in followers:
            for k in followers[f]:
                graph.add_edge(k, f)

        for o in friends:
            for p in friends[o]:
                graph.add_edge(o, p)

    # Prepare 100 ids lists for converting id to screen names
    mapping = {}
    lista = {}
    position = 0
    hundreds = 0
    lista[hundreds] = []
    for d in graph.nodes():
        if position == 100:
            hundreds += 1
            position = 0
            lista[hundreds] = []
        lista[hundreds].append(d)
        position += 1


    # Save the full graph, all members of the chosen lists and all their
    # connections
    print()
    print("The personal profile was analyzed successfully.", errors, "errors were encountered.", len(graph), "nodes in the network.")
    print()
    print(protected_users, " protected users found.")
    print()
    print("Saving the file as twitter-lists-ego-networks-full.gexf...")
    nx.write_gexf(graph, "twitter-lists-ego-networks-full.gexf")

    # Clean from nodes who are not members, in order to get a 1.5 level network
    nodes_to_remove = []
    for v in graph.nodes(data=True):
        if v[0] not in members:
            nodes_to_remove.append(v[0])
        else:
            for j in members_data[v[0]]:
                try:
                    if members_data[v[0]][j] == None:
                        graph.nodes[v[0]][j] = "None"
                    else:
                        graph.nodes[v[0]][j] = members_data[v[0]][j]
                except:
                    pass
    graph.remove_nodes_from(nodes_to_remove)

    # Adding the team attribute
    for v in graph.nodes(data=True):
        if graph.nodes[v[0]]['screen_name'] in team:
            graph.nodes[v[0]]['team'] = True
        else:
            graph.nodes[v[0]]['team'] = False
    # Adding the author attribute
    for v in graph.nodes(data=True):
        if graph.nodes[v[0]]['screen_name'] in author:
            graph.nodes[v[0]]['author'] = True
            graph.nodes[v[0]]['team'] = False
        else:
            graph.nodes[v[0]]['author'] = False
    # Save the graph, only members of the chosen lists and the connections
    # among them
    print()
    print("Saving the file as twitter-lists-ego-networks-members.gexf...")
    nx.write_gexf(graph, "twitter-list-ego-networks-members.gexf")
