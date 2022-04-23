import requests
import random
import math
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import sys

class GroupNode:
    def __init__(self, artist_name, artist_id):
        self.members = {} # dict of lists. each key is an artist, vals lists of bands
        self.group_name = artist_name
        self.group_artist_id = artist_id
        
class BandGraph:

    def __init__(self):

        self.graph_nodes = {}
        self.person_name_lookup = {}
        self.node_queue = []
        self.visited = set()
        self.session = requests.Session()
        retry = Retry(connect=5, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        random.seed(22)

    def set_focal(self, artist_name):
        p = {"commonName":artist_name}
        response = requests.get(shs_url + "artist", params=p, headers={"Accept": "application/json"})
        resp = response.json()

        if resp['totalResults'] > 0:
            artist_res = resp['resultPage'][0]
            artist_id = artist_res['uri'].split("/")[-1]
            n = GroupNode(artist_name, artist_id)
            self.graph_nodes[artist_id] = n
            self.node_queue.append(n)

    def bfs_build(self):

        n = self.node_queue.pop()
        a_url = 'https://secondhandsongs.com/artist/%s' % (n.group_artist_id)
        artist_resp = self.session.get(a_url, headers={"Accept": "application/json"}).json()

        i = 0
        for r in artist_resp['relations']:
            if r['relationName'] == 'has as member':
                i += 1
                
        if i < 10:
            for r in artist_resp['relations']:
                if r['relationName'] == 'has as member':
                    person_name = r['artist']['commonName']
                    person_id = r['artist']['uri'].split("/")[-1]
                    if not person_id in self.person_name_lookup:
                        self.person_name_lookup[person_id] = person_name
                        self.get_group_nodes(person_id, n)
            
    def get_group_nodes(self, person_id, group_node):

        '''
        Scan through all the bands an artist has been in
        Update pointers for relationships
        '''

        a_url = 'https://secondhandsongs.com/artist/%s' % (person_id)
        artist_resp = self.session.get(a_url, headers={"Accept": "application/json"}).json()
        if not person_id in group_node.members:
            group_node.members[person_id] = []

        for r in artist_resp['relations']:
            if r['relationName'] == 'is member of':
                group_name = r['artist']['commonName']
                group_id = r['artist']['uri'].split("/")[-1]

                if not group_id in self.visited and group_id != group_node.group_artist_id:
                    n = GroupNode(group_name, group_id)
                    self.visited.add(group_id)
                    self.node_queue.append(n)
                    self.graph_nodes[group_id] = n
                else:
                    n = self.graph_nodes[group_id]

                
                if not person_id in n.members:
                    n.members[person_id] = []
                n.members[person_id].append(group_node)

                if not person_id in group_node.members:
                    group_node.members[person_id] = []
                group_node.members[person_id].append(n)

    def run_bfs_build(self):

        while len(self.node_queue) > 0:
            print(f"{len(self.node_queue)}")
            self.bfs_build()
        self.print_edge_list()

    def print_edge_list(self):
        for n in self.graph_nodes:
            for m in self.graph_nodes[n].members:
                for j in self.graph_nodes[n].members[m]:
                    if self.graph_nodes[n].group_artist_id != j.group_artist_id:
                        print(f"{self.graph_nodes[n].group_name}\t{self.person_name_lookup[m]}\t{j.group_name}")


shs_url = 'https://secondhandsongs.com/search/'
if __name__ == "__main__":
    focal_artist = sys.argv[1]
    
    g = BandGraph()
    g.set_focal(sys.argv[1])
    g.run_bfs_build()




