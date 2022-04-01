
import requests
import random

class GraphNode:
    def __init__(self, artist_name, artist_id):
        self.songs_covered  = {} # key is song, val is artist
        self.songs_written  = {} # key is song, val is artist
        self.artist_name = artist_name
        self.artist_id = artist_id

class CoverGraph:
    def __init__(self):
        self.graph_nodes = {}
        self.paths = []
        self.song_lookup = {}
        self.video_lookup = {}
        self.artist_lookup = {}
        self.verbose = False

    def print_edge_list(self):
        for gn in self.graph_nodes.values():
            for song in gn.songs_covered:
                print(f'{gn.artist_name}\t{self.song_lookup[song]}\t{gn.songs_covered[song].artist_name}\t{self.video_lookup[song]}')

    def handle_works(self, depth, max_depth, back_node_queue, visited_list):

        n = self.graph_nodes[back_node_queue.pop()]
        p_url = 'https://secondhandsongs.com/artist/%s/performances' % (n.artist_id)
        print(f'getting works by {n.artist_name}, total: {len(back_node_queue)} depth: {depth}')
        print(f'{p_url}')

        perf_list = requests.get(p_url, headers={"Accept": "application/json"}).json()
        print(len(perf_list))
        i = 0
        j = 0
        if not 'error' in perf_list:
            # find all the works by this artist
            for perf in perf_list:
                
                valid_orig_work = False
                if perf['isOriginal']:
                    i += 1
                    valid_orig_work = True

                    try:
                        perf_resp = requests.get(perf['uri'], headers={"Accept": "application/json"}).json()
                        work_uri = perf_resp['works'][0]['uri']
                        work_resp = requests.get(work_uri, headers={"Accept": "application/json"}).json()

                        song_title = work_resp['title']
                        song_artist = perf_resp['performer']['name']
                        song_artist_id_concat = perf_resp['performer']['uri'].split("/")[-1]
                        song_id = work_resp['uri'].split("/")[-1]
                        self.song_lookup[song_id] = song_title
                        j += 1
                        
                    except:
                        if self.verbose:
                            print(f"skipping work\t{work_resp['title']}")
                        valid_orig_work = False

                # find all the covers of the work
                if valid_orig_work:
                    print(song_title, i , j)
                    for perf in work_resp['versions']:
                        perf_artist = perf['performer']['name']
                        perf_artist_id_concat = perf['performer']['uri'].split("/")[-1]
                        for perf_artist_id in perf_artist_id_concat.split("+"):
                            if not perf['isOriginal'] and \
                            not perf_artist.lower() in song_artist.lower() and \
                            not song_artist.lower() in perf_artist.lower():

                                if perf_artist_id in self.graph_nodes:
                                    artist_node = self.graph_nodes[perf_artist_id]
                                else:
                                    artist_node = GraphNode(perf_artist, perf_artist_id)
                                    self.graph_nodes[perf_artist_id] = artist_node

                                if 'external_uri' in perf:
                                    video_link = perf['external_uri'][0]['uri']
                                else:
                                    video_link = 'no video'
                                self.video_lookup[song_id] = video_link

                                # link the cover to this node
                                for song_artist_id in song_artist_id_concat.split("+"):
                                    artist_node.songs_covered[(song_artist_id, song_id, perf_artist_id)] = n
                                    n.songs_written[(song_artist_id, song_id, perf_artist_id)] = artist_node

                                if self.verbose:
                                    print(f'adding cover of:\t{self.song_lookup[song_id]}\tby\t{perf_artist}')
                                if depth <= max_depth:
                                    if not artist_node.artist_id in visited_list:
                                        back_node_queue = [artist_node.artist_id] + back_node_queue
                                        visited_list.add(artist_node.artist_id)
                                        print(f'adding {artist_node.artist_name} ({artist_node.artist_id}) to queue, total: {len(back_node_queue)} depth: {depth}')
                                        print(len(back_node_queue))
                                        #print(back_node_queue)

                    if len(back_node_queue) > 0 and depth < max_depth:
                        self.handle_works(depth+1, max_depth, back_node_queue, visited_list)
                


    def handle_perfs(self, depth, max_depth, node_queue, visited_list):
        
        n = self.graph_nodes[node_queue.pop()]
        p_url = 'https://secondhandsongs.com/artist/%s/performances' % (n.artist_id)
        print(f'getting performances by {n.artist_name}\td: {depth}')
        try:
            perf_list = requests.get(p_url, headers={"Accept": "application/json"}).json()
        except:
            perf_list = {'error'}
        print(len(perf_list))

        if not 'error' in perf_list:
            for perf in perf_list:
                if not perf['isOriginal']:
                    
                    valid_json = True
                    try:
                        pr = requests.get(perf['uri'], headers={"Accept": "application/json"})
                        perf_resp = pr.json()
                    except:
                        valid_json = False
                    if valid_json and len(perf_resp['originals']) > 0:

                        original = perf_resp['originals'][0]['original']
                        if original['performer']:
                            if 'external_uri' in perf_resp and len(perf_resp['external_uri']) > 0:
                                video_link = perf_resp['external_uri'][0]['uri']
                            else:
                                video_link = 'no video'
                            song_artist_id_concat = original['performer']['uri'].split("/")[-1]
                            perf_artist_id_concat = perf_resp['performer']['uri'].split("/")[-1]

                            ids = song_artist_id_concat.split("+")
                            if len(ids) > 4:
                                ids = []

                            for song_artist_id in ids:
                                
                                if song_artist_id in self.graph_nodes:
                                    artist_node = self.graph_nodes[song_artist_id]
                                else:
                                    a_url = 'https://secondhandsongs.com/artist/%s' % (song_artist_id)
                                    artist_resp = requests.get(a_url, headers={"Accept": "application/json"}).json()
                                    #print(artist_resp)
                                    song_artist = artist_resp['commonName']
                                    artist_node = GraphNode(song_artist, song_artist_id)
                                    self.graph_nodes[song_artist_id] = artist_node
                                
                                song_title = original['title']
                                if self.verbose:
                                    print(f'adding cover of:\t{song_title}\tby\t{song_artist} total: {len(node_queue)} depth: {depth}')

                                song_id = original['uri'].split("/")[-1]
                                self.song_lookup[song_id] = song_title
                                self.video_lookup[song_id] = video_link

                                pids = perf_artist_id_concat.split("+")
                                if len(pids) > 4:
                                    pids = []
                                for perf_artist_id in pids:
                                    #print(perf_artist_id, song_artist_id)
                                    n.songs_covered[(song_artist_id, song_id, perf_artist_id)] = artist_node
                                    artist_node.songs_written[(song_artist_id, song_id, perf_artist_id)] = n

                                    if depth <= max_depth:
                                        if not artist_node.artist_id in visited_list:
                                            node_queue = [artist_node.artist_id] + node_queue
                                            visited_list.add(artist_node.artist_id)
                                            print(f'adding:{artist_node.artist_name} to queue ({song_title} :: {n.artist_name}) total: {len(node_queue)} depth: {depth}')
                if len(node_queue) > 0 and depth < max_depth:
                    self.handle_perfs(depth+1, max_depth, node_queue, visited_list)


    def print_playlist(self, path, out_file):
        """
        follow a linear chain of nodes representing the list of songs
        """

        edges = list(path.songs_written.keys())

        if len(edges) >= 2:
            print('ERROR: non-linear path')
            print(edges)

        print("\n", file=out_file)
        while len(edges) == 1:
            edge_id = edges[0]
            a1, work_id, a2 = edge_id
            work_name = self.song_lookup[work_id]
            covered_by = path.songs_written[edge_id]
            print(f'\t{covered_by.artist_name}\t{work_name}\t{path.artist_name}\t{self.video_lookup[work_id]}', file=out_file)
            path = covered_by
            edges = list(path.songs_written.keys())

    def dfs(self, stack, current_path, min_path_len, depth, visited_nodes, out_file):
        """
        follow edges, cover-er to cover-ee.
        """

        if self.verbose:
            print("stack:")
            for m in stack:
                print("\t%s" % (m.artist_name))
            print("\n")

        n = stack.pop()

        # if we encounter a leaf, print the path
        print(f'{len(n.songs_covered)}\td:{depth}')
        if len(n.songs_covered) == 0:
            print("leaf:\t%s" % (n.artist_name))
            if depth >= min_path_len:
                self.paths.append(current_path)
                self.print_playlist(current_path, out_file)

        # for internal nodes continue the search
        for edge_id in n.songs_covered:
            artist_1_id, work_id, artist_2_id = edge_id
            orig_artist_node = n.songs_covered[edge_id]
            if not orig_artist_node.artist_id in visited_nodes:
                stack = [orig_artist_node] + stack
                visited_nodes.add(orig_artist_node.artist_id)
                updated_path = GraphNode(orig_artist_node.artist_name, orig_artist_node.artist_id)
                updated_path.songs_written[edge_id] = current_path
            
            if self.verbose:
                print("-----")
                print("\t" + current_path.artist_name)
                print("\t" + self.song_lookup[work_id])
                print("\t" + updated_path.artist_name)
                print("\t%s" % (depth))
                print("------")

            if len(stack) > 0:
                self.dfs(stack, updated_path, min_path_len, depth+1, visited_nodes, out_file)

    def get_paths_exhaustive_dfs(self, min_path_len, out_file):
        for n in self.graph_nodes.values():

            current_path = GraphNode(n.artist_name, n.artist_id)
            stack = [n]         
            if len(n.songs_written) == 0 and len(n.songs_covered) > 0:
                print(n.artist_name, n.artist_id)
                print(n.songs_covered)
                self.dfs(stack, current_path, min_path_len, 0, set([n.artist_id]), out_file)

    """
    def get_paths_random_dfs(self, x, min_path_len, out_file):
        s = []
        for n in self.graph_nodes:
            s.append(n)
        random.shuffle(s)

        for n in self.graph_nodes:
            current_path = GraphNode(n.artist_name, n.artist_id)
            stack = [n]            
            self.dfs(stack, current_path, min_path_len, 0, out_file)
    """

