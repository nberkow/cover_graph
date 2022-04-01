import requests

shs_url = 'https://secondhandsongs.com/search/artist'
#shs_url = 'https://secondhandsongs.com/performance/1326103'

if __name__ == "__main__":

    query = {'commonName':'cher'}
    response = requests.get(shs_url, params=query, headers={"Accept": "application/json"})
    print(response.json())

    """
    #response = requests.get(shs_url, params={"commonName":"cher"}, json=True)
    #print(response.json())

    query = {'lat':'45', 'lon':'180'}
    response = requests.get('http://api.open-notify.org/iss-pass.json', params=query)
    print(response.json())
    """

    """
    working cmd
    
    curl -X GET "https://secondhandsongs.com/search/artist" 
    -H 'Content-Type: application/json'
    -d '{"commonName":"cher"}'
    """