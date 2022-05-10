import http.client
import json
import csv
import urllib.request
import urllib.response


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str) -> None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """
        if name.find(',') != -1:
            i = name.index(',')
            name = name[:i]+name[i+1:]

        if (id, name) not in self.nodes:
        	self.nodes.append((id, name))


    def add_edge(self, source: str, target: str) -> None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """
        if ((source, target) not in self.edges and (target, source) not in self.edges):
        	self.edges.append((source, target))


    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)


    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)

    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        a = {}
        for id, name in self.nodes:
        	a[id] = 0
        	for s,t in self.edges:
        		if id == s or id == t:
        			a[id] = a[id]+1
        a_sorted = sorted(a.items(), key = lambda x: x[1], reverse=True)
        r = {a_sorted[0][0]:a_sorted[0][1]}
        for i in range(1,len(a_sorted)):
        	if a_sorted[i-1][1] == a_sorted[i][1]:
        		r[a_sorted[i][0]] = a_sorted[i][1]
        	else:
        		break
        return r


    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(n[0] + "," + n[1] + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")



class  TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param integer movie_id: a movie_id
        :param integer limit: maximum number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range).
            If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
            If after excluding, the limit is not specified, then return all remaining cast members."
            e.g., if limit=5 and the actor whose id corresponds to cast member with order=1 is to be excluded,
            return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': '97909' # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
                Note that this is an example of the structure of the list and some of the fields returned by the API.
                The result of the API call will include many more fields for each cast member.

        Important: the exclude_ids processing should occur prior to limiting output.
        """
        url = "https://api.themoviedb.org/3/movie/"+movie_id+"/credits?api_key="+self.api_key+"&language=en-US"
        conn = urllib.request.urlopen(url)

        if conn.getcode() == 200:
            pass
        else:
            return None

        data = conn.read()
        contents = json.loads(data.decode('utf-8'))
        cast = contents['cast']
        cast_filtered = cast

        if exclude_ids:
            cast_filtered = [x for x in cast if x['id'] not in exclude_ids]

        if limit:
            cast_filtered = [x for x in cast_filtered if x['order'] < limit]

        return cast_filtered


    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
        """
        Using the TMDb API, get the movie credits for a person serving in a cast role
        documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits

        :param string person_id: the id of a person
        :param vote_avg_threshold: optional parameter to return the movie credit if it is >=
            the specified threshold.
            e.g., if the vote_avg_threshold is 5.0, then only return credits with a vote_avg >= 5.0
        :rtype: list
            return a list of dicts, one dict per movie credit with the following structure:
                [{'id': '97909' # the id of the movie credit
                'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                'vote_avg': 5.0 # the float value of the vote average value for the credit}, ... ]
        """
        url = "https://api.themoviedb.org/3/person/"+ person_id+"/movie_credits?api_key="+self.api_key+"&language=en-US"
        conn = urllib.request.urlopen(url)

        if conn.getcode() == 200:
            pass
        else:
            return None

        data = conn.read()
        contents = json.loads(data.decode('utf-8'))
        cast = contents['cast']
        cast_filtered = cast

        if vote_avg_threshold:
            cast_filtered = [x for x in cast if x['vote_average'] >= vote_avg_threshold]

        return cast_filtered


def return_name()->str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    username = 'jyi67'
    return username

def return_argo_lite_snapshot()->str:
    """
    Return the shared URL of your published graph in Argo-Lite
    """
    return "https://poloclub.github.io/argo-graph-lite/#2719d6ec-0d4d-450e-b42f-727ed8605076"


# You should modify __main__ as you see fit to build/test your graph using  the TMDBAPIUtils & Graph classes.
# Some boilerplate/sample code is provided for demonstration. We will not call __main__ during grading.

if __name__ == "__main__":

    graph = Graph()
    graph.add_node(id='2975', name='Laurence Fishburne')
    tmdb_api_utils = TMDBAPIUtils(api_key='3a631989315c63cac7014ab62bfed2d0')

    # call functions or place code here to build graph (graph building code not graded)
    # Suggestion: code should contain steps outlined above in BUILD CO-ACTOR NETWORK


    def build_base_graph(graph:Graph(), id:str, vote_avg_threshold:float):
        LFcredits = tmdb_api_utils.get_movie_credits_for_person(id, vote_avg_threshold)

        for c in LFcredits:
            castMembers = tmdb_api_utils.get_movie_cast(str(c['id']), 3, [int(id)])

            for m in castMembers:
                graph.add_node(str(m['id']), m['name'])
                graph.add_edge(id, str(m['id']))
        return graph

    # graph = build_base_graph(graph, '2975', 8.0)
    # print(graph)

    def bulid(graph:Graph(), id:str, limit:int, vote_avg_threshold:float):
        exclude_ids = [int(id)]
        l = 0

        for times in range(2):
            if times == 0:
                nodes = graph.nodes
                new_add_nodes = nodes[1:]
                l = len(new_add_nodes)
                print('First iteration: ', nodes, new_add_nodes)
            else:
                nodes = graph.nodes
                print('here ', len(nodes), nodes)
                new_add_nodes = nodes[l+1:]
                l = len(new_add_nodes)
                print('Second iteration: ', nodes, new_add_nodes)

            for node in new_add_nodes:
                exclude_ids.append(int(node[0]))
                movies = tmdb_api_utils.get_movie_credits_for_person(node[0],vote_avg_threshold)
                if not movies: continue
                for movie in movies:
                    castMembers = tmdb_api_utils.get_movie_cast(str(movie['id']), limit, exclude_ids)
                    if not castMembers: continue
                    for c in castMembers:
                        graph.add_node(str(c['id']), c['name'])
                        graph.add_edge(node[0], str(c['id']))
        return graph

    graph = bulid(build_base_graph(graph, '2975', 8.0), '2975', 3, 8.0)


    graph.write_edges_file()
    graph.write_nodes_file()

    # If you have already built & written out your graph, you could read in your nodes & edges files
    # to perform testing on your graph.
    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")
