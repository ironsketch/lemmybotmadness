#! /usr/bin/env python3
import requests, sys, time

username = "lemmy_bot" # The username that you set up for your bot account. I just called mine lemmy_bot
password = "redacted" # The password to your bot account
apiaddy = "https://yourdomain.tld/api/v3/" # Your instance api base address 
jwt = "" # This will be used for the authentication key grabbed

def retrieve_jwt():
    global jwt
    global username
    global password
    global apiaddy

    payload = {"username_or_email": username, "password": password}
    r = requests.post(apiaddy + "user/login", json=payload)

    try:
        jwt = r.json()["jwt"]
    except KeyError as e:
        raise e
    
def follow(id):
    global jwt 
    global apiaddy

    # In order to follow a community, you need the id, follow = true and the authentication
    follow_payload = { "community_id": id, "follow": True, "auth": jwt }
    requests.post(apiaddy + "community/follow", timeout=15, json=follow_payload)

def resolveObject(search):
    global jwt 
    global apiaddy

    # In order to follow a community, it MUST first be resolved (The same as going to your
    # community search page and searching !name@domain.tld)
    r = requests.get(apiaddy + "resolve_object?q=" + search + "&auth=" + jwt)
    # We get the community id that was grabbed from our resolved object
    return r.json()["community"]["community"]["id"]

def getCommunities(extdomain):
    # This is a terrible function and must be updated... Sorry not sorry
    # When you call community/list you have to search page by page... 
    # This goes through the range of 1 to 9999. A better way to program 
    # this is either to get how many pages their are (if possible) and iterate through that
    # Or stop once the return is empty
    for page in range(1,9999):
        # The domain passed here is the external domain that we are searching communities in, not your domain
        url = "https://" + extdomain + "/api/v3/community/list?sort=Hot&page=" + str(page)
        try:
            result = requests.get(url)
            communities = result.json()["communities"]

            for comm in communities:
                addy = comm["community"]["actor_id"] # https://lemmygrad.ml/c/mmtc (example)
                addySplit = addy.split('/')
                # This domain does not always match the external domain we are searching on.
                communityFoundExtDomain = addySplit[2]
                print("Subscribing to: " + comm["community"]["name"])

                for _ in range(5):
                    try:
                        # This is also stupid programming. A better way to handle this is to
                        # search your instance to see if the follow was added. If not try again.
                        # Otherwise continue
                        search = "!" + comm["community"]["name"] + "%40" + communityFoundExtDomain
                        id = resolveObject(search)
                        follow(id) 
                        # Sleeping here isn't needed... don't ask
                        time.sleep(1)
                    except Exception as e:
                        print(e)
        except:
            break

def main():
    instances = open('approvedServerList.txt', 'r')
    for instance in instances:
        # Grab the login authentication key
        retrieve_jwt()
        print(instance.strip())
        # Get all the communities it can
        getCommunities(instance.strip())

main()
