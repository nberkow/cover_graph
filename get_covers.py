from CoverGraph import *
import requests


shs_url = 'https://secondhandsongs.com/search/'

if __name__ == "__main__":

    # Build the subgraph for an artist by accessing the api
    ## nodes: artists
    ## edges: song, cover-er to cover-ee
    
    # examples
    """
    shs_url = 'https://secondhandsongs.com/performance/123'
    response = requests.get(shs_url, headers={"Accept": "application/json"})
    print(response.json())

    shs_url = 'https://secondhandsongs.com/artist/123'
    response = requests.get(shs_url, headers={"Accept": "application/json"})
    print(response.json())

    shs_url = 'https://secondhandsongs.com/artist/88/performances'
    response = requests.get(shs_url, headers={"Accept": "application/json"})
    print(response.json())

    shs_url = 'https://secondhandsongs.com/artist/2870/works'
    response = requests.get(shs_url, headers={"Accept": "application/json"})
    print(response.json())
    """

    """['R.E.M.',
        'Nirvana', 
        'Olivia Rodrigo',
        'Bebe Rexha'
        's club 7',
        'Garth Brooks', 
        'Weezer',
        'get up kids',
        'CHVRCHES',
        'Gillian Welch', 
        'Katy Perry',
        'Taylor Swift',
        'Phoebe Bridgers']:"""
    for focal_artist in ['Phoebe Bridgers']:

        print("".join(focal_artist.split()))
        out_path = '/mnt/c/Documents and Settings/Nathan/Documents/covers/'
        with open('%s%s_playlists.txt' % (out_path, "".join(focal_artist.split())), 'w') as lists_file, \
             open('%s%s_artists.txt' % (out_path, "".join(focal_artist.split())), 'w') as artists_file, \
             open('%s%s_graph.txt' % (out_path, "".join(focal_artist.split())), 'w') as graph_file, \
             open('%s%s_path_graph.txt' % (out_path, "".join(focal_artist.split())), 'w') as path_graph_file:
            p = {"commonName":focal_artist}
            g = CoverGraph()
            g.song_lookup = {}
            node_queue = [] 
            back_node_queue = [] 
            depth = 0
            fwd_depth = 7
            back_depth = 3
            min_path_depth = 5

            # get the focal artist. Assume it's the first entry in the list
            response = requests.get(shs_url + "artist", params=p, headers={"Accept": "application/json"})
            resp = response.json()

            if resp['totalResults'] > 0:
                artist_info = resp['resultPage'][0]
                artist_id = artist_info['uri'].split("/")[-1]
                n = GraphNode(focal_artist, artist_id)
                g.graph_nodes[artist_id] = n
                node_queue.append(artist_id)
                back_node_queue.append(artist_id)

                print("building graph")
                # build the graph in both directions

                # works of the focal artist covered by others
                g.handle_works(depth, fwd_depth, back_node_queue, set([artist_id]))

                # covers of other artists by the focal artist
                g.handle_perfs(depth, back_depth, node_queue, set([artist_id]))
                print("graph built!")
                
                # save the graph
                g.print_edge_list(graph_file)

                for n in g.graph_nodes.values():
                    print(f"\t{n.artist_name}\t{n.artist_id}", file = artists_file)

                g.get_paths_exhaustive_dfs(min_path_depth)
                
                g.print_playlists(lists_file)

                # print the graph with a path highlighted (make random)
                d = list(g.paths.keys())
                d.sort(reverse=True)
                s = list(g.paths[d[0]])
                p = s[0]
                g.make_path_graph(p, path_graph_file)

            #g.print_edge_list()



                


                        








