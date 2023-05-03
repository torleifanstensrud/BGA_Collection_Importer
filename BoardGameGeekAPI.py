import requests
import time
import xml.etree.ElementTree as ET

class BoardGameGeekAPI:
    API_URL = "https://www.boardgamegeek.com/xmlapi2/"

    def __init__(self, bgg_username): 
        self.username = bgg_username
        
    def query_bgg(self, type_string, params):
        query_result = requests.get(self.API_URL + type_string, params=params)
        
        while query_result.status_code == 202:
            timeout = 5
            print("Code 202: Board Game Geek has queued your request. Trying again in " + str(timeout) + " seconds.")
            time.sleep(timeout)
            query_result = requests.get(self.API_URL + type_string, params=params)
                    
        while query_result.status_code == 429:
            timeout = 5
            print("Code 429: Board Game Geek asks you too slow down. Trying again in " + str(timeout) + " seconds.")
            time.sleep(timeout)
            query_result = requests.get(self.API_URL + type_string, params=params)
                    
        return query_result

    def query_bgg_collection(self):
        print('Querying collection from BoardGameGeek for user ' + self.username)
        params_base = {
            'username': self.username,
            'subtype': 'boardgame',
            'excludesubtype': 'boardgameexpansion',
            'own': 1,
            'stats': 1,
        }   
    
        query_result = self.query_bgg('collection', params_base)
                    
        base_game_items = ET.fromstring(query_result.text)
        
        params_expansion = {
            'username': self.username,
            'subtype': 'boardgameexpansion',
            'own': 1,
            'stats': 1,
        }

        query_result = self.query_bgg('collection', params_expansion)
                    
        expansion_items = ET.fromstring(query_result.text)
        
        xml_collection = {
                'base_game_items' : base_game_items,
                'expansion_items' : expansion_items,
        }
        
        return xml_collection
    
    def query_bgg_id(self, game_id):
        param = {
                'id': game_id,
                'stats': 1,
                 }   
        query_result = self.query_bgg('thing', param)
        print('\t' + game_id + ': Returned status code ' + str(query_result.status_code))
        return query_result
        
    def query_bgg_ids(self, game_ids):
        print('Querying base games:')
        xml_base_games = dict()
        for game_id in game_ids['base_game_ids']:  
            query_result = self.query_bgg_id(game_id)
            base_game_item = ET.fromstring(query_result.text)
            xml_base_games[game_id] = base_game_item
        
        print('Querying expansions:')
        xml_expansions = dict()
        for game_id in game_ids['expansion_ids']:
            query_result = self.query_bgg_id(game_id)
            expansion_item = ET.fromstring(query_result.text)
            xml_expansions[game_id] = expansion_item
        
        xml_games = {
            'xml_base_games' : xml_base_games,
            'xml_expansions' : xml_expansions,
        }
        return xml_games
    